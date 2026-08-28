from __future__ import annotations

import base64
import gzip
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from scripts.check_dashboard_report import (
    DashboardConsistencyError,
    verify_dashboard_report,
)
from scripts.check_store_assets import inspect_image


ROOT = Path(__file__).resolve().parents[3]


def portable_report(payload: dict) -> str:
    encoded = base64.b64encode(
        gzip.compress(
            json.dumps(payload, separators=(",", ":")).encode("utf-8"),
            mtime=0,
        )
    ).decode("ascii")
    return (
        "<html><body><template "
        'id="data-analytics-portable-artifact-payload-source" '
        'data-compression="gzip-base64">'
        f"{encoded}</template></body></html>"
    )


class ValidationScriptsTest(unittest.TestCase):
    def test_store_inspection_decodes_pixels_and_rejects_truncation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            valid = Path(directory) / "valid.png"
            corrupt = Path(directory) / "corrupt.png"
            Image.new("RGB", (8, 6), "blue").save(valid, format="PNG")
            self.assertEqual(inspect_image(valid), ((8, 6), "PNG", False))
            corrupt.write_bytes(valid.read_bytes()[:-20])
            with self.assertRaisesRegex(ValueError, "decode/verification failed"):
                inspect_image(corrupt)

    def test_dashboard_report_must_embed_exact_canonical_artifact(self) -> None:
        artifact = {
            "surface": "dashboard",
            "manifest": {"generatedAt": "2026-08-28T00:00:00Z"},
            "snapshot": {"status": "partial"},
            "sources": [],
        }
        embedded = {"ok": True, "widget_type": "artifact", **artifact}
        with tempfile.TemporaryDirectory() as directory:
            artifact_path = Path(directory) / "artifact.json"
            report_path = Path(directory) / "report.html"
            artifact_path.write_text(json.dumps(artifact))
            report_path.write_text(portable_report(embedded))
            verify_dashboard_report(artifact_path, report_path)

            artifact["snapshot"]["status"] = "complete"
            artifact_path.write_text(json.dumps(artifact))
            with self.assertRaisesRegex(
                DashboardConsistencyError, "does not match artifact.json"
            ):
                verify_dashboard_report(artifact_path, report_path)

    def test_ci_runs_growth_tests_compileall_and_dashboard_check(self) -> None:
        ci = (ROOT / ".github/workflows/ci.yml").read_text()
        self.assertIn("python3 -m compileall -q scripts", ci)
        self.assertIn("python3 -m unittest discover -s scripts/growth/tests", ci)
        self.assertIn("python3 scripts/check_dashboard_report.py", ci)
        self.assertIn("Pillow==12.2.0", ci)

        build_site = (ROOT / "scripts/build_site.py").read_text()
        self.assertIn("verify_dashboard_report(artifact, source)", build_site)


if __name__ == "__main__":
    unittest.main()
