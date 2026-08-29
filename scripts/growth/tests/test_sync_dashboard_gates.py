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
    def test_sync_relabels_predecessor_release_evidence(self) -> None:
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
                ROOT / "growth/reports/evaluation-2026-08-30.json",
                "2026-08-30T12:34:56Z",
            )

            artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
            rows = {
                row["gate_id"]: row
                for row in artifact["snapshot"]["datasets"]["gate_snapshot"]
            }
            self.assertIn("predecessor API 24", rows["android_physical_smoke"]["decision"])
            self.assertIn("predecessor simulator", rows["ios_physical_smoke"]["decision"])
            issues = {
                issue["id"]: issue["message"]
                for issue in artifact["snapshot"]["accessIssues"]
            }
            current_revision = json.loads(
                (ROOT / "growth/quality/gates.json").read_text(encoding="utf-8")
            )["gates"]["release_artifact_source_sync"]["source_revision"]
            self.assertIn(
                f"current source authority {current_revision[:7]}",
                issues["ios_crash_report_missing"],
            )
            self.assertIn(
                "0/3 current artifacts are byte-verified",
                issues["release_artifact_source_sync_missing"],
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
                "deterministic per-target release profiles",
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
                    ROOT / "growth/reports/evaluation-2026-08-30.json",
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
