#!/usr/bin/env python3
"""Build and install immutable GitHub-hosted public-rank state bundles."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

if __package__ in (None, ""):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.growth.common import config_fingerprint, load_json  # noqa: E402


TIMEZONE = "Asia/Tashkent"
OBSERVATION_BRANCH = "growth-observations"
CANONICAL_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}\.json$")
REVISION = re.compile(r"^[0-9a-f]{40}$")
RECEIPT_KIND = "nimbo-uz-hosted-canonical-rank"


class HostedRankStateError(ValueError):
    """The hosted observation cannot be proven safe to persist."""


def _day(value: str) -> str:
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise HostedRankStateError(f"invalid ISO date: {value!r}") from error
    if parsed.isoformat() != value:
        raise HostedRankStateError(f"date is not canonical ISO form: {value!r}")
    return value


def _object(path: Path, label: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise HostedRankStateError(f"{label} must be a regular file: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise HostedRankStateError(f"cannot read {label}: {error}") from error
    if not isinstance(payload, dict):
        raise HostedRankStateError(f"{label} must be a JSON object")
    return payload


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise HostedRankStateError(f"hash input must be a regular file: {path}")
    return _sha256_bytes(path.read_bytes())


def _canonical_files(root: Path, label: str) -> dict[str, Path]:
    if root.is_symlink() or not root.is_dir():
        raise HostedRankStateError(f"{label} must be a directory: {root}")
    result: dict[str, Path] = {}
    for path in root.iterdir():
        if path.suffix == ".json" and not CANONICAL_NAME.fullmatch(path.name):
            raise HostedRankStateError(
                f"{label} has a non-canonical root JSON file: {path.name}"
            )
        if not CANONICAL_NAME.fullmatch(path.name):
            continue
        captured_day = path.name.removesuffix(".json")
        _day(captured_day)
        payload = _object(path, f"{label} snapshot {captured_day}")
        if payload.get("date") != captured_day:
            raise HostedRankStateError(
                f"{label} snapshot date differs from filename: {path.name}"
            )
        result[captured_day] = path
    return result


def _write_exclusive(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as error:
        raise HostedRankStateError(f"refusing to overwrite {path}") from error


def prepare_history(
    *,
    source_rank_dir: Path,
    state_rank_dir: Path | None,
    output_dir: Path,
    expected_date: str,
    allow_existing_date: bool = False,
) -> list[Path]:
    """Copy the authoritative history after proving source/state consistency."""

    expected_date = _day(expected_date)
    if output_dir.exists():
        raise HostedRankStateError(f"history output already exists: {output_dir}")
    source = _canonical_files(source_rank_dir, "default-branch rank directory")
    if expected_date in source and not allow_existing_date:
        raise HostedRankStateError(
            f"canonical day already exists on the default branch: {expected_date}"
        )

    if state_rank_dir is None:
        authoritative = source
    else:
        state = _canonical_files(state_rank_dir, "observation-branch rank directory")
        if expected_date in state and not allow_existing_date:
            raise HostedRankStateError(
                f"canonical day already exists on {OBSERVATION_BRANCH}: {expected_date}"
            )
        for captured_day, source_path in source.items():
            state_path = state.get(captured_day)
            if state_path is None:
                raise HostedRankStateError(
                    f"default branch contains {captured_day}, but the observation "
                    "branch does not"
                )
            if source_path.read_bytes() != state_path.read_bytes():
                raise HostedRankStateError(
                    f"canonical history diverges for {captured_day}; refusing "
                    "automatic reconciliation"
                )
        authoritative = state

    output_dir.mkdir(parents=True)
    copied: list[Path] = []
    for captured_day, source_path in sorted(authoritative.items()):
        destination = output_dir / f"{captured_day}.json"
        _write_exclusive(destination, source_path.read_bytes())
        copied.append(destination)
    return copied


def _expected_monitor_exit(snapshot: dict[str, Any]) -> int:
    evaluation = snapshot.get("evaluation")
    status = evaluation.get("status") if isinstance(evaluation, dict) else None
    if status in {"pass", "fail"}:
        return 0
    if status == "unknown":
        return 1
    raise HostedRankStateError("snapshot evaluation.status is invalid")


def validate_snapshot(
    snapshot_path: Path,
    *,
    source_root: Path,
    expected_date: str,
    monitor_exit_code: int,
) -> dict[str, Any]:
    expected_date = _day(expected_date)
    snapshot = _object(snapshot_path, "rank snapshot")
    if snapshot.get("schema_version") != 1:
        raise HostedRankStateError("rank snapshot schema_version must be 1")
    if snapshot.get("date") != expected_date:
        raise HostedRankStateError("rank snapshot date differs from expected date")
    if snapshot.get("timezone") != TIMEZONE:
        raise HostedRankStateError(f"rank snapshot timezone must be {TIMEZONE}")
    try:
        captured_at = datetime.fromisoformat(str(snapshot["captured_at"]))
    except (KeyError, ValueError) as error:
        raise HostedRankStateError("rank snapshot captured_at is invalid") from error
    if captured_at.tzinfo is None or captured_at.utcoffset() is None:
        raise HostedRankStateError("rank snapshot captured_at must be timezone-aware")
    if captured_at.astimezone(ZoneInfo(TIMEZONE)).date().isoformat() != expected_date:
        raise HostedRankStateError("rank snapshot crossed the expected local date")

    config = load_json(source_root / "growth/config.json")
    expected_fingerprint = config_fingerprint(config)
    if snapshot.get("config_fingerprint") != expected_fingerprint:
        raise HostedRankStateError("rank snapshot config fingerprint is not current")
    if snapshot.get("app") != config.get("app"):
        raise HostedRankStateError("rank snapshot app identity differs from config")
    if snapshot.get("market") != config.get("market"):
        raise HostedRankStateError("rank snapshot market differs from config")

    evaluation = snapshot.get("evaluation")
    if not isinstance(evaluation, dict):
        raise HostedRankStateError("rank snapshot evaluation is missing")
    if not isinstance(evaluation.get("complete"), bool):
        raise HostedRankStateError("rank snapshot evaluation.complete must be boolean")
    if snapshot.get("goal_evidence_complete") is not evaluation["complete"]:
        raise HostedRankStateError(
            "goal_evidence_complete differs from evaluation.complete"
        )
    expected_exit = _expected_monitor_exit(snapshot)
    if monitor_exit_code != expected_exit:
        raise HostedRankStateError(
            f"monitor exit {monitor_exit_code} conflicts with snapshot status"
        )
    return snapshot


def validate_evaluation(
    evaluation_path: Path,
    *,
    expected_date: str,
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    evaluation = _object(evaluation_path, "growth evaluation")
    if evaluation.get("schema_version") != 1:
        raise HostedRankStateError("growth evaluation schema_version must be 1")
    if evaluation.get("as_of") != expected_date:
        raise HostedRankStateError("growth evaluation as_of differs from capture date")
    goal = evaluation.get("top10_goal")
    if not isinstance(goal, dict):
        raise HostedRankStateError("growth evaluation top10_goal is missing")
    if goal.get("as_of_snapshot_present") is not True:
        raise HostedRankStateError("growth evaluation does not include the new snapshot")
    if goal.get("current_config_fingerprint") != snapshot.get("config_fingerprint"):
        raise HostedRankStateError(
            "growth evaluation fingerprint differs from the new snapshot"
        )
    required_days = goal.get("required_days")
    if isinstance(required_days, bool) or not isinstance(required_days, int):
        raise HostedRankStateError("growth evaluation required_days is invalid")
    return evaluation


def _revision(value: str, label: str, *, absent_allowed: bool = False) -> str:
    if absent_allowed and value == "absent":
        return value
    if REVISION.fullmatch(value) is None:
        raise HostedRankStateError(f"{label} must be a lowercase 40-hex revision")
    return value


def _bundle_paths(root: Path, captured_day: str) -> dict[str, Path]:
    return {
        "snapshot": root / "growth/data/public-rank" / f"{captured_day}.json",
        "evaluation": root / "growth/reports" / f"evaluation-{captured_day}.json",
        "receipt": (
            root
            / "growth/data/public-rank/hosted-receipts"
            / f"{captured_day}.json"
        ),
    }


def _safe_state_destination(state_root: Path, destination: Path) -> None:
    if state_root.is_symlink() or not state_root.is_dir():
        raise HostedRankStateError("state root must be a regular directory")
    resolved_root = state_root.resolve()
    cursor = destination.parent
    while cursor != state_root:
        if cursor.exists() and (cursor.is_symlink() or not cursor.is_dir()):
            raise HostedRankStateError(
                f"state destination has an unsafe parent: {cursor}"
            )
        if state_root not in cursor.parents:
            raise HostedRankStateError("state destination escapes the state root")
        cursor = cursor.parent
    if not destination.resolve(strict=False).is_relative_to(resolved_root):
        raise HostedRankStateError("state destination resolves outside the state root")


def build_bundle(
    *,
    source_root: Path,
    snapshot_path: Path,
    evaluation_path: Path,
    output_dir: Path,
    expected_date: str,
    source_revision: str,
    state_parent: str,
    monitor_exit_code: int,
    repository: str,
    run_id: str,
    run_attempt: str,
    event_name: str,
    ref: str,
) -> dict[str, Any]:
    expected_date = _day(expected_date)
    source_revision = _revision(source_revision, "source revision")
    state_parent = _revision(
        state_parent, "state parent", absent_allowed=True
    )
    if monitor_exit_code not in {0, 1}:
        raise HostedRankStateError("monitor exit must be 0 or 1")
    if repository != "4810092/Weather":
        raise HostedRankStateError("unexpected GitHub repository identity")
    if event_name not in {"schedule", "workflow_dispatch"}:
        raise HostedRankStateError("unexpected workflow event")
    if ref != "refs/heads/master":
        raise HostedRankStateError("hosted capture must run from refs/heads/master")
    if not run_id.isdigit() or not run_attempt.isdigit():
        raise HostedRankStateError("workflow run identity must be numeric")
    if output_dir.exists():
        raise HostedRankStateError(f"bundle output already exists: {output_dir}")

    snapshot = validate_snapshot(
        snapshot_path,
        source_root=source_root,
        expected_date=expected_date,
        monitor_exit_code=monitor_exit_code,
    )
    evaluation = validate_evaluation(
        evaluation_path,
        expected_date=expected_date,
        snapshot=snapshot,
    )
    snapshot_bytes = snapshot_path.read_bytes()
    evaluation_bytes = evaluation_path.read_bytes()
    paths = _bundle_paths(output_dir, expected_date)
    _write_exclusive(paths["snapshot"], snapshot_bytes)
    _write_exclusive(paths["evaluation"], evaluation_bytes)

    receipt: dict[str, Any] = {
        "schema_version": 1,
        "kind": RECEIPT_KIND,
        "date": expected_date,
        "timezone": TIMEZONE,
        "captured_at": snapshot["captured_at"],
        "source_revision": source_revision,
        "state_parent_revision": None if state_parent == "absent" else state_parent,
        "observation_branch": OBSERVATION_BRANCH,
        "monitor_exit_code": monitor_exit_code,
        "daily_evaluation_status": snapshot["evaluation"]["status"],
        "config_fingerprint": snapshot["config_fingerprint"],
        "snapshot": {
            "path": f"growth/data/public-rank/{expected_date}.json",
            "sha256": _sha256_bytes(snapshot_bytes),
        },
        "evaluation": {
            "path": f"growth/reports/evaluation-{expected_date}.json",
            "sha256": _sha256_bytes(evaluation_bytes),
            "current_streak_days": evaluation["top10_goal"][
                "current_streak_days"
            ],
            "goal_achieved": evaluation["top10_goal"]["goal_achieved"],
        },
        "workflow": {
            "repository": repository,
            "run_id": int(run_id),
            "run_attempt": int(run_attempt),
            "event_name": event_name,
            "ref": ref,
        },
    }
    receipt_bytes = (
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    ).encode("utf-8")
    _write_exclusive(paths["receipt"], receipt_bytes)
    return receipt


def validate_bundle(
    *,
    source_root: Path,
    bundle_dir: Path,
    expected_date: str,
    source_revision: str,
    state_parent: str,
    monitor_exit_code: int,
) -> dict[str, Any]:
    expected_date = _day(expected_date)
    source_revision = _revision(source_revision, "source revision")
    state_parent = _revision(
        state_parent, "state parent", absent_allowed=True
    )
    expected_paths = _bundle_paths(bundle_dir, expected_date)
    expected_files = {path.resolve() for path in expected_paths.values()}
    actual_files: set[Path] = set()
    if bundle_dir.is_symlink() or not bundle_dir.is_dir():
        raise HostedRankStateError("bundle root must be a directory")
    for path in bundle_dir.rglob("*"):
        if path.is_symlink():
            raise HostedRankStateError(f"bundle contains a symlink: {path}")
        if path.is_file():
            actual_files.add(path.resolve())
    if actual_files != expected_files:
        raise HostedRankStateError("bundle file set differs from the exact contract")

    receipt = _object(expected_paths["receipt"], "hosted capture receipt")
    if receipt.get("schema_version") != 1 or receipt.get("kind") != RECEIPT_KIND:
        raise HostedRankStateError("hosted capture receipt identity is invalid")
    expected_parent_value = None if state_parent == "absent" else state_parent
    expected_fields = {
        "date": expected_date,
        "timezone": TIMEZONE,
        "source_revision": source_revision,
        "state_parent_revision": expected_parent_value,
        "observation_branch": OBSERVATION_BRANCH,
        "monitor_exit_code": monitor_exit_code,
    }
    for key, value in expected_fields.items():
        if receipt.get(key) != value:
            raise HostedRankStateError(f"receipt field {key} differs from context")

    snapshot = validate_snapshot(
        expected_paths["snapshot"],
        source_root=source_root,
        expected_date=expected_date,
        monitor_exit_code=monitor_exit_code,
    )
    evaluation = validate_evaluation(
        expected_paths["evaluation"],
        expected_date=expected_date,
        snapshot=snapshot,
    )
    if receipt.get("captured_at") != snapshot.get("captured_at"):
        raise HostedRankStateError("receipt captured_at differs from snapshot")
    if receipt.get("config_fingerprint") != snapshot.get("config_fingerprint"):
        raise HostedRankStateError("receipt fingerprint differs from snapshot")
    if receipt.get("daily_evaluation_status") != snapshot["evaluation"]["status"]:
        raise HostedRankStateError("receipt daily status differs from snapshot")
    workflow = receipt.get("workflow")
    if not isinstance(workflow, dict):
        raise HostedRankStateError("receipt workflow identity is missing")
    if workflow.get("repository") != "4810092/Weather":
        raise HostedRankStateError("receipt repository identity is invalid")
    if workflow.get("event_name") not in {"schedule", "workflow_dispatch"}:
        raise HostedRankStateError("receipt workflow event is invalid")
    if workflow.get("ref") != "refs/heads/master":
        raise HostedRankStateError("receipt workflow ref is invalid")
    for field in ("run_id", "run_attempt"):
        value = workflow.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise HostedRankStateError(f"receipt workflow {field} is invalid")
    snapshot_receipt = receipt.get("snapshot")
    evaluation_receipt = receipt.get("evaluation")
    if not isinstance(snapshot_receipt, dict) or not isinstance(
        evaluation_receipt, dict
    ):
        raise HostedRankStateError("receipt artifact hashes are missing")
    if snapshot_receipt != {
        "path": f"growth/data/public-rank/{expected_date}.json",
        "sha256": _sha256(expected_paths["snapshot"]),
    }:
        raise HostedRankStateError("receipt snapshot hash or path differs")
    expected_evaluation_receipt = {
        "path": f"growth/reports/evaluation-{expected_date}.json",
        "sha256": _sha256(expected_paths["evaluation"]),
        "current_streak_days": evaluation["top10_goal"]["current_streak_days"],
        "goal_achieved": evaluation["top10_goal"]["goal_achieved"],
    }
    if evaluation_receipt != expected_evaluation_receipt:
        raise HostedRankStateError("receipt evaluation evidence differs")
    return receipt


def install_bundle(
    *,
    source_root: Path,
    bundle_dir: Path,
    state_root: Path,
    expected_date: str,
    source_revision: str,
    state_parent: str,
    monitor_exit_code: int,
) -> list[Path]:
    validate_bundle(
        source_root=source_root,
        bundle_dir=bundle_dir,
        expected_date=expected_date,
        source_revision=source_revision,
        state_parent=state_parent,
        monitor_exit_code=monitor_exit_code,
    )
    bundle_paths = _bundle_paths(bundle_dir, expected_date)
    state_paths = _bundle_paths(state_root, expected_date)
    for destination in state_paths.values():
        _safe_state_destination(state_root, destination)
        if destination.exists() or destination.is_symlink():
            raise HostedRankStateError(f"refusing to overwrite {destination}")

    created: list[Path] = []
    staged: list[Path] = []
    try:
        for key in ("snapshot", "evaluation", "receipt"):
            destination = state_paths[key]
            destination.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temporary_name = tempfile.mkstemp(
                dir=destination.parent,
                prefix=f".{destination.name}.",
                suffix=".tmp",
            )
            temporary = Path(temporary_name)
            staged.append(temporary)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(bundle_paths[key].read_bytes())
                handle.flush()
                os.fsync(handle.fileno())
            try:
                os.link(temporary, destination)
            except FileExistsError as error:
                raise HostedRankStateError(
                    f"refusing to overwrite {destination}"
                ) from error
            created.append(destination)
        return created
    except Exception:
        for destination in reversed(created):
            destination.unlink(missing_ok=True)
        raise
    finally:
        for temporary in staged:
            temporary.unlink(missing_ok=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare-history")
    prepare.add_argument("--source-rank-dir", type=Path, required=True)
    prepare.add_argument("--state-rank-dir", type=Path)
    prepare.add_argument("--output-dir", type=Path, required=True)
    prepare.add_argument("--date", required=True)
    prepare.add_argument("--allow-existing-date", action="store_true")

    for command in ("build-bundle", "validate-bundle", "install-bundle"):
        child = subparsers.add_parser(command)
        child.add_argument("--source-root", type=Path, required=True)
        child.add_argument("--date", required=True)
        child.add_argument("--source-revision", required=True)
        child.add_argument("--state-parent", required=True)
        child.add_argument("--monitor-exit-code", type=int, required=True)
        if command == "build-bundle":
            child.add_argument("--snapshot", type=Path, required=True)
            child.add_argument("--evaluation", type=Path, required=True)
            child.add_argument("--output-dir", type=Path, required=True)
            child.add_argument("--repository", required=True)
            child.add_argument("--run-id", required=True)
            child.add_argument("--run-attempt", required=True)
            child.add_argument("--event-name", required=True)
            child.add_argument("--ref", required=True)
        else:
            child.add_argument("--bundle-dir", type=Path, required=True)
            if command == "install-bundle":
                child.add_argument("--state-root", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "prepare-history":
            copied = prepare_history(
                source_rank_dir=args.source_rank_dir,
                state_rank_dir=args.state_rank_dir,
                output_dir=args.output_dir,
                expected_date=args.date,
                allow_existing_date=args.allow_existing_date,
            )
            print(f"Prepared {len(copied)} immutable canonical snapshots.")
        elif args.command == "build-bundle":
            receipt = build_bundle(
                source_root=args.source_root,
                snapshot_path=args.snapshot,
                evaluation_path=args.evaluation,
                output_dir=args.output_dir,
                expected_date=args.date,
                source_revision=args.source_revision,
                state_parent=args.state_parent,
                monitor_exit_code=args.monitor_exit_code,
                repository=args.repository,
                run_id=args.run_id,
                run_attempt=args.run_attempt,
                event_name=args.event_name,
                ref=args.ref,
            )
            print(
                f"Built {RECEIPT_KIND} bundle for {receipt['date']} "
                f"({receipt['daily_evaluation_status']})."
            )
        elif args.command == "validate-bundle":
            validate_bundle(
                source_root=args.source_root,
                bundle_dir=args.bundle_dir,
                expected_date=args.date,
                source_revision=args.source_revision,
                state_parent=args.state_parent,
                monitor_exit_code=args.monitor_exit_code,
            )
            print(f"Validated immutable hosted bundle for {args.date}.")
        else:
            installed = install_bundle(
                source_root=args.source_root,
                bundle_dir=args.bundle_dir,
                state_root=args.state_root,
                expected_date=args.date,
                source_revision=args.source_revision,
                state_parent=args.state_parent,
                monitor_exit_code=args.monitor_exit_code,
            )
            print(f"Installed {len(installed)} no-clobber state files for {args.date}.")
    except (HostedRankStateError, OSError, KeyError, TypeError) as error:
        print(f"hosted rank state rejected: {error}", file=__import__("sys").stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
