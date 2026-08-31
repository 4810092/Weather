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
DEFAULT_EVALUATION = ROOT / "growth/reports/evaluation-2026-08-31.json"


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
        if gate_id == "ios_crash_gate":
            new_next = (
                "Obtain and symbolicate any diagnostic Apple exposes, upload "
                "the exact retained IPA unchanged to TestFlight, complete the "
                "iPhone/iPad/widget/watch matrix, and collect post-rollout evidence"
            )
        elif gate_id == "release_artifact_source_sync":
            row["decision"] = (
                "PASS · local and protected hosted full-byte verification passed; "
                "manifest is atomically 3/3 verified-current"
            )
            new_next = (
                "Require the protected hosted chain to recheck the mutable draft before "
                "every later use, then bind store-delivered physical QA without changing "
                "the promoted artifact bytes"
            )
        elif gate_id == "android_physical_smoke":
            row["decision"] = (
                "BLOCKED · exact AAB-derived upload-key phone/API 25 passed; "
                "Play-delivered phone/tablet/widget/Wear matrix missing"
            )
            new_next = (
                "Deliver the exact phone and Wear AABs through Play Internal, rerun "
                "the phone scope against the Play-delivered package, and complete "
                "physical tablet/widget and paired Wear OS QA"
            )
        elif gate_id == "ios_physical_smoke":
            row["decision"] = (
                "BLOCKED · exact App Store-profile distribution IPA retained; TestFlight "
                "iPhone/iPad/widget/watch matrix missing"
            )
            new_next = (
                "Upload the exact retained IPA unchanged to TestFlight, install it "
                "on the ready iPhone and iPad, restore watch readiness, then run "
                "the complete iPhone/iPad/widget/watch matrix"
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
    old_play_definitions = (
        "Play conversion is the reported Play value and remains unreconciled",
        "Play conversion is the historical reported baseline; exact weekly "
        "all-country and UZ listing populations are reported separately",
    )
    new_play_definition = (
        "Play conversion is the 2026-08-28 reported baseline and was not "
        "revalidated on 2026-08-31"
    )
    if new_play_definition not in metric_definitions:
        old_play_definition = next(
            (
                definition
                for definition in old_play_definitions
                if definition in metric_definitions
            ),
            None,
        )
        if old_play_definition is None:
            raise ValueError("dashboard Play conversion metric definition is missing")
        metric_definitions[
            metric_definitions.index(old_play_definition)
        ] = new_play_definition
    scale_reason = gates_payload.get("scale_status_reason")
    scale_status = gates_payload.get("scale_status")
    if not isinstance(scale_reason, str) or not isinstance(scale_status, str):
        raise ValueError("dashboard scale status/reason is malformed")
    sql, scale_comment_count = re.subn(
        r"(?m)^-- Public outreach and acquisition scaling remain gated .*$",
        f"-- {scale_reason}",
        sql,
        count=1,
    )
    if scale_comment_count != 1:
        raise ValueError("dashboard gate SQL scale-status comment is missing")
    gate_query["description"] = (
        "Loads the fail-closed scale gates and their next evidence-producing "
        f"action. Scale status is {scale_status}. {scale_reason}"
    )
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
        "The 2026-08-31 App Store overview is available as a read-only observation "
        "(300 impressions, 23 product-page views, 8 first downloads, 1 redownload, "
        "3 updates, 4.86% reported conversion, and insufficient retention), but no "
        "raw export or reporting-window metadata is attached. Google overview "
        "values are carried forward from 2026-08-28 and were not revalidated. The "
        "validated Google Play aggregate for 2026-08-18..2026-08-24 remains "
        "separate: all-country listing traffic is 26 visitors and 11 unique "
        "install clicks, while UZ is 0 visitors and 0 clicks, so UZ conversion is "
        "UNKNOWN."
    )
    crash_issue["message"] = (
        "App Store Connect reports two crashes for public iOS 1.0.1 (4), one on "
        "August 25 and one on August 29, 2026. The August 29 event maps to "
        "iPhone; the August 25 device/OS dimension is suppressed or unavailable. "
        "Neither event exposes "
        "a diagnostic, stack, incident/signature ID, or crashed-binary UUID. "
        "An existing API key authenticates for app, version, build, and "
        "analytics-request inventory, but diagnostic-signature GETs return "
        "security 403. "
        f"Current source {current_revision_short} passes twelve targeted iOS "
        "Simulator provider mapping/service tests. Exact-source hosted run "
        "33300967788 also passed shared Simulator tests, all 18 Apple surface-"
        "state tests, and the unsigned application build. Protected run "
        "33381050098 additionally produced a retained, independently verified "
        "distribution-signed 1.1.0 (6) IPA/archive. That candidate is not the "
        "crashed public build, has not been exercised through TestFlight, identifies "
        "neither production event, and does not close the crash gate for current "
        f"source authority {current_revision_short}."
    )
    source_issue["message"] = (
        f"Current product/build-input commit {current_revision_short} passed exact-source "
        "ordinary GitHub Actions run 33300967788, including all 15 API 24/API 36 "
        "Compose UI tests and all 18 Apple surface-state tests. Protected run "
        "33381050098 then passed both macOS jobs with all 8/8 signing inputs and "
        "produced a schema-v3 receipt for phone d4a90676…, Wear e76d685b…, and "
        "Apple 7466afb1…. The GitHub ZIP matched its API digest; the safe-extracted "
        "closed tree and all three candidates passed an independent verifier run "
        "and are retained outside Git under a complete checksum manifest. Hosted "
        "materialization run 33392732428 then passed at evidence head 30a67edf: it "
        "validated the exact source artifact/package/receipt bindings and stored the "
        "package and receipt as hash-bound assets 537966386 and 537966414 in "
        "unpublished draft release 379745439. A fresh local macOS run downloaded and "
        "rechecked those exact assets, safely extracted the closed tree, verified "
        "pinned Bundletool 1.18.3, and returned byte_verified=true for phone, Wear, "
        "and Apple. Protected workflow_run 33405849102 then completed isolated "
        "no-checkout staging and the separate read-only hosted macOS verifier at "
        "b07192e, revalidating the live draft and returning byte_verified=true for "
        "all three artifacts. The committed upload manifest is atomically 3/3 "
        "verified-current and remains draft-blocked. The draft is mutable and the "
        "protected chain must recheck it before every later use. The Play-delivered "
        "Android physical matrix and TestFlight Apple matrix remain "
        "missing; two public iOS crashes still lack diagnostics. No store upload, "
        "processing, submission, release, or availability is claimed."
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
        "twelve targeted iOS Simulator tests pass. Exact-source GitHub Actions "
        "run 33300967788 passed ordinary Android/iOS, all 15 API 24/API 36 "
        "phone/tablet Compose UI tests, and all 18 Apple surface-state tests. "
        "Its retained archives are unsigned/test regression evidence only. "
        "Exact-source debug APK and pulled installed bytes share SHA-256 prefix "
        "d66c8f0 and "
        "passed a bounded physical API 25 phone/widget smoke, including denied "
        "location, Bukhara search, live forecast, cache/recovery, process health, "
        "and cleanup. This is debug-certificate evidence, not upload signing. The "
        "protected master-only hosted run 33381050098 passed both jobs with all "
        "8/8 signing inputs and produced retained, independently byte-verified "
        "phone, Wear, and Apple candidates. The schema-v3 receipt proves 3/3 "
        "candidate bytes. Hosted materialization run 33392732428 then validated the "
        "exact source artifact/package/receipt bindings and retained the package and "
        "receipt as hash-bound assets in unpublished draft release 379745439. A fresh "
        "local macOS run then reopened those exact assets, verified pinned Bundletool, "
        "and returned byte_verified=true for all three outputs. Protected workflow_run "
        "33405849102 repeated the complete verifier successfully at b07192e. The "
        "committed manifest is atomically 3/3 verified-current and remains "
        "draft-blocked. The exact phone AAB was then converted without rebuilding into "
        "an upload-key-signed universal APK; installed and pulled bytes matched at "
        "e970352d…, and the clean physical API 25 onboarding/live/share/offline/"
        "recovery smoke passed. This is not Play app-signing-key delivery, so the "
        "Play-delivered phone/tablet/widget/Wear and TestFlight Apple matrices remain "
        "missing. "
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
    verdict = verdict.replace(
        "Public iOS 1.0.1 (4) now has two reported crashes, one on August 25 "
        "and one on August 29. One maps to iPhone; the other device/OS "
        "dimension is suppressed or unavailable, and neither exposes a "
        "diagnostic, stack, incident/signature ID, or crashed-binary UUID.",
        "Public iOS 1.0.1 (4) now has two reported crashes, one on August 25 "
        "and one on August 29. The August 29 event maps to iPhone; the August "
        "25 device/OS dimension is suppressed or unavailable, and neither "
        "exposes a diagnostic, stack, incident/signature ID, or crashed-binary "
        "UUID.",
    )
    verdict = verdict.replace(
        "Android Keychain metadata and the existing mode-600 keystore are "
        "present, but protected signing access remains unavailable.",
        "Android Keychain metadata and the existing mode-600 keystore remain "
        "present. Protected run 33381050098 used all 8/8 signing inputs and "
        "yielded a retained, independently byte-verified package; physical "
        "delivery remains separate.",
    )
    verdict = verdict.replace(
        "There is no exact-current signed phone/Wear artifact, distribution-"
        "signed Apple archive, iOS 15 runtime pass, or matching physical matrix.",
        "Exact-current signed phone/Wear and Apple artifacts are retained, "
        "byte-verified, and manifest-promoted, but not store-delivered; "
        "there is no iOS 15 runtime pass or matching physical matrix.",
    )
    verdict = verdict.replace(
        "There is no retained, accepted, byte-verified exact-current signed "
        "phone/Wear artifact or distribution-signed Apple archive, and no iOS "
        "15 runtime pass or matching physical matrix.",
        "Exact-current signed phone/Wear and Apple artifacts are retained, "
        "byte-verified, and manifest-promoted, but not store-delivered; "
        "there is no iOS 15 runtime pass or matching physical matrix.",
    )
    verdict = verdict.replace(
        "Android Keychain metadata and the existing mode-600 keystore remain "
        "present. The protected environment now contains all 8/8 signing "
        "inputs, but neither candidate run yielded a retained, byte-verified "
        "package; hosted proof of the current correction remains pending.",
        "Android Keychain metadata and the existing mode-600 keystore remain "
        "present. Protected run 33381050098 used all 8/8 signing inputs and "
        "yielded a retained, independently byte-verified package; physical "
        "delivery remains separate.",
    )
    verdict = verdict.replace(
        "At 20:44 +05:00 the iPad was paired but not action-ready; the iPhone "
        "and watch remained unavailable.",
        "At the August 31 read-only device check, the iPhone 14 Pro and iPad mini 5 "
        "were paired, booted, and Developer Mode enabled; the iPhone can take a "
        "TestFlight update and the iPad a fresh install after processing. The paired "
        "Series 5 watch was compatible, but Developer Mode was disabled and its "
        "developer tunnel disconnected.",
    )
    verdict = verdict.replace(
        "Scale status remains hold; public outreach and acquisition scaling "
        "remain gated on crash diagnosis, source-synced signed phone, Wear OS, "
        "and Apple artifacts, complete physical-device coverage, and critical "
        "console guardrails.",
        "Scale status remains hold; public outreach and acquisition scaling "
        "remain gated on crash diagnosis, complete physical-device and internal-"
        "delivery coverage, and critical console guardrails. The hosted full-byte "
        "repeat passes; its chain must still recheck the mutable draft before every "
        "later use.",
    )
    verdict = verdict.replace(
        "Scale status remains hold; public outreach and acquisition scaling "
        "remain gated on crash diagnosis, durable manifest promotion of the "
        "retained candidates, complete physical-device coverage, and critical "
        "console guardrails.",
        "Scale status remains hold; public outreach and acquisition scaling "
        "remain gated on crash diagnosis, complete physical-device and internal-"
        "delivery coverage, and critical console guardrails. The hosted full-byte "
        "repeat passes; its chain must still recheck the mutable draft before every "
        "later use.",
    )
    verdict = verdict.replace(
        "Scale status remains hold; public outreach and acquisition scaling "
        "remain gated on crash diagnosis, full trusted macOS verification and "
        "atomic manifest promotion of the materialized candidates, complete "
        "physical-device coverage, and critical console guardrails.",
        "Scale status remains hold; public outreach and acquisition scaling "
        "remain gated on crash diagnosis, complete physical-device and internal-"
        "delivery coverage, and critical console guardrails. The hosted full-byte "
        "repeat passes; its chain must still recheck the mutable draft before every "
        "later use.",
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
    verdict = verdict.replace(
        "Exact-current signed phone/Wear and Apple candidates are retained and "
        "byte-verified, but they are not manifest-promoted or store-delivered;",
        "Exact-current signed phone/Wear and Apple candidates are retained, "
        "byte-verified, and manifest-promoted, but not store-delivered;",
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
