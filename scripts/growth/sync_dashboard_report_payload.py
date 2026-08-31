#!/usr/bin/env python3
"""Synchronize the portable dashboard payload and semantic static fallback."""

from __future__ import annotations

import argparse
import base64
import binascii
from dataclasses import dataclass
import gzip
from html import escape
from html.parser import HTMLParser
import io
import json
import os
from pathlib import Path
import re
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
FALLBACK_ID = "data-analytics-portable-fallback"


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


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DashboardPayloadSyncError(f"dashboard artifact {label} must be an object")
    return value


def _array(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise DashboardPayloadSyncError(f"dashboard artifact {label} must be an array")
    return value


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _format_value(value: Any, value_format: str | None = None) -> str:
    if value_format == "percent" and isinstance(value, (int, float)):
        rendered = f"{value * 100:.2f}".rstrip("0").rstrip(".")
        return f"{rendered}%"
    if value_format == "number" and isinstance(value, float) and value.is_integer():
        return str(int(value))
    return _text(value)


def _inline_markdown(value: str) -> str:
    rendered = escape(value)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", rendered)


def _render_markdown(body: Any) -> str:
    if not isinstance(body, str):
        raise DashboardPayloadSyncError("dashboard markdown block body must be text")
    parts: list[str] = []
    for paragraph in (item.strip() for item in body.split("\n\n")):
        if not paragraph:
            continue
        if paragraph.startswith("## "):
            parts.append(f"<h2>{_inline_markdown(paragraph[3:])}</h2>")
        else:
            parts.append(f"<p>{_inline_markdown(paragraph)}</p>")
    return "".join(parts)


def _render_metric_strip(
    block: dict[str, Any],
    cards_by_id: dict[str, dict[str, Any]],
    datasets: dict[str, Any],
) -> str:
    articles: list[str] = []
    for card_id in _array(block.get("cardIds", []), "metric-strip cardIds"):
        card = cards_by_id.get(_text(card_id))
        if card is None:
            raise DashboardPayloadSyncError(f"dashboard card is missing: {card_id}")
        dataset_id = _text(card.get("dataset"))
        rows = _array(datasets.get(dataset_id), f"dataset {dataset_id}")
        row = _object(rows[0], f"dataset {dataset_id} first row") if rows else {}
        metrics = _array(card.get("metrics"), f"card {card_id} metrics")
        if not metrics:
            raise DashboardPayloadSyncError(f"dashboard card has no metrics: {card_id}")
        primary = _object(metrics[0], f"card {card_id} primary metric")
        value = _format_value(row.get(_text(primary.get("field"))), primary.get("format"))
        badges: list[str] = []
        for raw_metric in metrics[1:]:
            metric = _object(raw_metric, f"card {card_id} secondary metric")
            metric_value = _format_value(
                row.get(_text(metric.get("field"))), metric.get("format")
            )
            badges.append(
                '<span class="portable-metric-badge">'
                f'<span>{escape(_text(metric.get("label")))}</span> '
                f"<strong>{escape(metric_value)}</strong></span>"
            )
        articles.append(
            '<article class="portable-metric-card" '
            f'data-artifact-id="metric:{escape(_text(block.get("id")))}:{escape(_text(card_id))}" '
            'data-artifact-kind="card">'
            f'<p class="portable-metric-label">{escape(_text(primary.get("label")))}</p>'
            f'<p class="portable-metric-value">{escape(value)}</p>'
            f'<p class="portable-card-description">{escape(_text(card.get("description")))}</p>'
            f'<div class="portable-metric-badges">{"".join(badges)}</div>'
            "</article>"
        )
    return f'<section class="portable-metric-grid">{"".join(articles)}</section>'


def _render_table(
    title: str,
    subtitle: str,
    columns: list[dict[str, Any]],
    rows: list[Any],
) -> str:
    headers = "".join(
        f'<th scope="col">{escape(_text(column.get("label")))}</th>'
        for column in columns
    )
    rendered_rows: list[str] = []
    for raw_row in rows:
        row = _object(raw_row, f"table {title} row")
        rendered_rows.append(
            "<tr>"
            + "".join(
                f'<td>{escape(_text(row.get(_text(column.get("field")))))}</td>'
                for column in columns
            )
            + "</tr>"
        )
    return (
        '<section class="portable-content-card portable-table-card">'
        f'<header class="portable-visual-header"><h2>{escape(title)}</h2>'
        f"<p>{escape(subtitle)}</p></header>"
        '<div class="portable-table-scroll"><table>'
        f"<caption>{escape(title)}</caption><thead><tr>{headers}</tr></thead>"
        f"<tbody>{''.join(rendered_rows)}</tbody></table></div></section>"
    )


def _render_chart_as_table(
    chart: dict[str, Any], datasets: dict[str, Any]
) -> str:
    encodings = _object(chart.get("encodings"), f"chart {chart.get('id')} encodings")
    columns: list[dict[str, Any]] = []
    for channel in ("x", "color", "y"):
        encoding = encodings.get(channel)
        if isinstance(encoding, dict):
            columns.append(
                {
                    "field": encoding.get("field"),
                    "label": encoding.get("label") or encoding.get("field"),
                }
            )
    dataset_id = _text(chart.get("dataset"))
    rows = _array(datasets.get(dataset_id), f"dataset {dataset_id}")
    normalized: list[dict[str, Any]] = []
    for raw_row in rows:
        row = dict(_object(raw_row, f"chart {chart.get('id')} row"))
        for encoding in encodings.values():
            if isinstance(encoding, dict):
                field = _text(encoding.get("field"))
                row[field] = _format_value(row.get(field), encoding.get("format"))
        normalized.append(row)
    return _render_table(
        _text(chart.get("title")),
        _text(chart.get("subtitle")),
        columns,
        normalized,
    )


def render_static_fallback(artifact: dict[str, Any]) -> str:
    """Render a deterministic semantic fallback from the canonical artifact."""
    manifest = _object(artifact.get("manifest"), "manifest")
    snapshot = _object(artifact.get("snapshot"), "snapshot")
    datasets = _object(snapshot.get("datasets"), "snapshot datasets")
    title = _text(manifest.get("title"))
    generated_at = _text(manifest.get("generatedAt"))
    status = _text(snapshot.get("status"))
    cards_by_id = {
        _text(card.get("id")): card
        for card in (
            _object(item, "manifest card")
            for item in _array(manifest.get("cards", []), "manifest cards")
        )
    }
    tables_by_id = {
        _text(table.get("id")): table
        for table in (
            _object(item, "manifest table")
            for item in _array(manifest.get("tables", []), "manifest tables")
        )
    }
    charts_by_id = {
        _text(chart.get("id")): chart
        for chart in (
            _object(item, "manifest chart")
            for item in _array(manifest.get("charts", []), "manifest charts")
        )
    }

    issues = []
    for raw_issue in _array(snapshot.get("accessIssues", []), "snapshot accessIssues"):
        issue = _object(raw_issue, "snapshot access issue")
        issues.append(
            f'<li><strong>{escape(_text(issue.get("dataset")))}:</strong> '
            f'{escape(_text(issue.get("message")))}</li>'
        )
    notice = ""
    if issues:
        notice = (
            '<section class="portable-notice" aria-labelledby="portable-access-issues">'
            '<h2 id="portable-access-issues">Data access issues</h2>'
            f"<ul>{''.join(issues)}</ul></section>"
        )

    rendered_blocks: list[str] = []
    for raw_block in _array(manifest.get("blocks", []), "manifest blocks"):
        block = _object(raw_block, "manifest block")
        block_type = _text(block.get("type"))
        content = ""
        if block_type == "markdown":
            content = f'<section class="portable-markdown">{_render_markdown(block.get("body"))}</section>'
        elif block_type == "metric-strip":
            content = _render_metric_strip(block, cards_by_id, datasets)
        elif block_type == "table":
            table_id = _text(block.get("tableId"))
            table = tables_by_id.get(table_id)
            if table is None:
                raise DashboardPayloadSyncError(f"dashboard table is missing: {table_id}")
            columns = [
                _object(item, f"table {table_id} column")
                for item in _array(table.get("columns"), f"table {table_id} columns")
            ]
            dataset_id = _text(table.get("dataset"))
            content = _render_table(
                _text(table.get("title")),
                _text(table.get("subtitle")),
                columns,
                _array(datasets.get(dataset_id), f"dataset {dataset_id}"),
            )
        elif block_type == "chart":
            chart_id = _text(block.get("chartId"))
            chart = charts_by_id.get(chart_id)
            if chart is None:
                raise DashboardPayloadSyncError(f"dashboard chart is missing: {chart_id}")
            content = _render_chart_as_table(chart, datasets)
        else:
            raise DashboardPayloadSyncError(f"unsupported dashboard block type: {block_type}")
        rendered_blocks.append(
            '<div class="portable-block portable-layout-full" '
            f'data-artifact-block-id="{escape(_text(block.get("id")))}" '
            f'data-artifact-block-type="{escape(block_type)}">{content}</div>'
        )

    source_items: list[str] = []
    for raw_source in _array(artifact.get("sources", []), "sources"):
        source = _object(raw_source, "source")
        query = _object(source.get("query"), f"source {source.get('id')} query")
        source_items.append(
            f'<li><strong>{escape(_text(source.get("label")))}</strong>'
            f'<span class="portable-source-meta">{escape(_text(source.get("path")))} · '
            f'{escape(_text(query.get("executed_at")))}</span>'
            f'<p>{escape(_text(query.get("description")))}</p></li>'
        )
    sources = (
        '<section class="portable-sources" aria-labelledby="portable-sources-heading">'
        '<h2 id="portable-sources-heading">Sources</h2>'
        f"<ol>{''.join(source_items)}</ol></section>"
    )

    return (
        f'<main id="{FALLBACK_ID}" class="portable-fallback" '
        'data-portable-fallback="true" data-portable-surface="dashboard" '
        f'data-canonical-generated-at="{escape(generated_at)}">'
        '<header class="portable-page-header"><div class="portable-page-heading">'
        '<p class="portable-surface-label">Data Analytics dashboard</p>'
        f"<h1>{escape(title)}</h1></div><div class=\"portable-page-meta\">"
        f'<span class="portable-status">{escape(status)}</span>'
        f'<time datetime="{escape(generated_at)}">{escape(generated_at)}</time>'
        f"</div></header>{notice}<div class=\"portable-block-stack\">"
        f"{''.join(rendered_blocks)}</div>{sources}</main>"
    )


def replace_static_fallback(report: str, artifact: dict[str, Any]) -> str:
    """Replace exactly one semantic fallback with canonical rendered content."""
    opening = f'<main id="{FALLBACK_ID}"'
    if report.count(opening) != 1:
        raise DashboardPayloadSyncError(
            f"dashboard report must contain exactly one {FALLBACK_ID!r} main"
        )
    start = report.index(opening)
    end = report.find("</main>", start)
    if end < 0:
        raise DashboardPayloadSyncError("dashboard static fallback main is not closed")
    end += len("</main>")
    return report[:start] + render_static_fallback(artifact) + report[end:]


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
    """Synchronize report payload and fallback; return whether bytes changed."""
    artifact = _load_artifact(artifact_path)
    report = _read_utf8(report_path, "dashboard report")
    synchronized = replace_static_fallback(report, artifact)
    synchronized = replace_embedded_payload(synchronized, artifact)
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
    print(f"Dashboard payload and static fallback {result}: {arguments.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
