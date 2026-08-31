#!/usr/bin/env python3
"""Synchronize the portable dashboard's embedded canonical artifact payload."""

from __future__ import annotations

import argparse
import base64
import binascii
from dataclasses import dataclass
import gzip
from html.parser import HTMLParser
import io
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import textwrap
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = REPO_ROOT / "growth/dashboard/artifact.json"
DEFAULT_REPORT = REPO_ROOT / "growth/dashboard/report.html"
PAYLOAD_TEMPLATE_ID = "data-analytics-portable-artifact-payload-source"
PAYLOAD_COMPRESSION = "gzip-base64"


class DashboardPayloadSyncError(ValueError):
    """The report cannot be safely synchronized with the canonical artifact."""


@dataclass
class _PayloadTemplate:
    content_start: int
    content_end: int | None
    compression: str | None
    malformed_reason: str | None = None


class _PayloadTemplateParser(HTMLParser):
    """Locate one payload template while retaining exact source offsets."""

    def __init__(self, source: str) -> None:
        super().__init__(convert_charrefs=False)
        self._line_offsets = self._build_line_offsets(source)
        self.target_count = 0
        self.target: _PayloadTemplate | None = None
        self._active = False

    @staticmethod
    def _build_line_offsets(source: str) -> list[int]:
        offsets = [0]
        for line in source.splitlines(keepends=True):
            offsets.append(offsets[-1] + len(line))
        return offsets

    def _offset(self) -> int:
        line, column = self.getpos()
        try:
            return self._line_offsets[line - 1] + column
        except IndexError as error:
            raise DashboardPayloadSyncError(
                "dashboard parser returned an invalid source position"
            ) from error

    @staticmethod
    def _values(
        attrs: list[tuple[str, str | None]], name: str
    ) -> list[str | None]:
        return [value for attribute, value in attrs if attribute == name]

    def _record_target(
        self,
        attrs: list[tuple[str, str | None]],
        *,
        self_closing: bool,
    ) -> None:
        identifier_values = self._values(attrs, "id")
        if PAYLOAD_TEMPLATE_ID not in identifier_values:
            if self._active:
                self._mark_malformed("payload template contains nested markup")
            return

        self.target_count += 1
        if self.target_count > 1:
            self._mark_malformed("dashboard contains multiple payload templates")
            return

        raw_start = self.get_starttag_text()
        if raw_start is None:
            raise DashboardPayloadSyncError(
                "dashboard payload template has no readable opening tag"
            )
        compression_values = self._values(attrs, "data-compression")
        malformed_reason = None
        if len(identifier_values) != 1:
            malformed_reason = "payload template has duplicate id attributes"
        elif len(compression_values) != 1:
            malformed_reason = (
                "payload template must have exactly one data-compression attribute"
            )
        elif self_closing:
            malformed_reason = "payload template must not be self-closing"

        start = self._offset() + len(raw_start)
        self.target = _PayloadTemplate(
            content_start=start,
            content_end=start if self_closing else None,
            compression=(compression_values[0] if compression_values else None),
            malformed_reason=malformed_reason,
        )
        self._active = not self_closing

    def _mark_malformed(self, reason: str) -> None:
        if self.target is not None and self.target.malformed_reason is None:
            self.target.malformed_reason = reason

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag == "template":
            self._record_target(attrs, self_closing=False)
        elif self._active:
            self._mark_malformed("payload template contains nested markup")

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag == "template":
            self._record_target(attrs, self_closing=True)
        elif self._active:
            self._mark_malformed("payload template contains nested markup")

    def handle_endtag(self, tag: str) -> None:
        if not self._active:
            return
        if tag == "template":
            if self.target is not None:
                self.target.content_end = self._offset()
            self._active = False
        else:
            self._mark_malformed("payload template contains nested markup")

    def handle_comment(self, data: str) -> None:
        if self._active:
            self._mark_malformed("payload template contains a comment")

    def handle_decl(self, decl: str) -> None:
        if self._active:
            self._mark_malformed("payload template contains a declaration")

    def handle_pi(self, data: str) -> None:
        if self._active:
            self._mark_malformed("payload template contains a processing instruction")

    def unknown_decl(self, data: str) -> None:
        if self._active:
            self._mark_malformed("payload template contains an unknown declaration")


def _read_utf8(path: Path, label: str) -> str:
    try:
        return path.read_bytes().decode("utf-8")
    except (OSError, UnicodeError) as error:
        raise DashboardPayloadSyncError(
            f"cannot read {label} {path}: {error}"
        ) from error


def _load_artifact(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(_read_utf8(path, "dashboard artifact"))
    except json.JSONDecodeError as error:
        raise DashboardPayloadSyncError(
            f"dashboard artifact is not valid JSON: {error}"
        ) from error
    if not isinstance(payload, dict):
        raise DashboardPayloadSyncError("dashboard artifact must be a JSON object")
    return payload


def _payload_template(report: str) -> _PayloadTemplate:
    parser = _PayloadTemplateParser(report)
    try:
        parser.feed(report)
        parser.close()
    except DashboardPayloadSyncError:
        raise
    except Exception as error:
        raise DashboardPayloadSyncError(
            f"dashboard report cannot be parsed: {error}"
        ) from error
    if parser.target_count != 1 or parser.target is None:
        raise DashboardPayloadSyncError(
            "dashboard report must contain exactly one "
            f"{PAYLOAD_TEMPLATE_ID!r} template"
        )
    target = parser.target
    if target.malformed_reason is not None:
        raise DashboardPayloadSyncError(target.malformed_reason)
    if target.content_end is None:
        raise DashboardPayloadSyncError("dashboard payload template is not closed")
    if target.compression != PAYLOAD_COMPRESSION:
        raise DashboardPayloadSyncError(
            f"dashboard payload must declare data-compression={PAYLOAD_COMPRESSION}"
        )
    _validate_existing_payload(report[target.content_start : target.content_end])
    return target


def _validate_existing_payload(content: str) -> None:
    encoded = "".join(content.split())
    if not encoded:
        raise DashboardPayloadSyncError("dashboard payload template is empty")
    try:
        compressed = base64.b64decode(encoded, validate=True)
        decoded = gzip.decompress(compressed).decode("utf-8")
        payload = json.loads(decoded)
    except (
        binascii.Error,
        gzip.BadGzipFile,
        OSError,
        UnicodeError,
        json.JSONDecodeError,
    ) as error:
        raise DashboardPayloadSyncError(
            f"existing dashboard payload is malformed: {error}"
        ) from error
    if not isinstance(payload, dict):
        raise DashboardPayloadSyncError(
            "existing dashboard payload must decode to a JSON object"
        )


def encode_artifact_payload(artifact: dict[str, Any]) -> str:
    """Return a deterministic, wrapped gzip-base64 representation."""
    serialized = json.dumps(
        artifact,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    compressed_buffer = io.BytesIO()
    with gzip.GzipFile(
        filename="",
        mode="wb",
        compresslevel=9,
        fileobj=compressed_buffer,
        mtime=0,
    ) as archive:
        archive.write(serialized)
    compressed = compressed_buffer.getvalue()
    encoded = base64.b64encode(compressed).decode("ascii")
    return "\n".join(textwrap.wrap(encoded, width=76))


def replace_embedded_payload(report: str, artifact: dict[str, Any]) -> str:
    """Replace only the validated canonical payload template's text content."""
    target = _payload_template(report)
    assert target.content_end is not None
    encoded = encode_artifact_payload(artifact)
    replacement = f"\n{encoded}\n"
    return report[: target.content_start] + replacement + report[target.content_end :]


def _atomic_write_utf8(path: Path, content: str) -> None:
    try:
        mode = stat.S_IMODE(path.stat().st_mode)
    except OSError as error:
        raise DashboardPayloadSyncError(
            f"cannot inspect dashboard report {path}: {error}"
        ) from error

    temporary_path: Path | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.name}.",
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(descriptor, "wb") as output:
            output.write(content.encode("utf-8"))
            output.flush()
            os.fsync(output.fileno())
        os.chmod(temporary_path, mode)
        os.replace(temporary_path, path)
        temporary_path = None
    except (OSError, UnicodeError) as error:
        raise DashboardPayloadSyncError(
            f"cannot update dashboard report {path}: {error}"
        ) from error
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def sync_dashboard_report_payload(artifact_path: Path, report_path: Path) -> bool:
    """Synchronize the report payload atomically; return whether bytes changed."""
    artifact = _load_artifact(artifact_path)
    report = _read_utf8(report_path, "dashboard report")
    synchronized = replace_embedded_payload(report, artifact)
    if synchronized == report:
        return False
    _atomic_write_utf8(report_path, synchronized)
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> int:
    arguments = parse_args()
    try:
        changed = sync_dashboard_report_payload(arguments.artifact, arguments.report)
    except DashboardPayloadSyncError as error:
        print(f"Dashboard payload sync failed: {error}", file=sys.stderr)
        return 1
    result = "updated" if changed else "already current"
    print(f"Dashboard embedded artifact payload {result}: {arguments.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
