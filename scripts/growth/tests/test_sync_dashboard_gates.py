from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.growth import sync_dashboard_gates


ROOT = Path(__file__).resolve().parents[3]


class SyncDashboardGatesTest(unittest.TestCase):
    def test_sync_records_canonical_fail_closed_source_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            artifact_path = temporary_root / "artifact.json"
            gate_sql_path = temporary_root / "gate_snapshot.sql"
            for source, destination in (
                (ROOT / "growth/dashboard/artifact.json", artifact_path),
                (ROOT / "growth/dashboard/gate_snapshot.sql", gate_sql_path),
            ):
                shutil.copy2(source, destination)

            sync_dashboard_gates.sync(
                artifact_path,
                gate_sql_path,
                ROOT / "growth/quality/gates.json",
                ROOT / "growth/reports/evaluation-2026-09-01.json",
                "2026-08-30T12:34:56Z",
            )

            artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
            baseline_rows = {
                row["metric"]: row
                for row in artifact["snapshot"]["datasets"]["platform_baseline"]
                if row["platform"] == "Google Play"
            }
            apple_rows = {
                row["metric"]: row
                for row in artifact["snapshot"]["datasets"]["platform_baseline"]
                if row["platform"] == "App Store"
            }
            self.assertEqual(apple_rows["Ratings"]["value"], "1")
            self.assertEqual(
                apple_rows["Ratings"]["evidence_class"],
                "public_itunes_lookup_uz_2026-09-01",
            )
            self.assertEqual(baseline_rows["Installations"]["value"], "25")
            self.assertEqual(baseline_rows["First launches"]["value"], "18")
            self.assertEqual(
                baseline_rows["Monthly active devices"]["value"], "13"
            )
            self.assertEqual(
                baseline_rows["Installations"]["evidence_class"],
                "live_global_last_28_days_2026-08-31",
            )
            self.assertEqual(
                artifact["snapshot"]["datasets"]["headline_metrics"][0][
                    "first_launch_rate"
                ],
                0.72,
            )
            self.assertEqual(
                artifact["snapshot"]["datasets"]["headline_metrics"][0][
                    "apple_weather_rank"
                ],
                ">192",
            )
            rank_rows = {
                row["check"]: row
                for row in artifact["snapshot"]["datasets"]["rank_snapshot"]
            }
            self.assertEqual(
                rank_rows["App Store · Weather chart"]["observed_rank"], "66"
            )
            self.assertEqual(
                rank_rows["App Store search · weather"]["observed_rank"], ">192"
            )
            self.assertIn(
                "request 14",
                next(
                    block["body"]
                    for block in artifact["manifest"]["blocks"]
                    if block["id"] == "play_console_context"
                ),
            )
            self.assertIn(
                "still exposed the pre-review public title Nimbo",
                next(
                    block["body"]
                    for block in artifact["manifest"]["blocks"]
                    if block["id"] == "play_console_context"
                ),
            )
            self.assertIn(
                "public Apple UZ lookup on September 1 reports 1 rating at 5.0",
                next(
                    issue["message"]
                    for issue in artifact["snapshot"]["accessIssues"]
                    if issue["id"] == "raw_store_exports_missing"
                ),
            )
            self.assertIn(
                "google-play-public-propagation-2026-09-01.md",
                next(
                    block["body"]
                    for block in artifact["manifest"]["blocks"]
                    if block["id"] == "play_console_context"
                ),
            )
            rows = {
                row["gate_id"]: row
                for row in artifact["snapshot"]["datasets"]["gate_snapshot"]
            }
            canonical_gates = json.loads(
                (ROOT / "growth/quality/gates.json").read_text(encoding="utf-8")
            )["gates"]
            for gate_id, gate in canonical_gates.items():
                self.assertEqual(rows[gate_id]["status"], gate["status"])
                self.assertEqual(rows[gate_id]["evidence"], gate["reason"])
            self.assertIn(
                "current Android artifacts are protected-signed",
                rows["android_physical_smoke"]["decision"],
            )
            self.assertIn(
                "current Apple build 8 is protected-signed",
                rows["ios_physical_smoke"]["decision"],
            )
            self.assertIn(
                "source-current TestFlight",
                rows["ios_crash_gate"]["next_action"],
            )
            self.assertIn(
                "protected signing and durable materialization passed",
                rows["release_artifact_source_sync"]["decision"],
            )
            issues = {
                issue["id"]: issue["message"]
                for issue in artifact["snapshot"]["accessIssues"]
            }
            current_revision = canonical_gates["release_artifact_source_sync"][
                "source_revision"
            ]
            self.assertEqual(
                issues["ios_crash_report_missing"],
                canonical_gates["ios_crash_gate"]["reason"],
            )
            self.assertEqual(
                issues["release_artifact_source_sync_missing"],
                canonical_gates["release_artifact_source_sync"]["reason"],
            )
            self.assertIn(
                "Pass trusted macOS verification",
                rows["release_artifact_source_sync"]["next_action"],
            )
            self.assertIn(
                "source-current phone and Wear artifacts",
                rows["android_physical_smoke"]["next_action"],
            )
            self.assertNotIn(
                "background checks",
                rows["android_physical_smoke"]["next_action"],
            )
            self.assertNotIn(
                "TalkBack and background",
                rows["android_physical_smoke"]["next_action"],
            )
            self.assertNotIn(
                "exact-current 9c2dce4",
                issues["release_artifact_source_sync_missing"],
            )
            self.assertIn(
                f"Current product/build-input commit {current_revision}",
                artifact["manifest"]["blocks"][0]["body"],
            )
            self.assertIn(
                canonical_gates["release_artifact_source_sync"]["reason"],
                artifact["manifest"]["blocks"][0]["body"],
            )
            self.assertIn(
                "manifest remains fail-closed at 0/3 verified-current",
                artifact["manifest"]["blocks"][0]["body"],
            )
            self.assertIn(
                "The August 29 event maps to iPhone",
                artifact["manifest"]["blocks"][0]["body"],
            )
            self.assertIn(
                canonical_gates["android_physical_smoke"]["reason"],
                artifact["manifest"]["blocks"][0]["body"],
            )
            self.assertIn(
                canonical_gates["ios_physical_smoke"]["reason"],
                artifact["manifest"]["blocks"][0]["body"],
            )
            self.assertIn(
                "All predecessor artifacts and observations are historical and non-transferable",
                artifact["manifest"]["blocks"][0]["body"],
            )
            self.assertIn(
                "Canonical release authority remains fail-closed",
                artifact["manifest"]["blocks"][0]["body"],
            )
            self.assertIn(
                "canonical 2026-09-01 capture",
                artifact["manifest"]["blocks"][0]["body"],
            )
            evaluation_source = next(
                source
                for source in artifact["sources"]
                if source["id"] == "evaluation_snapshot"
            )
            self.assertEqual(
                evaluation_source["path"],
                "growth/reports/evaluation-2026-09-01.json",
            )
            self.assertNotIn(
                "neither candidate run yielded a retained",
                artifact["manifest"]["blocks"][0]["body"],
            )
            self.assertNotIn(
                "atomically 3/3 verified-current with byte_verified=true",
                artifact["manifest"]["blocks"][0]["body"],
            )
            self.assertNotIn(
                "replacement build 7 is signed and byte-verified but not delivered",
                artifact["manifest"]["blocks"][0]["body"],
            )

    def test_second_replace_failure_rolls_back_both_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            artifact_path = temporary_root / "artifact.json"
            gate_sql_path = temporary_root / "gate_snapshot.sql"
            gates_path = temporary_root / "gates.json"
            evaluation_path = temporary_root / "evaluation.json"
            for source, destination in (
                (ROOT / "growth/dashboard/artifact.json", artifact_path),
                (ROOT / "growth/dashboard/gate_snapshot.sql", gate_sql_path),
                (ROOT / "growth/quality/gates.json", gates_path),
                (
                    ROOT / "growth/reports/evaluation-2026-09-01.json",
                    evaluation_path,
                ),
            ):
                shutil.copy2(source, destination)

            gate_id = "ios_crash_gate"
            replacement_reason = "fixture reason requiring both outputs to change"
            gates = json.loads(gates_path.read_text(encoding="utf-8"))
            gates["gates"][gate_id]["reason"] = replacement_reason
            gates_path.write_text(json.dumps(gates), encoding="utf-8")
            evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
            evaluation_gate = next(
                gate
                for gate in evaluation["guardrails"]["scale_gates"]
                if gate["id"] == gate_id
            )
            evaluation_gate["reason"] = replacement_reason
            evaluation_path.write_text(json.dumps(evaluation), encoding="utf-8")

            original_artifact = artifact_path.read_bytes()
            original_sql = gate_sql_path.read_bytes()
            real_replace = sync_dashboard_gates._replace_staged_file
            replace_count = 0

            def fail_second_replace(temporary: Path, destination: Path) -> None:
                nonlocal replace_count
                replace_count += 1
                if replace_count == 2:
                    raise OSError("fixture second replace failure")
                real_replace(temporary, destination)

            with mock.patch.object(
                sync_dashboard_gates,
                "_replace_staged_file",
                side_effect=fail_second_replace,
            ):
                with self.assertRaisesRegex(OSError, "second replace failure"):
                    sync_dashboard_gates.sync(
                        artifact_path,
                        gate_sql_path,
                        gates_path,
                        evaluation_path,
                        "2026-08-30T12:34:56Z",
                    )

            self.assertGreaterEqual(replace_count, 3)
            self.assertEqual(artifact_path.read_bytes(), original_artifact)
            self.assertEqual(gate_sql_path.read_bytes(), original_sql)


if __name__ == "__main__":
    unittest.main()
