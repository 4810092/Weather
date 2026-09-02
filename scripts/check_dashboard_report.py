#!/usr/bin/env python3
"""Verify that the portable growth dashboard embeds the canonical artifact."""

from __future__ import annotations

import argparse
import base64
import binascii
import gzip
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

try:
    from scripts.growth.sync_dashboard_report_payload import (
        DashboardPayloadSyncError,
        FALLBACK_ID,
        render_static_fallback,
    )
except ModuleNotFoundError:  # Direct execution with scripts/ on sys.path.
    from growth.sync_dashboard_report_payload import (
        DashboardPayloadSyncError,
        FALLBACK_ID,
        render_static_fallback,
    )


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = REPO_ROOT / "growth/dashboard/artifact.json"
DEFAULT_REPORT = REPO_ROOT / "growth/dashboard/report.html"
PAYLOAD_TEMPLATE_ID = "data-analytics-portable-artifact-payload-source"
CANONICAL_KEYS = ("surface", "manifest", "snapshot", "sources")
EXPECTED_SOURCE_PATHS = {
    "baseline_snapshot": "growth/dashboard/baseline_snapshot.sql",
    "driver_comparison": "growth/dashboard/driver_comparison.sql",
    "rank_snapshot": "growth/dashboard/rank_snapshot.sql",
    "evaluation_snapshot": "growth/reports/evaluation-2026-09-01.json",
    "gate_snapshot": "growth/dashboard/gate_snapshot.sql",
    "quality_guardrail_snapshot": "growth/dashboard/guardrail_snapshot.sql",
}
BACKING_JSON_PATHS = {
    "baseline": "growth/baseline/2026-08-31.json",
    "rank": "growth/data/public-rank/2026-09-01.json",
    "evaluation": "growth/reports/evaluation-2026-09-01.json",
    "framework": "growth/kpi-framework.json",
    "gates": "growth/quality/gates.json",
}


class DashboardConsistencyError(ValueError):
    """The rendered report cannot be proven to represent its JSON source."""


class _PayloadParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.active = False
        self.count = 0
        self.compression: str | None = None
        self.parts: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        if tag == "template" and attributes.get("id") == PAYLOAD_TEMPLATE_ID:
            self.active = True
            self.count += 1
            self.compression = attributes.get("data-compression")

    def handle_endtag(self, tag: str) -> None:
        if tag == "template" and self.active:
            self.active = False

    def handle_data(self, data: str) -> None:
        if self.active:
            self.parts.append(data)


def embedded_artifact_payload(report: Path) -> dict[str, Any]:
    parser = _PayloadParser()
    try:
        parser.feed(report.read_text(encoding="utf-8"))
        parser.close()
    except (OSError, UnicodeError) as error:
        raise DashboardConsistencyError(f"cannot read dashboard report: {error}") from error
    if parser.count != 1:
        raise DashboardConsistencyError(
            f"dashboard report must contain exactly one {PAYLOAD_TEMPLATE_ID!r} template"
        )
    if parser.compression != "gzip-base64":
        raise DashboardConsistencyError(
            "dashboard payload must declare data-compression=gzip-base64"
        )
    encoded = "".join("".join(parser.parts).split())
    try:
        compressed = base64.b64decode(encoded, validate=True)
        decoded = gzip.decompress(compressed).decode("utf-8")
        payload = json.loads(decoded)
    except (binascii.Error, gzip.BadGzipFile, OSError, UnicodeError, json.JSONDecodeError) as error:
        raise DashboardConsistencyError(
            f"dashboard payload cannot be decoded and parsed: {error}"
        ) from error
    if not isinstance(payload, dict):
        raise DashboardConsistencyError("dashboard payload must be a JSON object")
    return payload


def static_fallback(report: Path) -> str:
    try:
        source = report.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise DashboardConsistencyError(f"cannot read dashboard report: {error}") from error
    opening = f'<main id="{FALLBACK_ID}"'
    if source.count(opening) != 1:
        raise DashboardConsistencyError(
            f"dashboard report must contain exactly one {FALLBACK_ID!r} main"
        )
    start = source.index(opening)
    end = source.find("</main>", start)
    if end < 0:
        raise DashboardConsistencyError("dashboard static fallback main is not closed")
    return source[start : end + len("</main>")]


def _repo_file(repo_root: Path, relative: str) -> Path:
    relative_path = Path(relative)
    if relative_path.is_absolute():
        raise DashboardConsistencyError(
            f"dashboard source path must be repository-relative: {relative!r}"
        )
    root = repo_root.resolve()
    candidate = (root / relative_path).resolve()
    if not candidate.is_relative_to(root):
        raise DashboardConsistencyError(
            f"dashboard source path escapes repository root: {relative!r}"
        )
    if not candidate.is_file():
        raise DashboardConsistencyError(
            f"dashboard source file does not exist: {relative}"
        )
    return candidate


def _load_json_object(repo_root: Path, relative: str) -> dict[str, Any]:
    path = _repo_file(repo_root, relative)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise DashboardConsistencyError(
            f"cannot read dashboard backing source {relative}: {error}"
        ) from error
    if not isinstance(payload, dict):
        raise DashboardConsistencyError(
            f"dashboard backing source must be a JSON object: {relative}"
        )
    return payload


def _normalize_sql(sql: str) -> str:
    """Remove SQL layout/comments without changing quoted string values."""
    output: list[str] = []
    index = 0
    quoted = False
    line_comment = False
    while index < len(sql):
        character = sql[index]
        following = sql[index + 1] if index + 1 < len(sql) else ""
        if line_comment:
            if character in "\r\n":
                line_comment = False
            index += 1
            continue
        if quoted:
            output.append(character)
            if character == "'":
                if following == "'":
                    output.append(following)
                    index += 2
                    continue
                quoted = False
            index += 1
            continue
        if character == "'":
            quoted = True
            output.append(character)
            index += 1
            continue
        if character == "-" and following == "-":
            line_comment = True
            index += 2
            continue
        if not character.isspace():
            output.append(character)
        index += 1
    if quoted:
        raise DashboardConsistencyError("dashboard SQL contains an unclosed quote")
    return "".join(output).rstrip(";")


def _records_by_id(
    rows: object,
    identifier_field: str,
    dataset_name: str,
) -> dict[str, dict[str, Any]]:
    if not isinstance(rows, list):
        raise DashboardConsistencyError(
            f"dashboard dataset {dataset_name!r} must be a list"
        )
    records: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise DashboardConsistencyError(
                f"dashboard dataset {dataset_name!r} contains a non-object row"
            )
        identifier = row.get(identifier_field)
        if not isinstance(identifier, str) or not identifier or identifier in records:
            raise DashboardConsistencyError(
                f"dashboard dataset {dataset_name!r} has invalid or duplicate "
                f"{identifier_field!r}"
            )
        records[identifier] = row
    return records


def _observed_rank(surface: dict[str, Any]) -> str:
    rank = surface.get("target_rank")
    bound = surface.get("target_rank_bound")
    if isinstance(rank, int) and rank > 0 and bound is None:
        return str(rank)
    if rank is None and isinstance(bound, str) and bound.startswith(">"):
        return bound
    raise DashboardConsistencyError(
        f"rank source {surface.get('surface_id')!r} has no usable target observation"
    )


def _threshold_text(identifier: str, operator: str, threshold: object) -> str:
    symbols = {">=": "≥", "<=": "≤", "==": "=", "<": "<", ">": ">"}
    symbol = symbols.get(operator)
    if symbol is None or not isinstance(threshold, (int, float)):
        raise DashboardConsistencyError(
            f"guardrail {identifier!r} has an unsupported threshold definition"
        )
    numeric = f"{threshold:g}"
    suffix = "%" if identifier.endswith("_pct") else ""
    return f"{symbol} {numeric}{suffix}"


def _verify_source_registry(
    artifact: dict[str, Any], repo_root: Path
) -> dict[str, dict[str, Any]]:
    manifest = artifact.get("manifest")
    if not isinstance(manifest, dict):
        raise DashboardConsistencyError("dashboard manifest must be an object")
    summary_rows = manifest.get("sources", [])
    detail_rows = artifact.get("sources", [])
    if not summary_rows and not detail_rows:
        return {}
    summary = _records_by_id(summary_rows, "id", "manifest.sources")
    detailed = _records_by_id(detail_rows, "id", "sources")
    if set(summary) != set(EXPECTED_SOURCE_PATHS) or set(detailed) != set(
        EXPECTED_SOURCE_PATHS
    ):
        raise DashboardConsistencyError(
            "dashboard source registry differs from the required cited input set"
        )
    for source_id, expected_path in EXPECTED_SOURCE_PATHS.items():
        summary_source = summary[source_id]
        detailed_source = detailed[source_id]
        for field in ("label", "path"):
            if summary_source.get(field) != detailed_source.get(field):
                raise DashboardConsistencyError(
                    f"dashboard source {source_id!r} has inconsistent {field} metadata"
                )
        if detailed_source.get("path") != expected_path:
            raise DashboardConsistencyError(
                f"dashboard source {source_id!r} must cite {expected_path}"
            )
        source_file = _repo_file(repo_root, expected_path)
        if source_file.suffix == ".sql":
            query = detailed_source.get("query")
            query_sql = query.get("sql") if isinstance(query, dict) else None
            if not isinstance(query_sql, str) or _normalize_sql(
                query_sql
            ) != _normalize_sql(source_file.read_text(encoding="utf-8")):
                raise DashboardConsistencyError(
                    f"dashboard source {source_id!r} SQL differs from {expected_path}"
                )

    referenced: set[str] = set()
    for section in ("cards", "charts", "tables", "blocks"):
        items = manifest.get(section, [])
        if not isinstance(items, list):
            raise DashboardConsistencyError(
                f"dashboard manifest section {section!r} must be a list"
            )
        for item in items:
            if not isinstance(item, dict):
                raise DashboardConsistencyError(
                    f"dashboard manifest section {section!r} contains a non-object"
                )
            source_id = item.get("sourceId")
            if source_id is not None:
                if not isinstance(source_id, str) or source_id not in detailed:
                    raise DashboardConsistencyError(
                        f"dashboard manifest references unknown source {source_id!r}"
                    )
                referenced.add(source_id)
    if referenced != set(detailed):
        raise DashboardConsistencyError(
            "dashboard source registry contains uncited or unregistered inputs"
        )
    return detailed


def _verify_baseline_and_driver_parity(
    datasets: dict[str, Any], baseline: dict[str, Any], framework: dict[str, Any]
) -> None:
    try:
        apple = baseline["platforms"]["apple"]["metrics"]
        google = baseline["platforms"]["google"]["metrics"]
        driver_definitions = {
            row["id"]: row for row in framework["drivers"]
        }
    except (KeyError, TypeError) as error:
        raise DashboardConsistencyError(
            f"baseline/framework source schema is incomplete: {error}"
        ) from error

    google_monthly_active_metric = (
        "Monthly active devices"
        if google.get("monthly_active_users_label") == "monthly_active_devices"
        else "Monthly active users"
    )
    baseline_expected = {
        "App Store · Impressions": ("App Store", "Impressions", str(apple["reported_impressions"])),
        "App Store · First-time downloads": ("App Store", "First-time downloads", str(apple["first_time_downloads"])),
        "App Store · Conversion rate": ("App Store", "Conversion rate", f"{apple['reported_conversion_rate_pct']:.2f}%"),
        "App Store · Ratings": ("App Store", "Ratings", str(apple["ratings_count"])),
        "App Store · Crashes": ("App Store", "Crashes", str(apple["reported_crashes"])),
        "Google Play · Impressions": ("Google Play", "Impressions", str(google["reported_impressions"])),
        "Google Play · Installations": ("Google Play", "Installations", str(google["installations"])),
        "Google Play · First launches": ("Google Play", "First launches", str(google["first_launches"])),
        f"Google Play · {google_monthly_active_metric}": (
            "Google Play",
            google_monthly_active_metric,
            str(google["monthly_active_users"]),
        ),
        "Google Play · Conversion rate": ("Google Play", "Conversion rate", f"{google['reported_conversion_rate_pct']:.2f}%"),
        "Google Play · Ratings": ("Google Play", "Ratings", str(google["reported_ratings_count_from_plan"])),
    }
    baseline_rows = _records_by_id(
        datasets.get("platform_baseline"), "metric_label", "platform_baseline"
    )
    if set(baseline_rows) != set(baseline_expected):
        raise DashboardConsistencyError(
            "dashboard platform_baseline rows differ from the baseline source"
        )
    for label, expected in baseline_expected.items():
        actual = baseline_rows[label]
        if (actual.get("platform"), actual.get("metric"), actual.get("value")) != expected:
            raise DashboardConsistencyError(
                f"dashboard platform_baseline value differs for {label!r}"
            )

    first_launch_rate = round(google["first_launches"] / google["installations"], 4)
    expected_driver_rows = [
        {"metric": "Apple conversion", "series": "Baseline", "rate": round(apple["reported_conversion_rate_pct"] / 100, 4)},
        {"metric": "Apple conversion", "series": "Target", "rate": driver_definitions["apple_conversion_rate_pct"]["target"] / 100},
        {"metric": "Play conversion", "series": "Baseline", "rate": round(google["reported_conversion_rate_pct"] / 100, 4)},
        {"metric": "Play conversion", "series": "Target", "rate": driver_definitions["google_store_listing_ctr_pct"]["target"] / 100},
        {"metric": "First launch / install", "series": "Baseline", "rate": first_launch_rate},
        {"metric": "First launch / install", "series": "Target", "rate": driver_definitions["first_launch_rate_pct"]["target"] / 100},
    ]
    if datasets.get("driver_comparison") != expected_driver_rows:
        raise DashboardConsistencyError(
            "dashboard driver_comparison differs from baseline/framework sources"
        )


def _verify_rank_parity(
    datasets: dict[str, Any], rank: dict[str, Any], framework: dict[str, Any]
) -> None:
    try:
        requirements = framework["primary_goal"]["daily_requirements"]
        apple = rank["surfaces"]["apple"]
        google = rank["surfaces"]["google"]
        evaluation = rank["evaluation"]
        profiles = requirements["google_required_profiles"]
        rank_target = requirements["apple_weather_chart_rank_lte"]
        diagnostics = framework["primary_goal"]["diagnostic_requirements"]
        generic_target = diagnostics["generic_queries_required"]
        quorum = diagnostics["generic_query_profile_quorum"]
    except (KeyError, TypeError) as error:
        raise DashboardConsistencyError(
            f"rank/framework source schema is incomplete: {error}"
        ) from error
    if (
        rank.get("date") != "2026-09-01"
        or rank.get("goal_evidence_complete") is not True
        or not evaluation.get("complete")
    ):
        raise DashboardConsistencyError(
            "dashboard rank source must be the complete 2026-09-01 goal snapshot"
        )
    weather_rank = _observed_rank(apple["search"]["weather"])
    category_rank = _observed_rank(apple["category"])
    expected_rows = [
        {"check": "App Store search · weather", "result": f"{weather_rank} · target ≤{rank_target}", "surface": "App Store UZ search", "profile": "all", "query": "weather", "observed_rank": weather_rank, "target_rank": rank_target, "evidence_class": "fixed_public_capture"},
        {"check": "App Store · Weather chart", "result": f"{category_rank} · target ≤{rank_target}", "surface": "App Store UZ Weather chart", "profile": "official", "query": "category", "observed_rank": category_rank, "target_rank": rank_target, "evidence_class": "fixed_public_capture"},
    ]
    for profile in profiles:
        observed = _observed_rank(google["category"][profile])
        expected_rows.append(
            {"check": f"Google category · {profile}", "result": f"{observed} · target ≤{requirements['google_weather_category_rank_lte']}", "surface": "Google Play UZ Weather category", "profile": profile, "query": "category", "observed_rank": observed, "target_rank": requirements["google_weather_category_rank_lte"], "evidence_class": "fixed_logged_out_capture"}
        )
    query_ids = set(google["search"][profiles[0]])
    if any(set(google["search"][profile]) != query_ids for profile in profiles):
        raise DashboardConsistencyError(
            "rank source profiles do not use one fixed generic-query set"
        )
    query_count = len(query_ids)
    qualifying = evaluation["google_generic_top10_query_count"]
    number_words = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}
    query_label = f"{number_words.get(query_count, query_count)} configured queries"
    expected_rows.append(
        {"check": "Google generic-query diagnostic", "result": f"{qualifying}/{query_count} qualify · diagnostic benchmark ≥{generic_target}", "surface": "Google Play UZ generic-query diagnostic", "profile": f"{quorum}-of-{len(profiles)} profiles", "query": query_label, "observed_rank": f"{qualifying} qualifying queries", "target_rank": generic_target, "evidence_class": "fixed_logged_out_capture"}
    )
    if datasets.get("rank_snapshot") != expected_rows:
        raise DashboardConsistencyError(
            "dashboard rank_snapshot differs from the fixed public-rank source"
        )


def _verify_evaluation_and_gate_parity(
    datasets: dict[str, Any],
    evaluation: dict[str, Any],
    framework: dict[str, Any],
    gates: dict[str, Any],
) -> None:
    try:
        source_gates = gates["gates"]
        evaluated_gates = {
            row["id"]: row for row in evaluation["guardrails"]["scale_gates"]
        }
        framework_gate_ids = {
            row["id"] for row in framework["scale_gates"]
        }
        top10_goal = evaluation["top10_goal"]
    except (KeyError, TypeError) as error:
        raise DashboardConsistencyError(
            f"evaluation/gate source schema is incomplete: {error}"
        ) from error
    if set(source_gates) != framework_gate_ids or set(source_gates) != set(
        evaluated_gates
    ):
        raise DashboardConsistencyError(
            "operational gate IDs differ across registry, framework, and evaluation"
        )
    dashboard_gates = _records_by_id(
        datasets.get("gate_snapshot"), "gate_id", "gate_snapshot"
    )
    if set(dashboard_gates) != set(source_gates):
        raise DashboardConsistencyError(
            "dashboard gate_snapshot IDs differ from the operational gate registry"
        )
    for gate_id, source_gate in source_gates.items():
        if not isinstance(source_gate, dict) or not isinstance(
            source_gate.get("blocks_publication"), bool
        ):
            raise DashboardConsistencyError(
                f"operational gate {gate_id!r} lacks blocks_publication metadata"
            )
        dashboard_gate = dashboard_gates[gate_id]
        evaluated_gate = evaluated_gates[gate_id]
        if (
            dashboard_gate.get("status") != source_gate.get("status")
            or dashboard_gate.get("evidence") != source_gate.get("reason")
            or evaluated_gate.get("actual") != source_gate.get("status")
            or evaluated_gate.get("reason") != source_gate.get("reason")
        ):
            raise DashboardConsistencyError(
                f"dashboard/evaluation gate state differs for {gate_id!r}"
            )

    framework_guardrails = {
        row["id"]: row for row in framework["guardrails"]
    }
    evaluated_guardrails = {
        row["id"]: row
        for row in evaluation["guardrails"]["metric_guardrails"]
    }
    if set(framework_guardrails) != set(evaluated_guardrails):
        raise DashboardConsistencyError(
            "metric guardrail IDs differ between framework and evaluation"
        )
    critical_ids = {
        identifier
        for identifier, definition in framework_guardrails.items()
        if definition.get("critical") is True
    }
    dashboard_guardrails = _records_by_id(
        datasets.get("quality_guardrails"),
        "guardrail_id",
        "quality_guardrails",
    )
    if set(dashboard_guardrails) != critical_ids:
        raise DashboardConsistencyError(
            "dashboard quality_guardrails must expose every critical metric guardrail"
        )
    for guardrail_id in critical_ids:
        definition = framework_guardrails[guardrail_id]
        evaluated = evaluated_guardrails[guardrail_id]
        dashboard = dashboard_guardrails[guardrail_id]
        expected_threshold = _threshold_text(
            guardrail_id, definition["operator"], definition["threshold"]
        )
        expected = (
            evaluated.get("status"),
            definition.get("critical"),
            definition.get("unknown_policy"),
            expected_threshold,
        )
        actual = (
            dashboard.get("status"),
            dashboard.get("critical"),
            dashboard.get("unknown_policy"),
            dashboard.get("threshold"),
        )
        framework_projection = (
            evaluated.get("operator"),
            evaluated.get("threshold"),
            evaluated.get("critical"),
            evaluated.get("unknown_policy"),
        )
        expected_projection = (
            definition.get("operator"),
            definition.get("threshold"),
            definition.get("critical"),
            definition.get("unknown_policy"),
        )
        if actual != expected or framework_projection != expected_projection:
            raise DashboardConsistencyError(
                f"dashboard/evaluation guardrail state differs for {guardrail_id!r}"
            )

    if (
        "store_policy_console_clearance" not in source_gates
        or "open_policy_issues" not in framework_guardrails
    ):
        raise DashboardConsistencyError(
            "operational policy gate and app-global policy metric must use distinct IDs"
        )

    headline_rows = datasets.get("headline_metrics")
    if not isinstance(headline_rows, list) or len(headline_rows) != 1:
        raise DashboardConsistencyError(
            "dashboard headline_metrics must contain exactly one row"
        )
    headline = headline_rows[0]
    if not isinstance(headline, dict):
        raise DashboardConsistencyError("dashboard headline_metrics row must be an object")
    if (
        headline.get("top10_streak_days") != top10_goal.get("current_streak_days")
        or headline.get("top10_streak_target") != top10_goal.get("required_days")
    ):
        raise DashboardConsistencyError(
            "dashboard Top-10 headline differs from the evaluation source"
        )


def verify_dashboard_sources(
    artifact: dict[str, Any], *, repo_root: Path = REPO_ROOT
) -> None:
    """Prove the dashboard snapshot still matches every cited repository input."""
    sources = _verify_source_registry(artifact, repo_root)
    if not sources:
        return
    snapshot = artifact.get("snapshot")
    datasets = snapshot.get("datasets") if isinstance(snapshot, dict) else None
    if not isinstance(datasets, dict):
        raise DashboardConsistencyError("dashboard snapshot.datasets must be an object")
    baseline = _load_json_object(repo_root, BACKING_JSON_PATHS["baseline"])
    rank = _load_json_object(repo_root, BACKING_JSON_PATHS["rank"])
    evaluation = _load_json_object(repo_root, BACKING_JSON_PATHS["evaluation"])
    framework = _load_json_object(repo_root, BACKING_JSON_PATHS["framework"])
    gates = _load_json_object(repo_root, BACKING_JSON_PATHS["gates"])
    _verify_baseline_and_driver_parity(datasets, baseline, framework)
    _verify_rank_parity(datasets, rank, framework)
    _verify_evaluation_and_gate_parity(datasets, evaluation, framework, gates)

    headline = datasets["headline_metrics"][0]
    apple_weather = _observed_rank(
        rank["surfaces"]["apple"]["search"]["weather"]
    )
    driver_definitions = {row["id"]: row for row in framework["drivers"]}
    apple_metrics = baseline["platforms"]["apple"]["metrics"]
    google_metrics = baseline["platforms"]["google"]["metrics"]
    expected_headline = {
        "top10_streak_days": evaluation["top10_goal"]["current_streak_days"],
        "top10_streak_target": evaluation["top10_goal"]["required_days"],
        "apple_weather_rank": apple_weather,
        "rank_target": framework["primary_goal"]["daily_requirements"]["apple_weather_chart_rank_lte"],
        "apple_conversion": round(apple_metrics["reported_conversion_rate_pct"] / 100, 4),
        "apple_conversion_target": driver_definitions["apple_conversion_rate_pct"]["target"] / 100,
        "play_conversion": round(google_metrics["reported_conversion_rate_pct"] / 100, 4),
        "play_conversion_target": driver_definitions["google_store_listing_ctr_pct"]["target"] / 100,
        "first_launch_rate": round(google_metrics["first_launches"] / google_metrics["installations"], 4),
        "first_launch_target": driver_definitions["first_launch_rate_pct"]["target"] / 100,
    }
    if headline != expected_headline:
        raise DashboardConsistencyError(
            "dashboard headline_metrics differs from cited baseline, rank, evaluation, or KPI sources"
        )


def verify_dashboard_report(
    artifact: Path,
    report: Path,
    *,
    repo_root: Path = REPO_ROOT,
) -> None:
    try:
        canonical = json.loads(artifact.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise DashboardConsistencyError(f"cannot read dashboard artifact: {error}") from error
    if not isinstance(canonical, dict):
        raise DashboardConsistencyError("dashboard artifact must be a JSON object")
    verify_dashboard_sources(canonical, repo_root=repo_root)
    embedded = embedded_artifact_payload(report)
    missing = [key for key in CANONICAL_KEYS if key not in canonical or key not in embedded]
    if missing:
        raise DashboardConsistencyError(
            f"dashboard artifact/report missing canonical sections: {', '.join(missing)}"
        )
    for key in CANONICAL_KEYS:
        if embedded[key] != canonical[key]:
            artifact_generated = canonical.get("manifest", {}).get("generatedAt")
            report_generated = embedded.get("manifest", {}).get("generatedAt")
            raise DashboardConsistencyError(
                f"dashboard report section {key!r} does not match artifact.json "
                f"(artifact generatedAt={artifact_generated!r}, "
                f"report generatedAt={report_generated!r}); regenerate report.html"
            )
    try:
        expected_fallback = render_static_fallback(canonical)
    except DashboardPayloadSyncError as error:
        raise DashboardConsistencyError(
            f"dashboard canonical fallback cannot be rendered: {error}"
        ) from error
    if static_fallback(report) != expected_fallback:
        raise DashboardConsistencyError(
            "dashboard static fallback does not match artifact.json; "
            "regenerate report.html"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> int:
    arguments = parse_args()
    try:
        verify_dashboard_report(arguments.artifact, arguments.report)
    except DashboardConsistencyError as error:
        print(f"Dashboard consistency check failed: {error}", file=sys.stderr)
        return 1
    print(
        "Dashboard consistency check passed: cited sources, artifact.json, "
        "embedded payload, and static fallback agree."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
