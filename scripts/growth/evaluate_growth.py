#!/usr/bin/env python3
"""Evaluate Top-10 streak, KPI evidence, guardrails, and the 90-day rule."""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.growth.common import (  # noqa: E402
    GROWTH_ROOT,
    MODEL_VITAL_METRICS,
    POLICY_METRICS,
    is_concrete_device,
    load_json,
    now_in,
    parse_date,
    write_json,
)


def _load_dated_json(directory: Path, as_of: date, date_field: str) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    if not directory.is_dir():
        return payloads
    for path in sorted(directory.glob("*.json")):
        payload = load_json(path)
        payload_date = parse_date(str(payload[date_field]))
        if payload_date <= as_of:
            payloads.append(payload)
    return sorted(payloads, key=lambda payload: payload[date_field])


def calculate_streak(
    snapshots: list[dict[str, Any]], as_of: date, required_days: int
) -> dict[str, Any]:
    by_date = {parse_date(snapshot["date"]): snapshot for snapshot in snapshots}
    current_streak = 0
    cursor = as_of
    current_fingerprint = (
        by_date[as_of].get("config_fingerprint") if as_of in by_date else None
    )
    if not isinstance(current_fingerprint, str) or not current_fingerprint:
        current_fingerprint = None
    while (
        current_fingerprint is not None
        and cursor in by_date
        and by_date[cursor].get("config_fingerprint") == current_fingerprint
        and by_date[cursor].get("evaluation", {}).get("status") == "pass"
    ):
        current_streak += 1
        cursor -= timedelta(days=1)

    max_streak = 0
    run = 0
    previous: date | None = None
    previous_fingerprint: str | None = None
    achieved_on: date | None = None
    achieved_fingerprint: str | None = None
    for snapshot_date in sorted(by_date):
        fingerprint = by_date[snapshot_date].get("config_fingerprint")
        passed = (
            isinstance(fingerprint, str)
            and bool(fingerprint)
            and by_date[snapshot_date].get("evaluation", {}).get("status") == "pass"
        )
        same_run = (
            previous is not None
            and snapshot_date == previous + timedelta(days=1)
            and fingerprint == previous_fingerprint
        )
        if passed and same_run:
            run += 1
        elif passed:
            run = 1
        else:
            run = 0
        max_streak = max(max_streak, run)
        if achieved_on is None and run >= required_days:
            achieved_on = snapshot_date
            achieved_fingerprint = fingerprint
        previous = snapshot_date
        previous_fingerprint = fingerprint if passed else None
    return {
        "as_of_snapshot_present": as_of in by_date,
        "current_config_fingerprint": current_fingerprint,
        "current_streak_days": current_streak,
        "max_streak_days": max_streak,
        "required_days": required_days,
        "goal_achieved": max_streak >= required_days,
        "first_achieved_on": achieved_on.isoformat() if achieved_on else None,
        "first_achieved_config_fingerprint": achieved_fingerprint,
    }


def _surface_rank(snapshot: dict[str, Any], surface_id: str) -> int | None:
    parts = surface_id.split(".")
    if parts[:3] == ["apple", "search", "weather"]:
        surface = snapshot["surfaces"]["apple"]["search"].get("weather", {})
    elif parts[:2] == ["apple", "category"]:
        surface = snapshot["surfaces"]["apple"].get("category", {})
    elif parts[:2] == ["google", "category"] and len(parts) == 3:
        surface = snapshot["surfaces"]["google"]["category"].get(parts[2], {})
    else:
        return None
    rank = surface.get("target_rank")
    return int(rank) if isinstance(rank, int) else None


def rank_improvements(snapshots: list[dict[str, Any]]) -> dict[str, Any]:
    if not snapshots:
        return {
            "config_fingerprint": None,
            "comparable_surfaces": [],
            "max_improvement": None,
            "caveat": "no public-rank snapshots",
        }
    fingerprint = snapshots[-1].get("config_fingerprint")
    comparable_snapshots = [
        snapshot
        for snapshot in snapshots
        if snapshot.get("config_fingerprint") == fingerprint
    ]
    surface_ids = [
        "apple.search.weather",
        "apple.category",
        "google.category.uz-UZ",
        "google.category.ru-UZ",
        "google.category.en-UZ",
    ]
    rows: list[dict[str, Any]] = []
    for surface_id in surface_ids:
        ranked = [
            (snapshot["date"], _surface_rank(snapshot, surface_id))
            for snapshot in comparable_snapshots
        ]
        ranked = [(day, rank) for day, rank in ranked if rank is not None]
        if len(ranked) < 2:
            continue
        baseline_day, baseline_rank = ranked[0]
        current_day, current_rank = ranked[-1]
        rows.append(
            {
                "surface_id": surface_id,
                "baseline_date": baseline_day,
                "baseline_rank": baseline_rank,
                "current_date": current_day,
                "current_rank": current_rank,
                "improvement": baseline_rank - current_rank,
            }
        )
    return {
        "config_fingerprint": fingerprint,
        "comparable_surfaces": rows,
        "max_improvement": max((row["improvement"] for row in rows), default=None),
        "caveat": "Only exact numeric ranks under the current config fingerprint are compared; bounded absences are not assigned a synthetic rank.",
    }


def _summary_metric_values(
    weekly: dict[str, Any] | None, metric: str, *, include_derived: bool = True
) -> list[float]:
    if weekly is None:
        return []
    candidates: list[dict[str, Any]] = list(weekly.get("records", []))
    if include_derived:
        candidates.extend(weekly.get("derived_metrics", []))
    return [
        float(record["value"])
        for record in candidates
        if record.get("metric") == metric
        and record.get("decision_eligible", True) is True
        and record.get("storefront") == "UZ"
        and record.get("source_scope") == "summary"
        and record.get("device") == "all"
        and record.get("app_version") == "all"
    ]


def _one_value(weekly: dict[str, Any] | None, metric: str) -> float | None:
    values = _summary_metric_values(weekly, metric)
    return values[0] if len(values) == 1 else None


def _guardrail_metric_values(
    weekly: dict[str, Any] | None, metric: str
) -> list[float]:
    if weekly is None:
        return []
    if metric in POLICY_METRICS:
        return [
            float(record["value"])
            for record in weekly.get("records", [])
            if record.get("metric") == metric
            and record.get("decision_eligible", True) is True
            and record.get("storefront") == "ALL"
            and record.get("source_scope") == "summary"
            and record.get("device") == "all"
            and record.get("app_version") == "all"
        ]
    if metric not in MODEL_VITAL_METRICS:
        return _summary_metric_values(weekly, metric, include_derived=False)
    return [
        float(record["value"])
        for record in weekly.get("records", [])
        if record.get("metric") == metric
        and record.get("decision_eligible", True) is True
        and record.get("storefront") == "UZ"
        and record.get("source_scope") == "device"
        and is_concrete_device(record.get("device"))
        and record.get("app_version") == "all"
    ]


def _driver_definitions(framework: dict[str, Any]) -> dict[str, dict[str, Any]]:
    definitions: dict[str, dict[str, Any]] = {}
    for definition in framework["drivers"]:
        identifier = definition["id"]
        if identifier in definitions:
            raise ValueError(f"duplicate driver definition {identifier}")
        definitions[identifier] = definition
    return definitions


def evaluate_drivers(
    weekly: dict[str, Any] | None, framework: dict[str, Any]
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    definitions = _driver_definitions(framework)

    def result_status(
        value: float | None,
        definition: dict[str, Any],
        *,
        sufficient: bool,
    ) -> str:
        if not sufficient or value is None:
            return "unknown"
        return (
            "pass"
            if _compare(
                value,
                str(definition["operator"]),
                float(definition["target"]),
            )
            else "fail"
        )

    def add_with_denominator(
        identifier: str,
        value_metric: str,
    ) -> None:
        definition = definitions[identifier]
        denominator_metric = str(definition["minimum_denominator_metric"])
        minimum = float(definition["minimum_denominator"])
        value = _one_value(weekly, value_metric)
        denominator = _one_value(weekly, denominator_metric)
        sufficient = value is not None and denominator is not None and denominator >= minimum
        results.append(
            {
                "id": identifier,
                "value": value,
                "operator": definition["operator"],
                "target": definition["target"],
                "denominator": denominator,
                "minimum_denominator": minimum,
                "sufficient": sufficient,
                "status": result_status(value, definition, sufficient=sufficient),
            }
        )

    add_with_denominator(
        "apple_conversion_rate_pct",
        "apple_conversion_rate_pct",
    )
    google_definition = definitions["google_store_listing_ctr_pct"]
    google_ctr = _one_value(weekly, "google_store_listing_ctr_pct")
    if google_ctr is None:
        google_ctr = _one_value(weekly, "google_store_listing_ctr_pct_derived")
    google_denominator_metric = str(
        google_definition["minimum_denominator_metric"]
    )
    google_visitors = _one_value(weekly, google_denominator_metric)
    google_minimum = float(google_definition["minimum_denominator"])
    google_sufficient = (
        google_ctr is not None
        and google_visitors is not None
        and google_visitors >= google_minimum
    )
    results.append(
        {
            "id": "google_store_listing_ctr_pct",
            "value": google_ctr,
            "operator": google_definition["operator"],
            "target": google_definition["target"],
            "denominator": google_visitors,
            "minimum_denominator": google_minimum,
            "sufficient": google_sufficient,
            "status": result_status(
                google_ctr, google_definition, sufficient=google_sufficient
            ),
        }
    )

    for platform in ("apple", "google"):
        for metric in (
            "first_launch_rate_pct",
            "d7_retention_pct",
            "dau_mau_pct",
        ):
            definition = definitions[metric]
            values = [
                float(record["value"])
                for record in (weekly or {}).get("derived_metrics", [])
                if record.get("platform") == platform
                and record.get("decision_eligible", True) is True
                and record.get("storefront") == "UZ"
                and record.get("source_scope") == "summary"
                and record.get("device") == "all"
                and record.get("app_version") == "all"
                and record.get("metric") == metric
            ]
            value = values[0] if len(values) == 1 else None
            results.append(
                {
                    "id": f"{platform}_{metric}",
                    "value": value,
                    "operator": definition["operator"],
                    "target": definition["target"],
                    "sufficient": value is not None,
                    "status": result_status(
                        value, definition, sufficient=value is not None
                    ),
                }
            )

    for platform in ("apple", "google"):
        ratings_definition = definitions["ratings_count"]
        average_definition = definitions["average_rating"]
        ratings = _one_value(weekly, f"{platform}_ratings_count")
        average = _one_value(weekly, f"{platform}_average_rating")
        results.extend(
            [
                {
                    "id": f"{platform}_ratings_count",
                    "value": ratings,
                    "operator": ratings_definition["operator"],
                    "target": ratings_definition["target"],
                    "sufficient": ratings is not None,
                    "status": result_status(
                        ratings,
                        ratings_definition,
                        sufficient=ratings is not None,
                    ),
                },
                {
                    "id": f"{platform}_average_rating",
                    "value": average,
                    "operator": average_definition["operator"],
                    "target": average_definition["target"],
                    "sufficient": average is not None,
                    "status": result_status(
                        average,
                        average_definition,
                        sufficient=average is not None,
                    ),
                },
            ]
        )
    relevant_below = [
        result["id"]
        for result in results
        if result["status"] == "fail"
        and (
            "conversion" in result["id"]
            or "ctr" in result["id"]
            or "retention" in result["id"]
        )
    ]
    return {
        "results": results,
        "sufficient_conversion_or_retention_below_target": relevant_below,
        "decision_exclusions": list(
            (weekly or {}).get("decision_exclusions", [])
        ),
    }


def _compare(value: float, operator: str, threshold: float) -> bool:
    if operator == ">=":
        return value >= threshold
    if operator == "<":
        return value < threshold
    if operator == "==":
        return value == threshold
    raise ValueError(f"unsupported operator {operator}")


def evaluate_guardrails(
    weekly: dict[str, Any] | None,
    framework: dict[str, Any],
    gates: dict[str, Any],
) -> dict[str, Any]:
    gate_results: list[dict[str, Any]] = []
    for required in framework["scale_gates"]:
        gate = gates.get("gates", {}).get(required["id"], {})
        actual = gate.get("status", "unknown")
        gate_results.append(
            {
                "id": required["id"],
                "required": required["required_status"],
                "actual": actual,
                "status": "pass" if actual == required["required_status"] else "fail",
                "reason": gate.get("reason"),
            }
        )

    guardrail_results: list[dict[str, Any]] = []
    for definition in framework["guardrails"]:
        identifier = definition["id"]
        metric_ids: list[str]
        if identifier == "user_loss_rate_pct":
            metric_ids = ["apple_user_loss_rate_pct", "google_user_loss_rate_pct"]
        elif identifier == "open_policy_issues":
            metric_ids = ["apple_policy_issues", "google_policy_issues"]
        else:
            metric_ids = [identifier]
        values_by_metric = {
            metric_id: _guardrail_metric_values(weekly, metric_id)
            for metric_id in metric_ids
        }
        values = [
            value
            for metric_id in metric_ids
            for value in values_by_metric[metric_id]
        ]
        missing_metric_ids = [
            metric_id for metric_id in metric_ids if not values_by_metric[metric_id]
        ]
        passed = all(
            _compare(value, definition["operator"], float(definition["threshold"]))
            for value in values
        )
        if not passed:
            status = "fail"
        elif missing_metric_ids:
            status = "unknown"
        else:
            status = "pass"
        guardrail_results.append(
            {
                "id": identifier,
                "metric_ids": metric_ids,
                "values": values,
                "missing_metric_ids": missing_metric_ids,
                "operator": definition["operator"],
                "threshold": definition["threshold"],
                "critical": definition["critical"],
                "status": status,
                "unknown_policy": definition["unknown_policy"],
            }
        )

    critical_ready = all(result["status"] == "pass" for result in gate_results) and all(
        result["status"] == "pass"
        for result in guardrail_results
        if result["critical"]
    )
    return {
        "scale_gates": gate_results,
        "metric_guardrails": guardrail_results,
        "critical_quality_gates_pass": critical_ready,
    }


def decide_90_day(
    guardrails: dict[str, Any],
    drivers: dict[str, Any],
    ranks: dict[str, Any],
    framework: dict[str, Any],
) -> tuple[str, str]:
    if not guardrails["critical_quality_gates_pass"]:
        return (
            "hold_acquisition_and_fix_gate",
            "At least one critical scale gate or quality guardrail is failed or unknown.",
        )
    exclusions = drivers.get("decision_exclusions", [])
    if exclusions:
        return (
            "continue_measurement_no_paid_decision",
            "One or more driver ratios have impossible or materially conflicting "
            "evidence and are excluded from decision eligibility.",
        )
    below = drivers["sufficient_conversion_or_retention_below_target"]
    if below:
        return (
            "iterate_product_and_store_listing",
            "Sufficient conversion or retention evidence is below target: "
            + ", ".join(below),
        )
    improvement = ranks["max_improvement"]
    threshold = float(
        framework["decision_thresholds"][
            "comparable_rank_improvement_positions"
        ]
    )
    if improvement is not None and improvement >= threshold:
        return (
            "continue_organic_program",
            f"At least one comparable primary surface improved by {improvement} positions.",
        )
    if improvement is not None:
        return (
            "prepare_paid_pilot_and_provider_cost_only_no_spend",
            "Best comparable primary-surface improvement is "
            f"{improvement}, below {threshold:g}.",
        )
    return (
        "continue_measurement_no_paid_decision",
        "There is not yet a comparable two-point rank series under one monitor configuration.",
    )


def evaluate(
    *,
    as_of: date,
    framework: dict[str, Any],
    gates: dict[str, Any],
    snapshots: list[dict[str, Any]],
    weekly_payloads: list[dict[str, Any]],
) -> dict[str, Any]:
    latest_weekly = weekly_payloads[-1] if weekly_payloads else None
    streak = calculate_streak(
        snapshots,
        as_of,
        int(framework["primary_goal"]["required_consecutive_complete_days"]),
    )
    ranks = rank_improvements(snapshots)
    drivers = evaluate_drivers(latest_weekly, framework)
    guardrails = evaluate_guardrails(latest_weekly, framework, gates)
    decision, reason = decide_90_day(guardrails, drivers, ranks, framework)
    checkpoint = parse_date(framework["checkpoint_90_day"])
    return {
        "schema_version": 1,
        "as_of": as_of.isoformat(),
        "checkpoint_90_day": checkpoint.isoformat(),
        "checkpoint_due": as_of >= checkpoint,
        "latest_weekly_period_end": latest_weekly.get("week_end") if latest_weekly else None,
        "top10_goal": streak,
        "rank_improvement": ranks,
        "drivers": drivers,
        "guardrails": guardrails,
        "decision_90_day_rule": {
            "decision": decision,
            "reason": reason,
            "paid_spend_authorized": False,
            "external_action_authorized": False,
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of")
    parser.add_argument(
        "--framework", type=Path, default=GROWTH_ROOT / "kpi-framework.json"
    )
    parser.add_argument(
        "--gates", type=Path, default=GROWTH_ROOT / "quality/gates.json"
    )
    parser.add_argument(
        "--rank-dir", type=Path, default=GROWTH_ROOT / "data/public-rank"
    )
    parser.add_argument(
        "--weekly-dir", type=Path, default=GROWTH_ROOT / "data/weekly"
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--replace", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    framework = load_json(args.framework)
    gates = load_json(args.gates)
    timezone_name = "Asia/Tashkent"
    as_of = parse_date(args.as_of) if args.as_of else now_in(timezone_name).date()
    snapshots = _load_dated_json(args.rank_dir, as_of, "date")
    weekly_payloads = _load_dated_json(args.weekly_dir, as_of, "week_end")
    payload = evaluate(
        as_of=as_of,
        framework=framework,
        gates=gates,
        snapshots=snapshots,
        weekly_payloads=weekly_payloads,
    )
    output = args.output or GROWTH_ROOT / "reports" / f"evaluation-{as_of.isoformat()}.json"
    if output.exists() and not args.replace:
        print(f"evaluation already exists: {output}; pass --replace", file=sys.stderr)
        return 2
    write_json(output, payload)
    decision = payload["decision_90_day_rule"]["decision"]
    print(f"Wrote {output}: {decision}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
