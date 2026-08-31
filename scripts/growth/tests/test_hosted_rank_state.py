from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.growth.common import config_fingerprint, load_json
from scripts.growth.hosted_rank_state import (
    HostedRankStateError,
    build_bundle,
    install_bundle,
    prepare_history,
    validate_bundle,
)


ROOT = Path(__file__).resolve().parents[3]
DAY = "2026-08-31"
SOURCE_REVISION = "1" * 40


class HostedRankStateTest(unittest.TestCase):
    def snapshot(self, *, status: str = "fail") -> dict:
        config = load_json(ROOT / "growth/config.json")
        complete = status != "unknown"
        return {
            "schema_version": 1,
            "date": DAY,
            "captured_at": f"{DAY}T00:05:30+05:00",
            "timezone": "Asia/Tashkent",
            "config_fingerprint": config_fingerprint(config),
            "app": config["app"],
            "market": config["market"],
            "goal_evidence_complete": complete,
            "evaluation": {
                "status": status,
                "complete": complete,
            },
        }

    def evaluation(self, snapshot: dict) -> dict:
        return {
            "schema_version": 1,
            "as_of": DAY,
            "top10_goal": {
                "as_of_snapshot_present": True,
                "current_config_fingerprint": snapshot["config_fingerprint"],
                "current_streak_days": 0,
                "max_streak_days": 0,
                "required_days": 7,
                "goal_achieved": False,
            },
        }

    @staticmethod
    def write_json(path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    def build_test_bundle(
        self,
        root: Path,
        *,
        status: str = "fail",
        state_parent: str = "absent",
    ) -> Path:
        snapshot = self.snapshot(status=status)
        snapshot_path = root / "snapshot.json"
        evaluation_path = root / "evaluation.json"
        bundle = root / "bundle"
        self.write_json(snapshot_path, snapshot)
        self.write_json(evaluation_path, self.evaluation(snapshot))
        build_bundle(
            source_root=ROOT,
            snapshot_path=snapshot_path,
            evaluation_path=evaluation_path,
            output_dir=bundle,
            expected_date=DAY,
            source_revision=SOURCE_REVISION,
            state_parent=state_parent,
            monitor_exit_code=1 if status == "unknown" else 0,
            repository="4810092/Weather",
            run_id="123",
            run_attempt="1",
            event_name="schedule",
            ref="refs/heads/master",
        )
        return bundle

    def test_prepare_history_uses_source_only_before_branch_exists(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            self.write_json(
                source / "2026-08-30.json",
                {"date": "2026-08-30", "marker": "original"},
            )
            output = root / "history"

            copied = prepare_history(
                source_rank_dir=source,
                state_rank_dir=None,
                output_dir=output,
                expected_date=DAY,
            )

            self.assertEqual(copied, [output / "2026-08-30.json"])
            self.assertEqual(
                (output / "2026-08-30.json").read_bytes(),
                (source / "2026-08-30.json").read_bytes(),
            )

    def test_prepare_history_rejects_existing_day_without_touching_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            existing = source / f"{DAY}.json"
            self.write_json(existing, {"date": DAY, "marker": "first-writer"})
            preserved = existing.read_bytes()

            with self.assertRaisesRegex(
                HostedRankStateError, "canonical day already exists"
            ):
                prepare_history(
                    source_rank_dir=source,
                    state_rank_dir=None,
                    output_dir=root / "history",
                    expected_date=DAY,
                )

            self.assertEqual(existing.read_bytes(), preserved)
            self.assertFalse((root / "history").exists())

    def test_prepare_history_can_copy_an_existing_day_for_idempotent_noop(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            existing = source / f"{DAY}.json"
            self.write_json(existing, {"date": DAY, "marker": "first-writer"})

            copied = prepare_history(
                source_rank_dir=source,
                state_rank_dir=None,
                output_dir=root / "history",
                expected_date=DAY,
                allow_existing_date=True,
            )

            self.assertEqual(copied, [root / "history" / f"{DAY}.json"])
            self.assertEqual(copied[0].read_bytes(), existing.read_bytes())

    def test_idempotent_noop_still_rejects_default_state_divergence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            state = root / "state"
            self.write_json(
                source / f"{DAY}.json",
                {"date": DAY, "marker": "default-only"},
            )
            state.mkdir()

            with self.assertRaisesRegex(
                HostedRankStateError,
                f"default branch contains {DAY}, but the observation branch does not",
            ):
                prepare_history(
                    source_rank_dir=source,
                    state_rank_dir=state,
                    output_dir=root / "history",
                    expected_date=DAY,
                    allow_existing_date=True,
                )

            self.assertFalse((root / "history").exists())

    def test_state_branch_must_contain_byte_identical_default_history(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            state = root / "state"
            payload = {"date": "2026-08-30", "marker": "canonical"}
            self.write_json(source / "2026-08-30.json", payload)
            self.write_json(state / "2026-08-30.json", payload)
            self.write_json(
                state / "2026-08-29.json",
                {"date": "2026-08-29", "marker": "branch-only"},
            )

            prepare_history(
                source_rank_dir=source,
                state_rank_dir=state,
                output_dir=root / "history",
                expected_date=DAY,
            )
            self.assertTrue((root / "history/2026-08-29.json").is_file())

            divergent = copy.deepcopy(payload)
            divergent["marker"] = "rewritten"
            self.write_json(source / "2026-08-30.json", divergent)
            with self.assertRaisesRegex(
                HostedRankStateError, "canonical history diverges"
            ):
                prepare_history(
                    source_rank_dir=source,
                    state_rank_dir=state,
                    output_dir=root / "second-history",
                    expected_date=DAY,
                )

    def test_bundle_round_trip_binds_hashes_context_and_unknown_status(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = self.build_test_bundle(root, status="unknown")

            receipt = validate_bundle(
                source_root=ROOT,
                bundle_dir=bundle,
                expected_date=DAY,
                source_revision=SOURCE_REVISION,
                state_parent="absent",
                monitor_exit_code=1,
            )

            self.assertEqual(receipt["daily_evaluation_status"], "unknown")
            self.assertEqual(receipt["monitor_exit_code"], 1)
            self.assertIsNone(receipt["state_parent_revision"])

    def test_bundle_tampering_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = self.build_test_bundle(root)
            snapshot_path = bundle / f"growth/data/public-rank/{DAY}.json"
            snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
            snapshot["tampered"] = True
            self.write_json(snapshot_path, snapshot)

            with self.assertRaisesRegex(
                HostedRankStateError, "receipt snapshot hash"
            ):
                validate_bundle(
                    source_root=ROOT,
                    bundle_dir=bundle,
                    expected_date=DAY,
                    source_revision=SOURCE_REVISION,
                    state_parent="absent",
                    monitor_exit_code=0,
                )

    def test_monitor_exit_must_match_fail_closed_daily_status(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot = self.snapshot(status="unknown")
            snapshot_path = root / "snapshot.json"
            evaluation_path = root / "evaluation.json"
            self.write_json(snapshot_path, snapshot)
            self.write_json(evaluation_path, self.evaluation(snapshot))

            with self.assertRaisesRegex(
                HostedRankStateError, "monitor exit 0 conflicts"
            ):
                build_bundle(
                    source_root=ROOT,
                    snapshot_path=snapshot_path,
                    evaluation_path=evaluation_path,
                    output_dir=root / "bundle",
                    expected_date=DAY,
                    source_revision=SOURCE_REVISION,
                    state_parent="absent",
                    monitor_exit_code=0,
                    repository="4810092/Weather",
                    run_id="123",
                    run_attempt="1",
                    event_name="schedule",
                    ref="refs/heads/master",
                )

    def test_second_install_cannot_overwrite_any_canonical_byte(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = self.build_test_bundle(root)
            state = root / "state"
            state.mkdir()
            arguments = {
                "source_root": ROOT,
                "bundle_dir": bundle,
                "state_root": state,
                "expected_date": DAY,
                "source_revision": SOURCE_REVISION,
                "state_parent": "absent",
                "monitor_exit_code": 0,
            }
            installed = install_bundle(**arguments)
            before = {path: path.read_bytes() for path in installed}

            with self.assertRaisesRegex(
                HostedRankStateError, "refusing to overwrite"
            ):
                install_bundle(**arguments)

            self.assertEqual({path: path.read_bytes() for path in installed}, before)
            self.assertEqual(list(state.rglob("*.tmp")), [])

    def test_bundle_rejects_unexpected_files_and_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = self.build_test_bundle(root)
            (bundle / "unexpected.txt").write_text("no\n", encoding="utf-8")
            with self.assertRaisesRegex(HostedRankStateError, "file set differs"):
                validate_bundle(
                    source_root=ROOT,
                    bundle_dir=bundle,
                    expected_date=DAY,
                    source_revision=SOURCE_REVISION,
                    state_parent="absent",
                    monitor_exit_code=0,
                )

    def test_install_rejects_a_symlinked_state_parent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = self.build_test_bundle(root)
            state = root / "state"
            outside = root / "outside"
            state.mkdir()
            outside.mkdir()
            (state / "growth").symlink_to(outside, target_is_directory=True)

            with self.assertRaisesRegex(
                HostedRankStateError, "unsafe parent|outside the state root"
            ):
                install_bundle(
                    source_root=ROOT,
                    bundle_dir=bundle,
                    state_root=state,
                    expected_date=DAY,
                    source_revision=SOURCE_REVISION,
                    state_parent="absent",
                    monitor_exit_code=0,
                )

            self.assertEqual(list(outside.rglob("*")), [])


if __name__ == "__main__":
    unittest.main()
