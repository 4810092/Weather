#!/usr/bin/env python3
"""Synchronize the portable growth dashboard with canonical gate evidence."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = ROOT / "growth/dashboard/artifact.json"
DEFAULT_GATE_SQL = ROOT / "growth/dashboard/gate_snapshot.sql"
DEFAULT_GATES = ROOT / "growth/quality/gates.json"
DEFAULT_EVALUATION = ROOT / "growth/reports/evaluation-2026-08-30.json"


def _load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return payload


def _sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _stage_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        text=True,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        return temporary
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def _replace_staged_file(temporary: Path, path: Path) -> None:
    temporary.replace(path)


def _atomic_text(path: Path, content: str) -> None:
    temporary = _stage_text(path, content)
    try:
        _replace_staged_file(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _atomic_texts(updates: tuple[tuple[Path, str], ...]) -> None:
    """Replace related text files together, rolling back a partial commit."""

    pending: list[tuple[Path, str, str | None]] = []
    identities: set[Path] = set()
    for path, content in updates:
        identity = path.resolve()
        if identity in identities:
            raise ValueError(f"duplicate atomic update target: {path}")
        identities.add(identity)
        original = path.read_text(encoding="utf-8") if path.exists() else None
        if original != content:
            pending.append((path, content, original))
    if not pending:
        return

    staged: list[tuple[Path, Path, str | None]] = []
    try:
        for path, content, original in pending:
            staged.append((path, _stage_text(path, content), original))

        attempted: list[tuple[Path, str | None]] = []
        try:
            for path, temporary, original in staged:
                attempted.append((path, original))
                _replace_staged_file(temporary, path)
        except Exception as write_error:
            rollback_failures: list[str] = []
            for path, original in reversed(attempted):
                try:
                    if original is None:
                        path.unlink(missing_ok=True)
                    else:
                        _atomic_text(path, original)
                except Exception as rollback_error:
                    rollback_failures.append(f"{path}: {rollback_error}")
            if rollback_failures:
                raise RuntimeError(
                    "dashboard sync failed and rollback was incomplete: "
                    + "; ".join(rollback_failures)
                ) from write_error
            raise
    finally:
        for _, temporary, _ in staged:
            temporary.unlink(missing_ok=True)


def sync(
    artifact_path: Path,
    gate_sql_path: Path,
    gates_path: Path,
    evaluation_path: Path,
    generated_at: str,
) -> None:
    artifact = _load_object(artifact_path)
    gates_payload = _load_object(gates_path)
    evaluation = _load_object(evaluation_path)
    gates = gates_payload.get("gates")
    datasets = artifact.get("snapshot", {}).get("datasets")
    rows = datasets.get("gate_snapshot") if isinstance(datasets, dict) else None
    if not isinstance(gates, dict) or not isinstance(rows, list):
        raise ValueError("gate registry or dashboard gate_snapshot is malformed")

    evaluation_gates = {
        gate.get("id"): gate
        for gate in evaluation.get("guardrails", {}).get("scale_gates", [])
        if isinstance(gate, dict) and isinstance(gate.get("id"), str)
    }
    row_ids = {
        row.get("gate_id")
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("gate_id"), str)
    }
    if row_ids != set(gates) or set(evaluation_gates) != set(gates):
        raise ValueError("dashboard, evaluation, and gate registry IDs differ")

    sql = gate_sql_path.read_text(encoding="utf-8")
    changed_rows = 0
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("dashboard gate_snapshot contains a non-object row")
        gate_id = row["gate_id"]
        gate = gates[gate_id]
        evaluation_gate = evaluation_gates[gate_id]
        status = gate.get("status")
        reason = gate.get("reason")
        if not isinstance(status, str) or not isinstance(reason, str):
            raise ValueError(f"{gate_id}: canonical status/reason is malformed")
        if (
            evaluation_gate.get("actual") != status
            or evaluation_gate.get("reason") != reason
        ):
            raise ValueError(f"{gate_id}: evaluation is stale relative to gates.json")

        old_status = row.get("status")
        old_reason = row.get("evidence")
        old_next = row.get("next_action")
        new_next = old_next
        if gate_id == "release_artifact_source_sync":
            row["decision"] = (
                "BLOCKED · current hosted source proof pending; 0/3 artifacts "
                "byte-verified; signed/physical matrix missing"
            )
            new_next = (
                "Unlock the local login Keychain, provision the four remaining "
                "protected release-signing secrets, run the master-only hosted "
                "workflow, promote its verified receipt, and bind exact "
                "physical QA to the retained bytes"
            )
        elif gate_id == "android_physical_smoke":
            row["decision"] = (
                "BLOCKED · current provider tests green; current hosted, signed, "
                "and physical phone/tablet/widget/Wear matrix missing"
            )
        elif gate_id == "ios_physical_smoke":
            row["decision"] = (
                "BLOCKED · current provider tests green; current hosted Apple, "
                "distribution-signed build 6, and physical matrix missing"
            )
        if not all(
            isinstance(value, str)
            for value in (row.get("gate"), old_status, old_reason, old_next, new_next)
        ):
            raise ValueError(f"{gate_id}: dashboard gate row is malformed")
        if (old_status, old_reason, old_next) != (status, reason, new_next):
            old_tuple = ", ".join(
                _sql_literal(value)
                for value in (
                    gate_id,
                    row["gate"],
                    old_status,
                    old_reason,
                    old_next,
                )
            )
            new_tuple = ", ".join(
                _sql_literal(value)
                for value in (
                    gate_id,
                    row["gate"],
                    status,
                    reason,
                    new_next,
                )
            )
            if sql.count(old_tuple) != 1:
                raise ValueError(
                    f"{gate_id}: gate_snapshot.sql does not contain one old tuple"
                )
            sql = sql.replace(old_tuple, new_tuple, 1)
            changed_rows += 1
        row["status"] = status
        row["evidence"] = reason
        row["next_action"] = new_next

    sources = artifact.get("sources")
    if not isinstance(sources, list):
        raise ValueError("dashboard sources are malformed")
    source_by_id = {
        source.get("id"): source
        for source in sources
        if isinstance(source, dict) and isinstance(source.get("id"), str)
    }
    baseline_source = source_by_id.get("baseline_snapshot")
    gate_source = source_by_id.get("gate_snapshot")
    evaluation_source = source_by_id.get("evaluation_snapshot")
    if (
        not isinstance(baseline_source, dict)
        or not isinstance(gate_source, dict)
        or not isinstance(evaluation_source, dict)
    ):
        raise ValueError("dashboard gate/evaluation sources are missing")
    baseline_query = baseline_source.get("query")
    gate_query = gate_source.get("query")
    evaluation_query = evaluation_source.get("query")
    if (
        not isinstance(baseline_query, dict)
        or not isinstance(gate_query, dict)
        or not isinstance(evaluation_query, dict)
    ):
        raise ValueError("dashboard gate/evaluation source queries are malformed")
    metric_definitions = baseline_query.get("metric_definitions")
    if not isinstance(metric_definitions, list):
        raise ValueError("dashboard baseline metric definitions are malformed")
    old_play_definition = "Play conversion is the reported Play value and remains unreconciled"
    new_play_definition = (
        "Play conversion is the historical reported baseline; exact weekly "
        "all-country and UZ listing populations are reported separately"
    )
    if old_play_definition in metric_definitions:
        metric_definitions[
            metric_definitions.index(old_play_definition)
        ] = new_play_definition
    elif new_play_definition not in metric_definitions:
        raise ValueError("dashboard Play conversion metric definition is missing")
    gate_query["sql"] = sql
    gate_query["executed_at"] = generated_at
    evaluation_query["executed_at"] = generated_at
    snapshot = artifact.get("snapshot")
    if not isinstance(snapshot, dict):
        raise ValueError("dashboard snapshot is malformed")
    access_issues = snapshot.get("accessIssues")
    if not isinstance(access_issues, list):
        raise ValueError("dashboard access issues are malformed")
    access_issue_by_id = {
        issue.get("id"): issue
        for issue in access_issues
        if isinstance(issue, dict) and isinstance(issue.get("id"), str)
    }
    raw_exports_issue = access_issue_by_id.get("raw_store_exports_missing")
    crash_issue = access_issue_by_id.get("ios_crash_report_missing")
    source_issue = access_issue_by_id.get("release_artifact_source_sync_missing")
    if (
        not isinstance(raw_exports_issue, dict)
        or not isinstance(crash_issue, dict)
        or not isinstance(source_issue, dict)
    ):
        raise ValueError("dashboard raw-export/release/crash access issues are missing")
    current_revision = gates["release_artifact_source_sync"].get(
        "source_revision"
    )
    if not isinstance(current_revision, str) or len(current_revision) != 40:
        raise ValueError("release artifact source revision is malformed")
    current_revision_short = current_revision[:7]

    raw_exports_issue["message"] = (
        "Current App Store Connect analytics exports remain unavailable. The "
        "validated Google Play aggregate for 2026-08-18..2026-08-24 is retained "
        "without PII: all-country listing traffic is 26 visitors and 11 unique "
        "install clicks, while UZ is 0 visitors and 0 clicks. UZ conversion is "
        "therefore UNKNOWN because its denominator is zero; the derived 42.31% "
        "all-country rate is diagnostic only. Exact-scope first launch, retention, "
        "active-use, ratings, vitals, and user-loss evidence remains unavailable."
    )
    crash_issue["message"] = (
        "App Store Connect confirms one crash on iOS 1.0.1 on August 25, 2026, "
        "but privacy suppression exposes no report, stack, UUID, device, or OS. "
        "An existing API key authenticates for app, version, build, and "
        "analytics-request inventory and confirms public 1.0.1 build 4, but "
        "the build-detail and diagnostic-signature GETs return security 403. "
        f"Current source {current_revision_short} passes twelve targeted iOS "
        "Simulator provider mapping/service tests. Predecessor hosted run "
        "33297505825 is non-transferable. Neither the authenticated inventory "
        "nor these bounded regression tests identify or close the "
        f"historical crash for current source authority {current_revision_short}."
    )
    source_issue["message"] = (
        f"Current product/build-input commit {current_revision_short} has no retained signed "
        "phone vc8, Wear 1000008, or distribution-signed Apple build-6 "
        "candidate, so 0/3 current artifacts are byte-verified. Fourteen "
        "targeted Android-host and twelve targeted iOS Simulator provider "
        "tests pass, including cache preservation after rejected required-row "
        "responses. The complete hosted Android/iOS and API 24/API 36 "
        "phone/tablet matrix for this authority is pending. Runs 33297505825 "
        "and 33299592101 passed only for its predecessor and are explicitly "
        "non-transferable. The manual master-only protected GitHub-hosted workflow and "
        "pre-manifest verifier remain configured and statically validated. The "
        "protected environment has 4/8 required secrets: its Android keystore "
        "payload and three Apple provisioning profiles are present, while two "
        "Android passwords plus the Apple P12 and its transport password remain "
        "absent. The signed workflow has not run. The locked "
        "local login Keychain still rejects "
        "Android protected credential reads and Apple private-key use. All signed "
        "bundles, screenshots, and device results belong to predecessor revisions "
        "and remain non-transferable regression or creative provenance only. None "
        "satisfies current upload signing or the complete physical matrix. "
        "CoreDevice readiness must be re-established, and App Store Connect "
        "contains no 1.1.0 version or builds 5/6. A bounded 1.1.0 version-create "
        "POST returned 403 and the final GET proved zero partial draft; no "
        "localization, asset, build association, submission, release, or other "
        "store mutation followed."
    )
    manifest = artifact.get("manifest")
    if not isinstance(manifest, dict):
        raise ValueError("dashboard manifest is malformed")
    blocks = manifest.get("blocks")
    if not isinstance(blocks, list) or not blocks or not isinstance(blocks[0], dict):
        raise ValueError("dashboard verdict block is missing")
    verdict = blocks[0].get("body")
    if not isinstance(verdict, str):
        raise ValueError("dashboard verdict body is malformed")
    current_summary = (
        "Current product/build-input commit "
        + current_revision
        + " keeps phone 1.1.0 (8), Wear OS 1.1.0 (1000008), and Apple "
        "1.1.0 (6), with fail-closed Apple source-revision plumbing and "
        "deterministic per-target release profiles. It tolerates omitted "
        "optional Open-Meteo forecast/AQI arrays while keeping required "
        "weather/time rows fail-closed. Fourteen targeted Android-host and "
        "twelve targeted iOS Simulator tests pass. The complete hosted matrix "
        "for this authority is pending; predecessor runs 33297505825 and "
        "33299592101 are non-transferable. The "
        "protected master-only hosted workflow and pre-manifest verifier are "
        "implemented but have not run because only 4/8 release-signing secrets "
        "are provisioned. No source-current signed artifact or physical-device "
        "matrix exists, so 0/3 current artifacts are byte-verified and the "
        "signed/physical gates remain blocked. "
        "Predecessor commit "
        "9c2dce4200dbba5487c8c458ade4616005fde6e6 closes three deterministic "
        "storage-failure exception escapes and adds four throwing-repository "
        "regressions, but all of its binaries, screenshots, and device results "
        "are historical and non-transferable."
    )
    current_pattern = re.compile(
        r"Current product/build-input commit [0-9a-f]{40} keeps .*?"
        r"are historical and non-transferable\.",
        re.DOTALL,
    )
    verdict, current_summary_count = current_pattern.subn(
        current_summary,
        verdict,
        count=1,
    )
    prior_start = "Product commit 9c2dce4200dbba5487c8c458ade4616005fde6e6 closes"
    prior_end = "historical event."
    if current_summary_count == 0 and prior_start in verdict:
        start = verdict.index(prior_start)
        end = verdict.index(prior_end, start) + len(prior_end)
        verdict = verdict[:start] + current_summary + verdict[end:]
        current_summary_count = 1
    if current_summary_count != 1:
        raise ValueError("dashboard verdict current-release summary is missing")
    verdict = verdict.replace(
        "Exact phone and Wear AABs embed 9c2dce4",
        "Predecessor phone and Wear AABs embed 9c2dce4",
    ).replace(
        "Exact Apple app, widget, and watch Release simulator hashes",
        "Predecessor Apple app, widget, and watch Release simulator hashes",
    ).replace(
        "A clean exact-current physical General Mobile API 25 run",
        "A clean predecessor physical General Mobile API 25 run",
    ).replace(
        "The byte-identical exact-current debug APK",
        "The byte-identical predecessor debug APK",
    ).replace(
        "from the exact-current 9c2dce4 build-6 simulator app",
        "from the source-bound predecessor 9c2dce4 build-6 simulator app",
    ).replace(
        "the Play conversion denominator is still unreconciled.",
        "the latest validated weekly Play slice has zero UZ visitors, so UZ "
        "conversion remains unknown; its 42.31% all-country rate is diagnostic only.",
    )
    blocks[0]["body"] = verdict
    manifest["generatedAt"] = generated_at
    snapshot["generatedAt"] = generated_at

    _atomic_texts(
        (
            (gate_sql_path, sql),
            (
                artifact_path,
                json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
            ),
        )
    )
    print(f"Synchronized {changed_rows} dashboard gate row(s) at {generated_at}.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--gate-sql", type=Path, default=DEFAULT_GATE_SQL)
    parser.add_argument("--gates", type=Path, default=DEFAULT_GATES)
    parser.add_argument("--evaluation", type=Path, default=DEFAULT_EVALUATION)
    parser.add_argument("--generated-at", required=True)
    arguments = parser.parse_args()
    sync(
        arguments.artifact,
        arguments.gate_sql,
        arguments.gates,
        arguments.evaluation,
        arguments.generated_at,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
