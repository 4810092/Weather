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
DEFAULT_EVALUATION = ROOT / "growth/reports/evaluation-2026-09-01.json"
DEFAULT_RANK = ROOT / "growth/data/public-rank/2026-09-01.json"
DEFAULT_BASELINE = ROOT / "growth/baseline/2026-08-31.json"
DEFAULT_BASELINE_SQL = ROOT / "growth/dashboard/baseline_snapshot.sql"
DEFAULT_DRIVER_SQL = ROOT / "growth/dashboard/driver_comparison.sql"
DEFAULT_RANK_SQL = ROOT / "growth/dashboard/rank_snapshot.sql"
DEFAULT_FRAMEWORK = ROOT / "growth/kpi-framework.json"


def _load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return payload


def _sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _observed_rank(surface: dict[str, Any]) -> str:
    rank = surface.get("target_rank")
    bound = surface.get("target_rank_bound")
    if isinstance(rank, int) and not isinstance(rank, bool) and rank > 0 and bound is None:
        return str(rank)
    if rank is None and isinstance(bound, str) and re.fullmatch(r">[1-9]\d*", bound):
        return bound
    raise ValueError(f"rank surface {surface.get('surface_id')!r} is malformed")


def _number_word(value: int) -> str:
    return {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}.get(
        value, str(value)
    )


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
    *,
    baseline_path: Path = DEFAULT_BASELINE,
    baseline_sql_path: Path = DEFAULT_BASELINE_SQL,
    driver_sql_path: Path = DEFAULT_DRIVER_SQL,
    rank_path: Path = DEFAULT_RANK,
    rank_sql_path: Path = DEFAULT_RANK_SQL,
    framework_path: Path = DEFAULT_FRAMEWORK,
) -> None:
    artifact = _load_object(artifact_path)
    gates_payload = _load_object(gates_path)
    evaluation = _load_object(evaluation_path)
    baseline = _load_object(baseline_path)
    rank = _load_object(rank_path)
    framework = _load_object(framework_path)
    gates = gates_payload.get("gates")
    datasets = artifact.get("snapshot", {}).get("datasets")
    rows = datasets.get("gate_snapshot") if isinstance(datasets, dict) else None
    if not isinstance(gates, dict) or not isinstance(rows, list):
        raise ValueError("gate registry or dashboard gate_snapshot is malformed")

    try:
        rank_date = rank["date"]
        captured_at = rank["captured_at"]
        rank_evaluation = rank["evaluation"]
        rank_apple = rank["surfaces"]["apple"]
        rank_google = rank["surfaces"]["google"]
        requirements = framework["primary_goal"]["daily_requirements"]
        top10_goal = evaluation["top10_goal"]
    except (KeyError, TypeError) as error:
        raise ValueError(f"rank/evaluation/framework source is malformed: {error}") from error
    if (
        not isinstance(rank_date, str)
        or not isinstance(captured_at, str)
        or rank.get("goal_evidence_complete") is not True
        or rank_evaluation.get("complete") is not True
        or evaluation.get("as_of") != rank_date
        or top10_goal.get("as_of_snapshot_present") is not True
        or top10_goal.get("current_config_fingerprint")
        != rank.get("config_fingerprint")
    ):
        raise ValueError("rank and evaluation are not one complete comparable day")
    profiles = requirements.get("google_required_profiles")
    if not isinstance(profiles, list) or not profiles or not all(
        isinstance(profile, str) and profile for profile in profiles
    ):
        raise ValueError("rank framework profiles are malformed")
    weather_rank = _observed_rank(rank_apple["search"]["weather"])
    category_rank = _observed_rank(rank_apple["category"])
    rank_target = requirements["apple_weather_chart_rank_lte"]
    google_rank_target = requirements["google_weather_category_rank_lte"]
    diagnostics = framework["primary_goal"]["diagnostic_requirements"]
    generic_target = diagnostics["generic_queries_required"]
    quorum = diagnostics["generic_query_profile_quorum"]
    query_ids = set(rank_google["search"][profiles[0]])
    if any(set(rank_google["search"][profile]) != query_ids for profile in profiles):
        raise ValueError("rank profiles do not share one fixed query set")
    query_count = len(query_ids)
    qualifying_queries = rank_evaluation.get("google_generic_top10_query_count")
    if not isinstance(qualifying_queries, int) or isinstance(qualifying_queries, bool):
        raise ValueError("rank generic-query evaluation is malformed")

    platforms = baseline.get("platforms", {})
    apple_metrics = platforms.get("apple", {}).get("metrics")
    google_metrics = platforms.get("google", {}).get("metrics")
    if not isinstance(apple_metrics, dict):
        raise ValueError("baseline Apple metrics are malformed")
    if not isinstance(google_metrics, dict):
        raise ValueError("baseline Google metrics are malformed")
    apple_ratings = apple_metrics.get("ratings_count")
    apple_rating_evidence = apple_metrics.get("ratings_count_evidence")
    apple_average_rating = apple_metrics.get("average_rating")
    if (
        not isinstance(apple_ratings, int)
        or isinstance(apple_ratings, bool)
        or apple_ratings < 0
        or not isinstance(apple_rating_evidence, str)
        or not apple_rating_evidence
        or not isinstance(apple_average_rating, (int, float))
        or isinstance(apple_average_rating, bool)
        or not 0 <= apple_average_rating <= 5
    ):
        raise ValueError("baseline Apple rating observation is malformed")
    installations = google_metrics.get("installations")
    first_launches = google_metrics.get("first_launches")
    monthly_active_devices = google_metrics.get("monthly_active_users")
    if not all(
        isinstance(value, int) and not isinstance(value, bool) and value >= 0
        for value in (installations, first_launches, monthly_active_devices)
    ):
        raise ValueError("baseline current Google counts are malformed")
    if installations == 0:
        raise ValueError("baseline installations cannot support a launch ratio")
    first_launch_rate = round(first_launches / installations, 4)

    platform_rows = datasets.get("platform_baseline")
    headline_rows = datasets.get("headline_metrics")
    driver_rows = datasets.get("driver_comparison")
    if (
        not isinstance(platform_rows, list)
        or not isinstance(headline_rows, list)
        or len(headline_rows) != 1
        or not isinstance(headline_rows[0], dict)
        or not isinstance(driver_rows, list)
    ):
        raise ValueError("dashboard baseline datasets are malformed")
    rank_rows = [
        {
            "check": "App Store search · weather",
            "result": f"{weather_rank} · target ≤{rank_target}",
            "surface": "App Store UZ search",
            "profile": "all",
            "query": "weather",
            "observed_rank": weather_rank,
            "target_rank": rank_target,
            "evidence_class": "fixed_public_capture",
        },
        {
            "check": "App Store · Weather chart",
            "result": f"{category_rank} · target ≤{rank_target}",
            "surface": "App Store UZ Weather chart",
            "profile": "official",
            "query": "category",
            "observed_rank": category_rank,
            "target_rank": rank_target,
            "evidence_class": "fixed_public_capture",
        },
    ]
    for profile in profiles:
        observed = _observed_rank(rank_google["category"][profile])
        rank_rows.append(
            {
                "check": f"Google category · {profile}",
                "result": f"{observed} · target ≤{google_rank_target}",
                "surface": "Google Play UZ Weather category",
                "profile": profile,
                "query": "category",
                "observed_rank": observed,
                "target_rank": google_rank_target,
                "evidence_class": "fixed_logged_out_capture",
            }
        )
    rank_rows.append(
        {
            "check": "Google generic-query diagnostic",
            "result": f"{qualifying_queries}/{query_count} qualify · diagnostic benchmark ≥{generic_target}",
            "surface": "Google Play UZ generic-query diagnostic",
            "profile": f"{quorum}-of-{len(profiles)} profiles",
            "query": f"{_number_word(query_count)} configured queries",
            "observed_rank": f"{qualifying_queries} qualifying queries",
            "target_rank": generic_target,
            "evidence_class": "fixed_logged_out_capture",
        }
    )
    datasets["rank_snapshot"] = rank_rows
    headline_rows[0]["top10_streak_days"] = top10_goal["current_streak_days"]
    headline_rows[0]["top10_streak_target"] = top10_goal["required_days"]
    headline_rows[0]["apple_weather_rank"] = weather_rank
    headline_rows[0]["rank_target"] = rank_target
    current_google = {
        "Installations": (str(installations), "live_global_last_28_days_2026-08-31"),
        "First launches": (str(first_launches), "live_global_last_28_days_2026-08-31"),
        "Monthly active devices": (
            str(monthly_active_devices),
            "live_global_last_28_days_2026-08-31",
        ),
    }
    apple_rating_seen = False
    seen_google: set[str] = set()
    for row in platform_rows:
        if not isinstance(row, dict):
            raise ValueError("dashboard platform_baseline contains a non-object row")
        if row.get("platform") == "App Store" and row.get("metric") == "Ratings":
            row["value"] = str(apple_ratings)
            row["evidence_class"] = apple_rating_evidence
            apple_rating_seen = True
            continue
        if row.get("platform") != "Google Play":
            continue
        metric = row.get("metric")
        if metric == "Monthly active users":
            metric = "Monthly active devices"
            row["metric"] = metric
            row["metric_label"] = "Google Play · Monthly active devices"
        current = current_google.get(metric)
        if current is None:
            continue
        row["value"], row["evidence_class"] = current
        seen_google.add(metric)
    if seen_google != set(current_google):
        raise ValueError("dashboard current Google baseline rows are incomplete")
    if not apple_rating_seen:
        raise ValueError("dashboard current Apple rating row is missing")
    headline_rows[0]["first_launch_rate"] = first_launch_rate
    launch_driver = [
        row
        for row in driver_rows
        if isinstance(row, dict)
        and row.get("metric") == "First launch / install"
        and row.get("series") == "Baseline"
    ]
    if len(launch_driver) != 1:
        raise ValueError("dashboard first-launch driver row is missing or duplicated")
    launch_driver[0]["rate"] = first_launch_rate

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
                "Keep build 9 unreleased; source-bind a monotonically newer Apple "
                "build, exercise its TestFlight background/widget path on iPhone "
                "and iPad, then collect post-release crash-free evidence"
            )
        elif gate_id == "release_artifact_source_sync":
            if status == "pass":
                row["decision"] = (
                    "PASS · protected signing and independent full-byte verification passed; "
                    "manifest is atomically 3/3 verified-current"
                )
                new_next = (
                    "Require the protected hosted chain to recheck the mutable draft "
                    "before every later use, then bind store-delivered physical QA"
                )
            else:
                row["decision"] = (
                    "BLOCKED · exact build 9 is runtime-failed and the corrected "
                    "source has no signed, source-bound successor"
                )
                new_next = (
                    "Create a monotonic Apple successor from corrected source, pass "
                    "protected signing and full-byte verification, then deliver it to TestFlight"
                )
        elif gate_id == "android_physical_smoke":
            if status == "pass":
                row["decision"] = (
                    "PASS · source-bound Android phone, tablet, widget, and Wear "
                    "runtime QA satisfies the owner-approved emulator policy"
                )
                new_next = (
                    "Preserve runtime and Internal-delivery evidence; collect a complete "
                    "post-delivery UZ Vitals window before any production decision"
                )
            else:
                row["decision"] = "BLOCKED · required Android runtime QA is incomplete"
                new_next = "Complete the source-bound Android runtime QA matrix"
        elif gate_id == "ios_physical_smoke":
            if status == "pass":
                row["decision"] = (
                    "PASS · source-current iPad Share, widget, and watch runtime QA "
                    "satisfies the owner-approved simulator policy"
                )
                new_next = (
                    "Preserve runtime coverage; separately complete App Store release "
                    "and crash-free evidence"
                )
            else:
                row["decision"] = (
                    "BLOCKED · exact TestFlight build 9 crashes during background "
                    "refresh and the correction has no TestFlight successor"
                )
                new_next = (
                    "Exercise a corrected, source-bound successor's background/widget "
                    "path on TestFlight iPhone and iPad"
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
    driver_source = source_by_id.get("driver_comparison")
    rank_source = source_by_id.get("rank_snapshot")
    gate_source = source_by_id.get("gate_snapshot")
    evaluation_source = source_by_id.get("evaluation_snapshot")
    if (
        not isinstance(baseline_source, dict)
        or not isinstance(driver_source, dict)
        or not isinstance(rank_source, dict)
        or not isinstance(gate_source, dict)
        or not isinstance(evaluation_source, dict)
    ):
        raise ValueError("dashboard gate/evaluation sources are missing")
    baseline_query = baseline_source.get("query")
    driver_query = driver_source.get("query")
    rank_query = rank_source.get("query")
    gate_query = gate_source.get("query")
    evaluation_query = evaluation_source.get("query")
    if (
        not isinstance(baseline_query, dict)
        or not isinstance(driver_query, dict)
        or not isinstance(rank_query, dict)
        or not isinstance(gate_query, dict)
        or not isinstance(evaluation_query, dict)
    ):
        raise ValueError("dashboard gate/evaluation source queries are malformed")
    baseline_query["sql"] = baseline_sql_path.read_text(encoding="utf-8")
    baseline_query["description"] = (
        "Loads the bounded 2026-08-31 store-console evidence plus the September 1 "
        "public Apple UZ rating/version lookup while keeping current global Play "
        "dashboard counts distinct from stale listing metrics."
    )
    baseline_query["filters"] = [
        "Console snapshot date 2026-08-31; public Apple UZ lookup rechecked 2026-09-01",
        f"Apple public UZ rating {apple_average_rating:.1f} from {apple_ratings} rating; no review text exposed",
        "Google installs, first launches, and monthly active devices are current global last-28-days counts",
        "Google impressions, listing conversion, and ratings are carried forward from 2026-08-28",
        "No cross-platform or cross-window denominator coercion",
    ]
    baseline_query["metric_definitions"] = [
        "Apple conversion is the App Store Connect reported 4.86% and is not recomputed from supplied counts",
        "Retention is insufficient and remains unknown rather than zero",
        "Play conversion is the 2026-08-28 reported baseline and was not revalidated on 2026-08-31",
        f"First launch rate is {first_launches} / {installations} = {first_launch_rate:.2%} and remains directional",
        "Monthly active users is displayed as the Play Console's monthly active devices count",
    ]
    driver_query["sql"] = driver_sql_path.read_text(encoding="utf-8")
    rank_query["sql"] = rank_sql_path.read_text(encoding="utf-8")
    rank_query["description"] = (
        "Loads the complete required category surfaces and separate search "
        "diagnostics from the canonical public-rank capture while preserving "
        "bounded absences."
    )
    rank_query["executed_at"] = captured_at
    rank_query["tables_used"] = [
        f"inline rank values backed by growth/data/public-rank/{rank_date}.json"
    ]
    rank_query["filters"] = [
        f"Snapshot date {rank_date}",
        "Storefront UZ",
        "Google logged-out profiles " + ", ".join(profiles),
        "diagnostic_capture_complete=false because auxiliary Apple Toshkent ob-havo search returned only one unique app",
        "goal_evidence_complete=true and evaluation.complete=true for all required category surfaces",
    ]
    baseline_query["executed_at"] = generated_at
    driver_query["executed_at"] = generated_at
    scale_reason = gates_payload.get("scale_status_reason")
    scale_status = gates_payload.get("scale_status")
    if not isinstance(scale_reason, str) or not isinstance(scale_status, str):
        raise ValueError("dashboard scale status/reason is malformed")
    sql, scale_comment_count = re.subn(
        r"(?m)^-- Public outreach and acquisition scaling remain .*$",
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
    evaluation_source["label"] = f"{rank_date} growth evaluation"
    evaluation_source["path"] = f"growth/reports/evaluation-{rank_date}.json"
    evaluation_query["sql"] = (
        "SELECT * FROM (VALUES ("
        f"{_sql_literal(rank_date)},{top10_goal['current_streak_days']},"
        f"{top10_goal['required_days']},"
        f"{'TRUE' if top10_goal['goal_achieved'] else 'FALSE'},TRUE)) "
        "AS evaluation(as_of,current_streak_days,required_days,goal_achieved,as_of_snapshot_present)"
    )
    evaluation_query["description"] = (
        "Loads the evaluated Top-10 streak state for the latest UZ rank day."
    )
    evaluation_query["tables_used"] = [
        f"inline evaluation values backed by growth/reports/evaluation-{rank_date}.json"
    ]
    evaluation_query["filters"] = [
        "Current comparable config fingerprint",
        f"Consecutive complete required category days through {rank_date}",
    ]
    evaluation_query["metric_definitions"] = [
        "Current streak counts consecutive complete days satisfying the Apple UZ Weather chart and all three fixed Google UZ Weather category profiles",
        "Generic-query results are validated ASO diagnostics and do not change the category-day result",
    ]
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
        "raw export or reporting-window metadata is attached. A separate public "
        f"Apple UZ lookup on September 1 reports {apple_ratings} rating at "
        f"{apple_average_rating:.1f}; it exposes no review text or reply surface. "
        "The authenticated "
        f"Play dashboard currently reports {installations} installs, {first_launches} "
        f"device first launches, and {monthly_active_devices} monthly active devices "
        "for its global last-28-days scope. Play impressions, listing conversion, "
        "and ratings remain carried forward from 2026-08-28. The "
        "validated Google Play aggregate for 2026-08-18..2026-08-24 remains "
        "separate: all-country listing traffic is 26 visitors and 11 unique "
        "install clicks, while UZ is 0 visitors and 0 clicks, so UZ conversion is "
        "UNKNOWN."
    )
    crash_issue["message"] = gates["ios_crash_gate"]["reason"]
    source_issue["message"] = gates["release_artifact_source_sync"]["reason"]
    manifest = artifact.get("manifest")
    if not isinstance(manifest, dict):
        raise ValueError("dashboard manifest is malformed")
    cards = {
        card.get("id"): card
        for card in manifest.get("cards", [])
        if isinstance(card, dict) and isinstance(card.get("id"), str)
    }
    play_conversion_card = cards.get("play_conversion")
    first_launch_card = cards.get("first_launch_rate")
    apple_search_card = cards.get("apple_search_rank")
    if not isinstance(play_conversion_card, dict) or not isinstance(
        first_launch_card, dict
    ) or not isinstance(apple_search_card, dict):
        raise ValueError("dashboard Play KPI cards are missing")
    apple_search_card["description"] = (
        f"Canonical {rank_date} UZ App Store public search for the non-branded "
        f"query weather records {weather_rank}; the August 28 baseline was #81. "
        "A bounded absence is not converted into a synthetic rank."
    )
    apple_search_metrics = apple_search_card.get("metrics")
    if not isinstance(apple_search_metrics, list):
        raise ValueError("dashboard Apple rank card metrics are malformed")
    apple_search_values = [
        metric
        for metric in apple_search_metrics
        if isinstance(metric, dict) and metric.get("field") == "apple_weather_rank"
    ]
    if len(apple_search_values) != 1:
        raise ValueError("dashboard Apple rank card value is missing or duplicated")
    apple_search_values[0]["format"] = "text" if weather_rank.startswith(">") else "number"
    play_conversion_card["description"] = (
        "Play listing conversion remains the reported 2026-08-28 value. Its "
        "source numerator and denominator were not shown in the August 31 global "
        "dashboard recheck, so it is not a reconciled KPI."
    )
    first_launch_card["description"] = (
        f"Directional global last-28-days calculation: {first_launches} device "
        f"first launches divided by {installations} installs = "
        f"{first_launch_rate:.2%}. The UI does not prove identical populations."
    )
    tables = {
        table.get("id"): table
        for table in manifest.get("tables", [])
        if isinstance(table, dict) and isinstance(table.get("id"), str)
    }
    baseline_table = tables.get("baseline_table")
    rank_table = tables.get("rank_table")
    if not isinstance(baseline_table, dict) or not isinstance(rank_table, dict):
        raise ValueError("dashboard baseline table is missing")
    rank_table["subtitle"] = (
        "The required category surfaces are complete and fail in both stores; "
        "generic-query results remain diagnostic only."
    )
    baseline_table["subtitle"] = (
        "Apple overview values and selected global Play last-28-days counts are "
        "current to August 31; the Apple UZ rating was publicly rechecked on "
        "September 1 and stale listing metrics are marked explicitly."
    )
    blocks = manifest.get("blocks")
    if not isinstance(blocks, list) or not blocks or not isinstance(blocks[0], dict):
        raise ValueError("dashboard verdict block is missing")
    manifest_sources = manifest.get("sources")
    if not isinstance(manifest_sources, list):
        raise ValueError("dashboard manifest sources are malformed")
    for source_rows in (sources, manifest_sources):
        rank_entries = [
            source
            for source in source_rows
            if isinstance(source, dict) and source.get("id") == "rank_snapshot"
        ]
        evaluation_entries = [
            source
            for source in source_rows
            if isinstance(source, dict) and source.get("id") == "evaluation_snapshot"
        ]
        if len(rank_entries) != 1 or len(evaluation_entries) != 1:
            raise ValueError("dashboard rank/evaluation source registry is malformed")
        rank_entries[0]["label"] = f"{rank_date} UZ rank snapshot"
        evaluation_entries[0]["label"] = f"{rank_date} growth evaluation"
        evaluation_entries[0]["path"] = f"growth/reports/evaluation-{rank_date}.json"
    play_context_blocks = [
        block
        for block in blocks
        if isinstance(block, dict) and block.get("id") == "play_console_context"
    ]
    if len(play_context_blocks) != 1:
        raise ValueError("dashboard Play Console context block is missing or duplicated")
    play_context_blocks[0]["body"] = (
        "## Authenticated Play context\n\n"
        f"At 23:17–23:23 +05:00 on August 31, the global last-28-days dashboard "
        f"reported {installations} installs, {first_launches} device first launches, "
        f"and {monthly_active_devices} monthly active devices. The directional "
        f"first-launch ratio is {first_launch_rate:.2%}; it is not promoted to a "
        "decision-eligible cohort rate because the UI does not prove identical "
        "populations. Play impressions, listing conversion, ratings, and production "
        "details remain carried forward where explicitly marked. The separate "
        "August 18–24 Store Listings import remains authoritative for its own window: "
        "26 all-country visitors and 11 unique install clicks, while UZ had zero "
        "visitors and zero clicks.\n\n"
        "A 05:05 +05:00 recheck confirms review request 14 still contains only the "
        "Uzbekistan Custom Store Listing's en-US "
        "and ru-RU store data and is under review. Managed publishing is off; approval, "
        "publication, and rank impact are not verified. A fixed logged-out gl=UZ "
        "recheck at the same checkpoint still exposed the pre-review public "
        "title Nimbo in both Uzbek and Russian product pages, so propagation is "
        "explicitly not verified. Phone Internal "
        "track 4700083514281298386 is active with the selected four-account License "
        "testers group. On September 1 the General Mobile opt-in was accepted and "
        "Google Play delivered version 1.1.0 (8) for bounded API 25 cold/live/share, "
        "offline/cache/recovery, large-text, and active system-TalkBack smoke. Wear "
        "Internal track 4699242452771231163 now has the same tester list "
        "and reports Active, but no physical Wear install exists. Evidence: "
        "growth/quality/google-play-console-2026-08-31.md and "
        "growth/quality/play-delivered-android-smoke-2026-09-01.md, with public response "
        "hashes in growth/quality/google-play-public-propagation-2026-09-01.md and the "
        "current cross-store state in growth/quality/store-release-recheck-2026-09-01.md."
    )
    verdict = blocks[0].get("body")
    if not isinstance(verdict, str):
        raise ValueError("dashboard verdict body is malformed")
    rank_summary = (
        "Nimbo is **not ready to scale acquisition**. The canonical "
        f"{rank_date} capture at {captured_at} fails every required category surface, "
        f"so the verified streak remains {top10_goal['current_streak_days']}/"
        f"{top10_goal['required_days']}: Apple weather search is {weather_rank}, "
        f"the official Apple Weather chart is #{category_rank}, all three fixed "
        "logged-out Google category profiles are outside the first 30, and "
        f"{qualifying_queries}/{query_count} generic Google queries meet the "
        "diagnostic benchmark. The "
        "auxiliary Apple Toshkent ob-havo search returned only one unique result "
        "and remains a non-goal diagnostic error; required goal evidence is "
        "complete. The current App Store Connect overview reports 300 impressions, "
        "23 product-page views, 8 first downloads, 1 redownload, 3 updates, and "
        "4.86% conversion; retention is insufficient. The conversion is preserved "
        "as reported because the supplied counts and report window do not reproduce "
        f"it. A separate public Apple UZ lookup reports {apple_ratings} rating at "
        f"{apple_average_rating:.1f} while public version 1.0.1 remains live. Public "
        "iOS 1.0.1 (4) has three consented crashes in the current 30-day and "
        "90-day App Store Connect Analytics windows. The seven-day August 26 "
        "through September 1 window contains two, on August 29 and August 30. "
        "No diagnostic, stack, incident/signature ID, crashed-process identity, "
        "binary UUID, or source-defined crash-free-session percentage is exposed. "
        "The crash gate therefore "
        "remains blocked. Google Play's global last-28-days dashboard counts were "
        f"revalidated on August 31 at {installations} installs, {first_launches} "
        f"device first launches, and {monthly_active_devices} monthly active devices; "
        "listing impressions, conversion, and ratings remain carried forward where "
        "marked."
    )
    verdict, rank_summary_count = re.subn(
        r"## Current verdict\n\n.*?\n\nCurrent product/build-input commit",
        "## Current verdict\n\n" + rank_summary + "\n\nCurrent product/build-input commit",
        verdict,
        count=1,
        flags=re.DOTALL,
    )
    if rank_summary_count != 1:
        raise ValueError("dashboard verdict rank summary is missing")
    current_summary = (
        "Current product/build-input commit "
        + current_revision
        + " is governed by the canonical fail-closed release registry. "
        + gates["release_artifact_source_sync"]["reason"]
        + " All predecessor artifacts and observations are historical and "
        "non-transferable."
    )
    current_pattern = re.compile(
        r"Current product/build-input commit [0-9a-f]{40} .*?"
        r"(?:All predecessor artifacts and observations|all of their binaries, screenshots, "
        r"and device results) are historical and non-transferable\.",
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
        "present. Historical protected run 33381050098 used all 8/8 signing "
        "inputs, but replacement vc9/vc1000009/build-7 signing is pending.",
    )
    verdict = verdict.replace(
        "There is no exact-current signed phone/Wear artifact, distribution-"
        "signed Apple archive, iOS 15 runtime pass, or matching physical matrix.",
        "Replacement vc9/vc1000009/build-7 artifacts are not signed or byte "
        "verified; predecessor store artifacts are historical, and there is no "
        "iOS 15 runtime pass or matching physical matrix.",
    )
    verdict = verdict.replace(
        "There is no retained, accepted, byte-verified exact-current signed "
        "phone/Wear artifact or distribution-signed Apple archive, and no iOS "
        "15 runtime pass or matching physical matrix.",
        "Replacement vc9/vc1000009/build-7 artifacts are not signed or byte "
        "verified; predecessor store artifacts are historical, and there is no "
        "iOS 15 runtime pass or matching physical matrix.",
    )
    verdict = verdict.replace(
        "Android Keychain metadata and the existing mode-600 keystore remain "
        "present. The protected environment now contains all 8/8 signing "
        "inputs, but neither candidate run yielded a retained, byte-verified "
        "package; hosted proof of the current correction remains pending.",
        "Android Keychain metadata and the existing mode-600 keystore remain "
        "present. Historical protected run 33381050098 used all 8/8 signing "
        "inputs, but replacement vc9/vc1000009/build-7 signing is pending.",
    )
    verdict = verdict.replace(
        "At 20:44 +05:00 the iPad was paired but not action-ready; the iPhone "
        "and watch remained unavailable.",
        "At the September 1 read-only device check, the iPhone 14 Pro was unavailable "
        "and the paired iPad mini 5 was locked, so app inventory and TestFlight install "
        "proof could not be collected. The paired Series 5 watch was compatible, but "
        "Developer Mode was disabled and its developer tunnel disconnected.",
    )
    verdict = verdict.replace(
        "Scale status remains hold; public outreach and acquisition scaling "
        "remain gated on crash diagnosis, source-synced signed phone, Wear OS, "
        "and Apple artifacts, complete physical-device coverage, and critical "
        "console guardrails.",
        "Scale status remains hold; public outreach and acquisition scaling "
        "remain gated on crash diagnosis, protected signing and independent "
        "verification of the replacement set, complete physical-device and store-"
        "delivery coverage, and critical console guardrails.",
    )
    verdict = verdict.replace(
        "Scale status remains hold; public outreach and acquisition scaling "
        "remain gated on crash diagnosis, durable manifest promotion of the "
        "retained candidates, complete physical-device coverage, and critical "
        "console guardrails.",
        "Scale status remains hold; public outreach and acquisition scaling "
        "remain gated on crash diagnosis, protected signing and independent "
        "verification of the replacement set, complete physical-device and store-"
        "delivery coverage, and critical console guardrails.",
    )
    verdict = verdict.replace(
        "Scale status remains hold; public outreach and acquisition scaling "
        "remain gated on crash diagnosis, full trusted macOS verification and "
        "atomic manifest promotion of the materialized candidates, complete "
        "physical-device coverage, and critical console guardrails.",
        "Scale status remains hold; public outreach and acquisition scaling "
        "remain gated on crash diagnosis, protected signing and independent "
        "verification of the replacement set, complete physical-device and store-"
        "delivery coverage, and critical console guardrails.",
    )
    verdict = verdict.replace(
        "Exact-current signed phone/Wear and Apple candidates are retained, "
        "byte-verified, manifest-promoted, and accepted into their internal store "
        "channels; there is no iOS 15 runtime pass or matching physical matrix.",
        "Replacement vc9/vc1000009/build-7 artifacts are not signed or byte "
        "verified; predecessor store artifacts are historical, and there is no "
        "iOS 15 runtime pass or matching physical matrix.",
    )
    verdict = verdict.replace(
        "Android Keychain metadata and the existing mode-600 keystore remain "
        "present. Protected run 33381050098 used all 8/8 signing inputs and "
        "yielded a retained, independently byte-verified package; manifest "
        "promotion and physical delivery remain separate.",
        "Android Keychain metadata and the existing mode-600 keystore remain "
        "present. Historical protected run 33381050098 used all 8/8 signing "
        "inputs, but replacement vc9/vc1000009/build-7 signing is pending.",
    )
    verdict = verdict.replace(
        "Authenticated App Store Connect relationship inventory now exposes exact "
        "build 6 as VALID and APP_STORE_ELIGIBLE, uploaded at 2026-08-31 21:47:14 "
        "Asia/Tashkent. Direct prerelease/TestFlight-detail GETs remain permission-"
        "blocked with security 403. The earlier bounded POST attempting to create "
        "only a manual-release 1.1.0 version also returned 403, and no version or "
        "localization draft was created. No localization, screenshot, Custom Product "
        "Page, production submission, or release mutation followed.",
        "Authenticated App Store Connect relationship inventory exposes historical "
        "build 6 as VALID and APP_STORE_ELIGIBLE; replacement build 7 is not signed "
        "or delivered. Direct prerelease/TestFlight-detail GETs remain permission-"
        "blocked with security 403. No production submission or release followed.",
    )
    verdict = verdict.replace(
        "Scale status remains hold; public outreach and acquisition scaling remain "
        "gated on crash diagnosis, complete physical-device and internal-delivery "
        "coverage, and critical console guardrails. The hosted full-byte repeat "
        "passes; its chain must still recheck the mutable draft before every later use.",
        "Scale status remains hold; public outreach and acquisition scaling remain "
        "gated on crash diagnosis, protected signing and independent verification "
        "of the replacement set, complete physical-device and store-delivery "
        "coverage, and critical console guardrails.",
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
        "Replacement vc9/vc1000009/build-7 candidates are protected-signed, "
        "independently byte-verified, and manifest-current but not store-delivered; "
        "predecessor store candidates remain historical;",
    )
    verdict = verdict.replace(
        "Exact-current signed phone/Wear and Apple candidates are retained, "
        "byte-verified, and manifest-promoted, but not store-delivered;",
        "Replacement vc9/vc1000009/build-7 candidates are protected-signed, "
        "independently byte-verified, and manifest-current but not store-delivered; "
        "predecessor store candidates remain historical;",
    )
    verdict = verdict.replace(
        "At the August 31 read-only device check, the iPad mini 5 was paired, "
        "unlocked, and DDI-ready with Nimbo absent; the iPhone 14 Pro was paired "
        "but locked/DDI-blocked, and the paired Series 5 watch was visible but "
        "offline for detail/app queries.",
        "At the September 1 read-only device check, the iPhone 14 Pro was unavailable "
        "and the paired iPad mini 5 was locked, so app inventory and TestFlight install "
        "proof could not be collected. The paired Series 5 watch was compatible, but "
        "Developer Mode was disabled and its developer tunnel disconnected.",
    )
    verdict = verdict.replace(
        "At the August 31 read-only device check, the iPhone 14 Pro and iPad mini 5 "
        "were paired, booted, and Developer Mode enabled; the iPad had no Nimbo "
        "install. The paired Series 5 watch was compatible, but Developer Mode was "
        "disabled and its developer tunnel disconnected.",
        "At the September 1 read-only device check, the iPhone 14 Pro was unavailable "
        "and the paired iPad mini 5 was locked, so app inventory and TestFlight install "
        "proof could not be collected. The paired Series 5 watch was compatible, but "
        "Developer Mode was disabled and its developer tunnel disconnected.",
    )
    verdict = verdict.replace(
        "Authenticated App Store Connect inventory reads expose public iOS 1.0.1 "
        "with valid build 4 and no 1.1.0 version or builds 5/6. Build-detail and "
        "diagnostic-signature GETs for build 4 returned security 403. One bounded "
        "POST attempting to create only a manual-release 1.1.0 version also "
        "returned 403; the final authenticated GET again returned zero 1.1.0 "
        "versions, proving that no partial version or localization draft was "
        "created. No build, localization, screenshot, Custom Product Page, "
        "submission, or release mutation followed.",
        "Authenticated App Store Connect relationship inventory exposes historical "
        "build 6 as VALID and APP_STORE_ELIGIBLE, uploaded at 2026-08-31 21:47:14 "
        "Asia/Tashkent; replacement build 7 is not signed or delivered. Direct "
        "prerelease/TestFlight-detail GETs remain permission-blocked with security "
        "403. No localization, screenshot, Custom Product Page, production "
        "submission, or release mutation followed.",
    )
    verdict = verdict.replace(
        "Google overview values are carried forward from August 28 and were not "
        "revalidated on August 31.",
        f"Google Play's global last-28-days dashboard counts were revalidated on "
        f"August 31 at {installations} installs, {first_launches} device first "
        f"launches, and {monthly_active_devices} monthly active devices; listing "
        "impressions, conversion, and ratings remain carried forward where marked.",
    )
    verdict = verdict.replace(
        "Google Play Custom Store Listing 4834799756935529888 remains an "
        "Uzbekistan-only draft.",
        "Google Play Custom Store Listing 4834799756935529888 is under review in "
        "request 14 with en-US and ru-RU store data; approval, publication, and "
        "propagation are not verified. A fixed logged-out gl=UZ recheck at the "
        "2026-09-01 05:05 +05:00 checkpoint still exposed the pre-review public title Nimbo in "
        "both Uzbek and Russian product pages.",
    )
    verdict = verdict.replace(
        "Replacement vc9/vc1000009/build-7 artifacts are not signed or byte "
        "verified; predecessor store artifacts are historical, and there is no "
        "iOS 15 runtime pass or matching physical matrix.",
        "Replacement vc9/vc1000009/build-7 artifacts are protected-signed and "
        "independently byte-verified but not store-delivered; predecessor store "
        "artifacts are historical, and there is no iOS 15 runtime pass or matching "
        "physical matrix.",
    ).replace(
        "Historical protected run 33381050098 used all 8/8 signing inputs, but "
        "replacement vc9/vc1000009/build-7 signing is pending.",
        "Protected run 33473684554 produced the replacement "
        "vc9/vc1000009/build-7 signed set and independent full-byte verification "
        "matched all three identities.",
    ).replace(
        "replacement build 7 is not signed or delivered",
        "replacement build 7 is signed and byte-verified but not delivered",
    ).replace(
        "protected signing and independent verification of the replacement set, "
        "complete physical-device and store-delivery coverage",
        "complete replacement physical-device and store-delivery coverage",
    )
    release_authority = (
        "Canonical release authority remains fail-closed. "
        + gates["release_artifact_source_sync"]["reason"]
        + " "
        + gates["android_physical_smoke"]["reason"]
        + " "
        + gates["ios_physical_smoke"]["reason"]
        + " No production submission or release followed."
    )
    verdict, release_authority_count = re.subn(
        r"(?:Canonical release authority remains fail-closed\.|"
        r"Replacement vc9/vc1000009/build-7 artifacts|Exact-current signed phone/Wear).*?"
        r"No production submission or release followed\.",
        release_authority,
        verdict,
        count=1,
        flags=re.DOTALL,
    )
    if release_authority_count != 1:
        raise ValueError("dashboard verdict release-authority section is missing")
    verdict = re.sub(
        r"Scale status remains hold; public outreach and acquisition scaling remain gated on .*?"
        r"critical console guardrails\.",
        "Scale status remains hold; public outreach and acquisition scaling remain "
        "gated on every blocking canonical quality gate and critical console guardrail.",
        verdict,
        count=1,
        flags=re.DOTALL,
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
    parser.add_argument("--rank", type=Path, default=DEFAULT_RANK)
    parser.add_argument("--rank-sql", type=Path, default=DEFAULT_RANK_SQL)
    parser.add_argument("--framework", type=Path, default=DEFAULT_FRAMEWORK)
    parser.add_argument("--generated-at", required=True)
    arguments = parser.parse_args()
    sync(
        arguments.artifact,
        arguments.gate_sql,
        arguments.gates,
        arguments.evaluation,
        arguments.generated_at,
        rank_path=arguments.rank,
        rank_sql_path=arguments.rank_sql,
        framework_path=arguments.framework,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
