#!/usr/bin/env python3
"""Verify that the portable growth dashboard embeds the canonical artifact."""

from __future__ import annotations

import argparse
import base64
import binascii
import gzip
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = REPO_ROOT / "growth/dashboard/artifact.json"
DEFAULT_REPORT = REPO_ROOT / "growth/dashboard/report.html"
PAYLOAD_TEMPLATE_ID = "data-analytics-portable-artifact-payload-source"
CANONICAL_KEYS = ("surface", "manifest", "snapshot", "sources")


class DashboardConsistencyError(ValueError):
    """The rendered report cannot be proven to represent its JSON source."""


class _PayloadParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.active = False
        self.count = 0
        self.compression: str | None = None
        self.parts: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        if tag == "template" and attributes.get("id") == PAYLOAD_TEMPLATE_ID:
            self.active = True
            self.count += 1
            self.compression = attributes.get("data-compression")

    def handle_endtag(self, tag: str) -> None:
        if tag == "template" and self.active:
            self.active = False

    def handle_data(self, data: str) -> None:
        if self.active:
            self.parts.append(data)


def embedded_artifact_payload(report: Path) -> dict[str, Any]:
    parser = _PayloadParser()
    try:
        parser.feed(report.read_text(encoding="utf-8"))
        parser.close()
    except (OSError, UnicodeError) as error:
        raise DashboardConsistencyError(f"cannot read dashboard report: {error}") from error
    if parser.count != 1:
        raise DashboardConsistencyError(
            f"dashboard report must contain exactly one {PAYLOAD_TEMPLATE_ID!r} template"
        )
    if parser.compression != "gzip-base64":
        raise DashboardConsistencyError(
            "dashboard payload must declare data-compression=gzip-base64"
        )
    encoded = "".join("".join(parser.parts).split())
    try:
        compressed = base64.b64decode(encoded, validate=True)
        decoded = gzip.decompress(compressed).decode("utf-8")
        payload = json.loads(decoded)
    except (binascii.Error, gzip.BadGzipFile, OSError, UnicodeError, json.JSONDecodeError) as error:
        raise DashboardConsistencyError(
            f"dashboard payload cannot be decoded and parsed: {error}"
        ) from error
    if not isinstance(payload, dict):
        raise DashboardConsistencyError("dashboard payload must be a JSON object")
    return payload


def verify_dashboard_report(artifact: Path, report: Path) -> None:
    try:
        canonical = json.loads(artifact.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise DashboardConsistencyError(f"cannot read dashboard artifact: {error}") from error
    if not isinstance(canonical, dict):
        raise DashboardConsistencyError("dashboard artifact must be a JSON object")
    embedded = embedded_artifact_payload(report)
    missing = [key for key in CANONICAL_KEYS if key not in canonical or key not in embedded]
    if missing:
        raise DashboardConsistencyError(
            f"dashboard artifact/report missing canonical sections: {', '.join(missing)}"
        )
    for key in CANONICAL_KEYS:
        if embedded[key] != canonical[key]:
            artifact_generated = canonical.get("manifest", {}).get("generatedAt")
            report_generated = embedded.get("manifest", {}).get("generatedAt")
            raise DashboardConsistencyError(
                f"dashboard report section {key!r} does not match artifact.json "
                f"(artifact generatedAt={artifact_generated!r}, "
                f"report generatedAt={report_generated!r}); regenerate report.html"
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> int:
    arguments = parse_args()
    try:
        verify_dashboard_report(arguments.artifact, arguments.report)
    except DashboardConsistencyError as error:
        print(f"Dashboard consistency check failed: {error}", file=sys.stderr)
        return 1
    print("Dashboard consistency check passed: report.html matches artifact.json.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
