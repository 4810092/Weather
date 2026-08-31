from __future__ import annotations

import base64
import gzip
import json
import stat
import tempfile
import unittest
from pathlib import Path

from scripts.growth.sync_dashboard_report_payload import (
    DashboardPayloadSyncError,
    FALLBACK_ID,
    PAYLOAD_TEMPLATE_ID,
    _payload_template,
    replace_embedded_payload,
    replace_static_fallback,
    sync_dashboard_report_payload,
)


def _encoded(payload: object) -> str:
    serialized = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(gzip.compress(serialized, mtime=0)).decode("ascii")


def _report(
    payload: object | None = None,
    *,
    compression: str = "gzip-base64",
    opening_tag: str | None = None,
    closing_tag: str = "</template>",
) -> str:
    content = _encoded({"previous": True} if payload is None else payload)
    opening = opening_tag or (
        f'<template id="{PAYLOAD_TEMPLATE_ID}" '
        f'data-compression="{compression}">'
    )
    return (
        "<!doctype html>\n<html><body>\n"
        f"{opening}\n{content}\n{closing_tag}\n"
        '<template id="data-analytics-portable-reader-runtime-source" '
        'data-compression="gzip-base64">runtime-bytes</template>\n'
        f'<main id="{FALLBACK_ID}" class="portable-fallback">'
        "<p>legacy no-JS fallback</p></main>\n"
        "</body></html>\n"
    )


class SyncDashboardReportPayloadTest(unittest.TestCase):
    def test_sync_is_deterministic_and_refreshes_payload_and_fallback(self) -> None:
        artifact = {
            "surface": "dashboard",
            "manifest": {
                "title": "Nimbo — O‘zbekiston",
                "generatedAt": "2026-08-31T18:00:00Z",
                "cards": [],
                "charts": [],
                "tables": [],
                "blocks": [
                    {
                        "id": "current_status",
                        "type": "markdown",
                        "body": "## Current status\n\nBuild 6 is **VALID**.",
                    }
                ],
            },
            "snapshot": {
                "status": "blocked",
                "accessIssues": [],
                "datasets": {"rows": [{"value": 1}]},
            },
            "sources": [],
        }
        original = _report()

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact_path = root / "artifact.json"
            report_path = root / "report.html"
            artifact_path.write_text(
                json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            report_path.write_text(original, encoding="utf-8")
            report_path.chmod(0o640)

            self.assertTrue(sync_dashboard_report_payload(artifact_path, report_path))
            synchronized = report_path.read_text(encoding="utf-8")
            synchronized_target = _payload_template(synchronized)
            self.assertIsNotNone(synchronized_target.content_end)

            self.assertNotIn("legacy no-JS fallback", synchronized)
            self.assertIn('data-canonical-generated-at="2026-08-31T18:00:00Z"', synchronized)
            self.assertIn("Nimbo — O‘zbekiston", synchronized)
            self.assertIn("Build 6 is <strong>VALID</strong>.", synchronized)
            self.assertEqual(stat.S_IMODE(report_path.stat().st_mode), 0o640)

            encoded = "".join(
                synchronized[
                    synchronized_target.content_start : synchronized_target.content_end
                ].split()
            )
            compressed = base64.b64decode(encoded, validate=True)
            self.assertEqual(compressed[4:8], b"\x00\x00\x00\x00")
            self.assertEqual(compressed[9], 255)
            self.assertEqual(json.loads(gzip.decompress(compressed)), artifact)

            first_bytes = report_path.read_bytes()
            self.assertFalse(sync_dashboard_report_payload(artifact_path, report_path))
            self.assertEqual(report_path.read_bytes(), first_bytes)

    def test_missing_static_fallback_fails_closed(self) -> None:
        artifact = {
            "manifest": {
                "title": "Nimbo",
                "generatedAt": "2026-08-31T18:00:00Z",
                "cards": [],
                "charts": [],
                "tables": [],
                "blocks": [],
            },
            "snapshot": {"status": "blocked", "accessIssues": [], "datasets": {}},
            "sources": [],
        }
        with self.assertRaisesRegex(DashboardPayloadSyncError, "exactly one.*main"):
            replace_static_fallback("<html><body></body></html>", artifact)

    def test_missing_payload_template_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            DashboardPayloadSyncError, "exactly one.*template"
        ):
            replace_embedded_payload("<html><body></body></html>", {"new": True})

    def test_multiple_payload_templates_fail_closed(self) -> None:
        report = _report() + _report()
        with self.assertRaisesRegex(
            DashboardPayloadSyncError, "exactly one.*template"
        ):
            replace_embedded_payload(report, {"new": True})

    def test_wrong_compression_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            DashboardPayloadSyncError, "data-compression=gzip-base64"
        ):
            replace_embedded_payload(
                _report(compression="base64"), {"new": True}
            )

    def test_unclosed_payload_template_fails_closed(self) -> None:
        report = (
            f'<template id="{PAYLOAD_TEMPLATE_ID}" '
            'data-compression="gzip-base64">\n'
            f"{_encoded({'previous': True})}\n"
        )
        with self.assertRaisesRegex(DashboardPayloadSyncError, "not closed"):
            replace_embedded_payload(report, {"new": True})

    def test_self_closing_payload_template_fails_closed(self) -> None:
        opening = (
            f'<template id="{PAYLOAD_TEMPLATE_ID}" '
            'data-compression="gzip-base64"/>'
        )
        with self.assertRaisesRegex(DashboardPayloadSyncError, "self-closing"):
            replace_embedded_payload(
                _report(opening_tag=opening, closing_tag=""), {"new": True}
            )

    def test_duplicate_compression_attribute_fails_closed(self) -> None:
        opening = (
            f'<template id="{PAYLOAD_TEMPLATE_ID}" '
            'data-compression="gzip-base64" data-compression="gzip-base64">'
        )
        with self.assertRaisesRegex(
            DashboardPayloadSyncError, "exactly one data-compression"
        ):
            replace_embedded_payload(
                _report(opening_tag=opening), {"new": True}
            )

    def test_nested_markup_fails_closed(self) -> None:
        report = _report().replace(
            _encoded({"previous": True}), "<span>not payload text</span>"
        )
        with self.assertRaisesRegex(DashboardPayloadSyncError, "nested markup"):
            replace_embedded_payload(report, {"new": True})

    def test_invalid_existing_payload_fails_closed(self) -> None:
        report = _report().replace(_encoded({"previous": True}), "not-base64!")
        with self.assertRaisesRegex(DashboardPayloadSyncError, "malformed"):
            replace_embedded_payload(report, {"new": True})

    def test_invalid_artifact_does_not_modify_report(self) -> None:
        original = _report()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact_path = root / "artifact.json"
            report_path = root / "report.html"
            artifact_path.write_text("[]", encoding="utf-8")
            report_path.write_text(original, encoding="utf-8")

            with self.assertRaisesRegex(DashboardPayloadSyncError, "JSON object"):
                sync_dashboard_report_payload(artifact_path, report_path)
            self.assertEqual(report_path.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
