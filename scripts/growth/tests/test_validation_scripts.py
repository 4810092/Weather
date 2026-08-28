from __future__ import annotations

import base64
import copy
import gzip
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from scripts.build_store_creatives import (
    generated_output_paths,
    generated_source_paths,
    validate_output_sha256_contract,
    validate_source_sha256_contract,
)
from scripts.check_dashboard_report import (
    BACKING_JSON_PATHS,
    EXPECTED_SOURCE_PATHS,
    DashboardConsistencyError,
    verify_dashboard_report,
    verify_dashboard_sources,
)
from scripts.check_store_assets import (
    inspect_image,
    load_creative_manifest,
    validate_store_image,
)
from scripts.check_store_metadata import validate_upload_artifacts


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
    def upload_manifest(self) -> dict:
        return json.loads(
            (ROOT / "store/upload-manifest-1.1.0.json").read_text(encoding="utf-8")
        )

    def test_store_inspection_decodes_pixels_and_rejects_truncation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            valid = Path(directory) / "valid.png"
            corrupt = Path(directory) / "corrupt.png"
            Image.new("RGB", (8, 6), "blue").save(valid, format="PNG")
            self.assertEqual(inspect_image(valid), ((8, 6), "PNG", "RGB", False))
            corrupt.write_bytes(valid.read_bytes()[:-20])
            with self.assertRaisesRegex(ValueError, "decode/verification failed"):
                inspect_image(corrupt)

    def test_opaque_rgba_store_screenshot_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            screenshot = Path(directory) / "opaque-rgba.png"
            Image.new("RGBA", (8, 6), (12, 34, 56, 255)).save(screenshot, format="PNG")
            relative = "store/screenshots/google-play/phone-en/opaque-rgba.png"
            self.assertEqual(
                validate_store_image(relative, screenshot, (8, 6), "PNG"),
                [f"{relative}: alpha channel is not allowed"],
            )

    def test_google_play_icon_requires_32_bit_alpha_and_size_limit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rgb = root / "rgb.png"
            rgba = root / "rgba.png"
            Image.new("RGB", (512, 512), "blue").save(rgb, format="PNG")
            Image.new("RGBA", (512, 512), (12, 34, 56, 255)).save(rgba, format="PNG")
            relative = "store/assets/google-play/icon-512.png"
            self.assertIn(
                f"{relative}: must be a 32-bit RGBA image with alpha",
                validate_store_image(
                    relative,
                    rgb,
                    (512, 512),
                    "PNG",
                    require_alpha=True,
                    max_bytes=1024 * 1024,
                ),
            )
            self.assertEqual(
                validate_store_image(
                    relative,
                    rgba,
                    (512, 512),
                    "PNG",
                    require_alpha=True,
                    max_bytes=1024 * 1024,
                ),
                [],
            )
            self.assertTrue(
                any(
                    "exceeds 1-byte store limit" in failure
                    for failure in validate_store_image(
                        relative,
                        rgba,
                        (512, 512),
                        "PNG",
                        require_alpha=True,
                        max_bytes=1,
                    )
                )
            )

    def test_creative_manifest_uses_locale_matched_watch_sources(self) -> None:
        manifest, failures = load_creative_manifest()
        self.assertEqual(failures, [])
        self.assertEqual(
            manifest["platforms"]["google-play"]["legacy_feature_graphic_locale"],
            "en-US",
        )
        for locale, payload in manifest["locales"].items():
            expected_segment = "en" if locale == "en-US" else locale
            self.assertTrue(
                all(
                    expected_segment in source
                    for source in payload["watch_sources"].values()
                )
            )

        output_paths = generated_output_paths(manifest)
        self.assertEqual(len(output_paths), 40)
        self.assertEqual(len(set(output_paths)), 40)
        self.assertEqual(set(manifest["output_sha256"]), set(output_paths))
        self.assertEqual(validate_output_sha256_contract(manifest, root=ROOT), [])
        source_paths = generated_source_paths(manifest)
        self.assertEqual(len(source_paths), 22)
        self.assertEqual(set(manifest["source_sha256"]), set(source_paths))
        self.assertEqual(validate_source_sha256_contract(manifest, root=ROOT), [])

    def test_creative_output_contract_rejects_path_set_mutations(self) -> None:
        manifest, failures = load_creative_manifest()
        self.assertEqual(failures, [])
        relative = next(iter(manifest["output_sha256"]))

        missing = copy.deepcopy(manifest)
        missing["output_sha256"].pop(relative)
        self.assertIn(
            f"creative output SHA-256 contract is missing: {relative}",
            validate_output_sha256_contract(missing, root=ROOT, verify_files=False),
        )

        unexpected = copy.deepcopy(manifest)
        unexpected["output_sha256"]["store/creatives/unexpected.png"] = "0" * 64
        self.assertIn(
            "creative output SHA-256 contract has unexpected paths: "
            "store/creatives/unexpected.png",
            validate_output_sha256_contract(unexpected, root=ROOT, verify_files=False),
        )

    def test_creative_output_contract_rejects_byte_mutation(self) -> None:
        manifest = {
            "platforms": {
                "app-store": {"output_dir": "generated/app-store"},
                "google-play": {
                    "output_dir": "generated/google-play",
                    "feature_graphics": {
                        "en-US": {"output": "generated/feature-en.jpg"}
                    },
                    "legacy_feature_graphic": "generated/feature-legacy.jpg",
                },
            },
            "locales": {"en-US": {}},
            "stories": [{"filename": "01.png"}],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in generated_output_paths(manifest):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(f"asset:{relative}".encode())
            manifest["output_sha256"] = {
                relative: hashlib.sha256((root / relative).read_bytes()).hexdigest()
                for relative in generated_output_paths(manifest)
            }
            self.assertEqual(validate_output_sha256_contract(manifest, root=root), [])

            mutated = generated_output_paths(manifest)[0]
            (root / mutated).write_bytes(b"replacement-with-different-bytes")
            self.assertTrue(
                any(
                    failure.startswith(f"{mutated}: SHA-256 drift")
                    for failure in validate_output_sha256_contract(manifest, root=root)
                )
            )

    def test_creative_source_contract_rejects_byte_mutation(self) -> None:
        manifest = {
            "platforms": {
                "app-store": {"phone_source": "sources/apple-{source_locale}.png"},
                "google-play": {
                    "phone_source": "sources/google-{source_locale}-{source_name}",
                    "feature_graphic_source": "sources/icon.png",
                },
            },
            "locales": {
                "en-US": {
                    "source_locale": "en",
                    "watch_sources": {
                        "app-store": "sources/apple-watch.png",
                        "google-play": "sources/google-watch.png",
                    },
                }
            },
            "stories": [{"google_source_name": "screen.png"}],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in generated_source_paths(manifest):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(f"source:{relative}".encode())
            manifest["source_sha256"] = {
                relative: hashlib.sha256((root / relative).read_bytes()).hexdigest()
                for relative in generated_source_paths(manifest)
            }
            self.assertEqual(validate_source_sha256_contract(manifest, root=root), [])

            mutated = generated_source_paths(manifest)[0]
            (root / mutated).write_bytes(b"replacement-source")
            self.assertTrue(
                any(
                    failure.startswith(f"{mutated}: source SHA-256 drift")
                    for failure in validate_source_sha256_contract(manifest, root=root)
                )
            )

    def test_upload_artifacts_match_source_and_preserve_fail_closed_state(self) -> None:
        failures: list[str] = []
        validate_upload_artifacts(self.upload_manifest(), "1.1.0", failures)
        self.assertEqual(failures, [])

    def test_blocked_upload_artifact_cannot_claim_current_evidence(self) -> None:
        invalid_values = {
            "sha256": "0" * 64,
            "signing_evidence": (
                "growth/quality/android-release-artifacts-2026-08-28.md"
            ),
            "physical_qa_evidence": (
                "growth/quality/android-physical-smoke-2026-08-28.md"
            ),
        }
        for field, value in invalid_values.items():
            with self.subTest(field=field):
                manifest = copy.deepcopy(self.upload_manifest())
                manifest["artifacts"]["android_phone"][field] = value
                failures: list[str] = []
                validate_upload_artifacts(manifest, "1.1.0", failures)
                self.assertIn(
                    "upload manifest artifact android_phone: blocked artifact "
                    f"must keep {field} null",
                    failures,
                )

    def test_upload_artifact_identity_must_match_source(self) -> None:
        manifest = copy.deepcopy(self.upload_manifest())
        manifest["artifacts"]["apple"]["build"] = 5
        failures: list[str] = []
        validate_upload_artifacts(manifest, "1.1.0", failures)
        self.assertTrue(
            any("declared build 5 differs from source 6" in item for item in failures)
        )

    def test_featuring_operational_blockers_use_canonical_gate_ids(self) -> None:
        featuring = json.loads(
            (ROOT / "growth/featuring/manifest.json").read_text(encoding="utf-8")
        )
        gates = json.loads(
            (ROOT / "growth/quality/gates.json").read_text(encoding="utf-8")
        )["gates"]
        operational = {
            blocker["id"]: blocker
            for blocker in featuring["blockers"]
            if blocker["blocker_type"] == "operational_gate"
        }
        expected = {
            gate_id: gate
            for gate_id, gate in gates.items()
            if gate["status"] != "pass"
        }
        self.assertEqual(set(operational), set(expected))
        for gate_id, gate in expected.items():
            self.assertEqual(operational[gate_id]["status"], gate["status"])
            self.assertEqual(
                operational[gate_id]["evidence"], "growth/quality/gates.json"
            )
        deliverable_ids = {
            blocker["id"]
            for blocker in featuring["blockers"]
            if blocker["blocker_type"] == "deliverable"
        }
        self.assertTrue(
            all(identifier.startswith("deliverable.") for identifier in deliverable_ids)
        )

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

    def test_dashboard_cited_inputs_are_mutation_checked(self) -> None:
        artifact = json.loads(
            (ROOT / "growth/dashboard/artifact.json").read_text(encoding="utf-8")
        )
        source_paths = set(EXPECTED_SOURCE_PATHS.values()) | set(
            BACKING_JSON_PATHS.values()
        )
        json_mutations = (
            (
                BACKING_JSON_PATHS["baseline"],
                ("platforms", "apple", "metrics", "reported_impressions"),
                207,
            ),
            (
                BACKING_JSON_PATHS["rank"],
                ("surfaces", "apple", "search", "weather", "target_rank"),
                80,
            ),
            (
                BACKING_JSON_PATHS["evaluation"],
                ("top10_goal", "current_streak_days"),
                1,
            ),
            (
                BACKING_JSON_PATHS["evaluation"],
                ("guardrails", "metric_guardrails", 0, "status"),
                "pass",
            ),
            (
                BACKING_JSON_PATHS["framework"],
                (
                    "primary_goal",
                    "daily_requirements",
                    "apple_weather_chart_rank_lte",
                ),
                9,
            ),
            (
                BACKING_JSON_PATHS["gates"],
                ("gates", "ios_crash_gate", "reason"),
                "synthetic stale gate evidence",
            ),
        )
        for relative, field_path, replacement in json_mutations:
            with self.subTest(source=relative), tempfile.TemporaryDirectory() as directory:
                temporary_root = Path(directory)
                for source in source_paths:
                    destination = temporary_root / source
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(ROOT / source, destination)
                verify_dashboard_sources(artifact, repo_root=temporary_root)
                source_file = temporary_root / relative
                payload = json.loads(source_file.read_text(encoding="utf-8"))
                target = payload
                for field in field_path[:-1]:
                    target = target[field]
                target[field_path[-1]] = replacement
                source_file.write_text(json.dumps(payload), encoding="utf-8")
                with self.assertRaises(DashboardConsistencyError):
                    verify_dashboard_sources(artifact, repo_root=temporary_root)

        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            for source in source_paths:
                destination = temporary_root / source
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / source, destination)
            sql_path = temporary_root / EXPECTED_SOURCE_PATHS["gate_snapshot"]
            sql_path.write_text(
                sql_path.read_text(encoding="utf-8") + "\nSELECT 1;\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(DashboardConsistencyError, "SQL differs"):
                verify_dashboard_sources(artifact, repo_root=temporary_root)

    def test_ci_runs_growth_tests_compileall_and_dashboard_check(self) -> None:
        ci = (ROOT / ".github/workflows/ci.yml").read_text()
        self.assertIn("python3 -m compileall -q scripts", ci)
        self.assertIn("python3 -m unittest discover -s scripts/growth/tests", ci)
        self.assertIn("python3 scripts/check_dashboard_report.py", ci)
        self.assertIn("Pillow==12.2.0", ci)
        self.assertIn("command -v ffprobe", ci)
        self.assertIn("command -v ffmpeg", ci)
        self.assertIn(":app:testDebugUnitTest", ci)
        self.assertIn("./gradlew :shared:iosSimulatorArm64Test", ci)
        self.assertIn("shared/build/test-results/iosSimulatorArm64Test", ci)
        self.assertIn("shared/build/reports/tests/iosSimulatorArm64Test", ci)

        build_site = (ROOT / "scripts/build_site.py").read_text()
        self.assertIn("verify_dashboard_report(artifact, source)", build_site)

        pages = (ROOT / ".github/workflows/pages.yml").read_text()
        for trigger_path in (
            '"growth/baseline/**"',
            '"growth/data/public-rank/**"',
            '"growth/kpi-framework.json"',
            '"growth/reports/**"',
        ):
            self.assertIn(trigger_path, pages)


if __name__ == "__main__":
    unittest.main()
