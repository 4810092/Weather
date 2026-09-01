#!/usr/bin/env python3
"""Render one deterministic, fail-closed Nimbo weekly growth review."""

from __future__ import annotations

import argparse
import math
import os
import re
import sys
import tempfile
from copy import deepcopy
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.growth.common import (  # noqa: E402
    GROWTH_ROOT,
    MODEL_VITAL_METRICS,
    POLICY_METRICS,
    ROOT,
    is_concrete_device,
    load_json,
    parse_date,
)


TIMEZONE = "Asia/Tashkent"
SUPPORTED_SCHEMA_VERSION = 1
REQUIRED_STREAK_DAYS = 7
RANK_THRESHOLD = 10
GENERIC_QUERY_REQUIRED = 2
GENERIC_QUERY_PROFILE_QUORUM = 2
ALLOWED_RESULT_STATUSES = frozenset({"pass", "fail", "unknown"})
ALLOWED_OPERATORS = frozenset({">=", "<", "=="})
ALLOWED_UNKNOWN_POLICIES = frozenset(
    {"block_scale", "review_required", "report_unknown"}
)

DECISION_LABELS = {
    "hold_acquisition_and_fix_gate": "HOLD",
    "iterate_product_and_store_listing": "ITERATE",
    "continue_organic_program": "CONTINUE ORGANIC",
    "prepare_paid_pilot_and_provider_cost_only_no_spend": (
        "PREPARE PAID PILOT, NO SPEND"
    ),
    "continue_measurement_no_paid_decision": "INSUFFICIENT DATA",
}

DRIVER_LABELS = {
    "apple_conversion_rate_pct": "Apple conversion",
    "google_store_listing_ctr_pct": "Google listing CTR",
    "apple_first_launch_rate_pct": "Apple first launch / install",
    "google_first_launch_rate_pct": "Google first launch / install",
    "apple_d7_retention_pct": "Apple D7 retention",
    "google_d7_retention_pct": "Google D7 retention",
    "apple_dau_mau_pct": "Apple DAU / MAU",
    "google_dau_mau_pct": "Google DAU / MAU",
    "apple_ratings_count": "Apple ratings count",
    "apple_average_rating": "Apple average rating",
    "google_ratings_count": "Google ratings count",
    "google_average_rating": "Google average rating",
}

GATE_LABELS = {
    "ios_crash_gate": "iOS crash gate",
    "open_meteo_promotion_clearance": "Open-Meteo promotion clearance",
    "release_artifact_source_sync": "Release artifact / source sync",
    "android_physical_smoke": "Android physical smoke",
    "ios_physical_smoke": "iOS physical smoke",
    "domain_activation": "nimbo.uz activation",
    "store_policy_console_clearance": "Store policy console clearance",
}

GUARDRAIL_LABELS = {
    "ios_crash_free_sessions_pct": "iOS crash-free sessions",
    "android_user_perceived_crash_rate_pct": "Android user-perceived crash rate",
    "android_user_perceived_anr_rate_pct": "Android user-perceived ANR rate",
    "android_phone_model_crash_rate_pct": "Android phone-model crash rate",
    "android_phone_model_anr_rate_pct": "Android phone-model ANR rate",
    "wear_model_crash_rate_pct": "Wear model crash rate",
    "wear_model_anr_rate_pct": "Wear model ANR rate",
    "user_loss_rate_pct": "User loss rate",
    "open_policy_issues": "Open policy issues",
}

GATE_ACTIONS = {
    "ios_crash_gate": (
        "Engineering",
        "Obtain and symbolicate any diagnostic Apple exposes, install build 7 "
        "from TestFlight, complete the iPhone, iPad, "
        "widget, and watch matrix, and collect post-rollout crash evidence before "
        "acquisition resumes.",
    ),
    "open_meteo_promotion_clearance": (
        "Product / legal",
        "Obtain written Open-Meteo promotion clearance; keep promotion paused until "
        "the reply is recorded.",
    ),
    "release_artifact_source_sync": (
        "Release engineering",
        "Require the protected hosted chain to recheck the mutable draft before "
        "every later use, then bind store-delivered physical QA.",
    ),
    "android_physical_smoke": (
        "Android engineering",
        "Complete replacement physical tablet/widget coverage, paired Wear "
        "vc1000009 install/handoff, and post-delivery vitals.",
    ),
    "ios_physical_smoke": (
        "Apple engineering",
        "Install build 7 from TestFlight, restore watch readiness, then complete "
        "iPhone, iPad, widget, and watch QA.",
    ),
    "domain_activation": (
        "Web operations",
        "Verify a matching nimbo.uz/www certificate, HTTPS redirects, canonicals, "
        "and localized routes before using the domain in store or outreach surfaces.",
    ),
    "store_policy_console_clearance": (
        "Store operations",
        "Resolve every open store policy item and preserve a dated console check.",
    ),
}

RATIO_METRICS = {
    "google_store_listing_ctr_pct": (
        "google",
        "google_unique_user_install_clicks",
        "google_store_listing_visitors",
    ),
    "apple_first_launch_rate_pct": (
        "apple",
        "apple_first_launches",
        "apple_installations",
    ),
    "google_first_launch_rate_pct": (
        "google",
        "google_first_launches",
        "google_installations",
    ),
    "apple_d7_retention_pct": (
        "apple",
        "apple_d7_retained",
        "apple_d7_eligible",
    ),
    "google_d7_retention_pct": (
        "google",
        "google_d7_retained",
        "google_d7_eligible",
    ),
    "apple_dau_mau_pct": (
        "apple",
        "apple_average_daily_active_devices_30d",
        "apple_active_devices_30d",
    ),
    "google_dau_mau_pct": (
        "google",
        "google_average_daily_active_users_30d",
        "google_monthly_active_users",
    ),
}

RANK_ROWS = (
    ("Apple UZ Top Free Weather", "apple.category"),
    ("Google UZ Weather, `uz-UZ`", "google.category.uz-UZ"),
    ("Google UZ Weather, `ru-UZ`", "google.category.ru-UZ"),
    ("Google UZ Weather, `en-UZ`", "google.category.en-UZ"),
)

EXPECTED_DRIVER_IDS = frozenset(DRIVER_LABELS)
EXPECTED_GATE_IDS = frozenset(GATE_LABELS)
EXPECTED_GUARDRAIL_IDS = frozenset(GUARDRAIL_LABELS)
PERCENT_DRIVER_IDS = frozenset(
    identifier
    for identifier in EXPECTED_DRIVER_IDS
    if identifier.endswith("_pct")
)
COUNT_DRIVER_IDS = frozenset(
    {"apple_ratings_count", "google_ratings_count"}
)
RATING_DRIVER_IDS = frozenset(
    {"apple_average_rating", "google_average_rating"}
)
COMPARABLE_SURFACE_IDS = frozenset(
    {surface_id for _, surface_id in RANK_ROWS} | {"apple.search.weather"}
)
GUARDRAIL_METRIC_IDS = {
    "ios_crash_free_sessions_pct": ("ios_crash_free_sessions_pct",),
    "android_user_perceived_crash_rate_pct": (
        "android_user_perceived_crash_rate_pct",
    ),
    "android_user_perceived_anr_rate_pct": (
        "android_user_perceived_anr_rate_pct",
    ),
    "android_phone_model_crash_rate_pct": (
        "android_phone_model_crash_rate_pct",
    ),
    "android_phone_model_anr_rate_pct": ("android_phone_model_anr_rate_pct",),
    "wear_model_crash_rate_pct": ("wear_model_crash_rate_pct",),
    "wear_model_anr_rate_pct": ("wear_model_anr_rate_pct",),
    "user_loss_rate_pct": (
        "apple_user_loss_rate_pct",
        "google_user_loss_rate_pct",
    ),
    "open_policy_issues": ("apple_policy_issues", "google_policy_issues"),
}
DERIVED_METRIC_UNITS = {
    "google_store_listing_ctr_pct_derived": "percent",
    "first_launch_rate_pct": "percent",
    "d7_retention_pct": "percent",
    "dau_mau_pct": "percent",
    "crashes_per_1000_sessions": "per_1000_sessions",
}
DERIVED_FORMULAS = {
    ("google", "google_store_listing_ctr_pct_derived"): (
        "google_unique_user_install_clicks",
        "google_store_listing_visitors",
        100.0,
    ),
    ("google", "first_launch_rate_pct"): (
        "google_first_launches",
        "google_installations",
        100.0,
    ),
    ("apple", "first_launch_rate_pct"): (
        "apple_first_launches",
        "apple_installations",
        100.0,
    ),
    ("google", "d7_retention_pct"): (
        "google_d7_retained",
        "google_d7_eligible",
        100.0,
    ),
    ("apple", "d7_retention_pct"): (
        "apple_d7_retained",
        "apple_d7_eligible",
        100.0,
    ),
    ("google", "dau_mau_pct"): (
        "google_average_daily_active_users_30d",
        "google_monthly_active_users",
        100.0,
    ),
    ("apple", "dau_mau_pct"): (
        "apple_average_daily_active_devices_30d",
        "apple_active_devices_30d",
        100.0,
    ),
    ("apple", "crashes_per_1000_sessions"): (
        "apple_crashes",
        "apple_sessions",
        1000.0,
    ),
}


class ReportInputError(ValueError):
    """Raised when a report input violates the local evidence contract."""


@lru_cache(maxsize=1)
def _framework_contract() -> dict[str, Any]:
    payload = _mapping(
        load_json(GROWTH_ROOT / "kpi-framework.json"), "KPI framework"
    )
    if payload.get("schema_version") != SUPPORTED_SCHEMA_VERSION:
        raise ReportInputError("KPI framework schema_version is unsupported")
    return payload


def _mapping(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReportInputError(f"{context} must be an object")
    return value


def _list(value: Any, context: str) -> list[Any]:
    if not isinstance(value, list):
        raise ReportInputError(f"{context} must be an array")
    return value


def _validated_date(value: Any, context: str) -> date:
    if not isinstance(value, str):
        raise ReportInputError(f"{context} must be an ISO date string")
    try:
        return parse_date(value)
    except ValueError as exc:
        raise ReportInputError(f"{context}: {exc}") from exc


def _validated_number(
    value: Any,
    context: str,
    *,
    allow_none: bool = False,
    minimum: float | None = None,
    maximum: float | None = None,
    integer: bool = False,
) -> float | None:
    if value is None and allow_none:
        return None
    numeric = _number(value)
    if numeric is None:
        raise ReportInputError(f"{context} must be a finite number")
    if minimum is not None and numeric < minimum:
        raise ReportInputError(f"{context} must be >= {minimum:g}")
    if maximum is not None and numeric > maximum:
        raise ReportInputError(f"{context} must be <= {maximum:g}")
    if integer and not numeric.is_integer():
        raise ReportInputError(f"{context} must be an integer")
    return numeric


def _compare(value: float, operator: str, threshold: float) -> bool:
    if operator == ">=":
        return value >= threshold
    if operator == "<":
        return value < threshold
    if operator == "==":
        return value == threshold
    raise ReportInputError(f"unsupported operator {operator!r}")


def _indexed_items(
    values: Any,
    context: str,
    expected_ids: frozenset[str],
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for position, raw in enumerate(_list(values, context)):
        item = _mapping(raw, f"{context}[{position}]")
        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier:
            raise ReportInputError(f"{context}[{position}] is missing id")
        if identifier in result:
            raise ReportInputError(f"duplicate {context} id {identifier}")
        result[identifier] = item
    actual_ids = frozenset(result)
    if actual_ids != expected_ids:
        missing = sorted(expected_ids - actual_ids)
        extra = sorted(actual_ids - expected_ids)
        raise ReportInputError(
            f"{context} ids do not match the canonical set; "
            f"missing={missing}, extra={extra}"
        )
    return result


def _validate_top10_goal(payload: dict[str, Any], as_of: date) -> None:
    goal = _mapping(payload.get("top10_goal"), "evaluation.top10_goal")
    present = goal.get("as_of_snapshot_present")
    if not isinstance(present, bool):
        raise ReportInputError(
            "evaluation.top10_goal.as_of_snapshot_present must be boolean"
        )
    fingerprint = goal.get("current_config_fingerprint")
    if present:
        if not isinstance(fingerprint, str) or not fingerprint:
            raise ReportInputError(
                "evaluation.top10_goal.current_config_fingerprint is required "
                "when the as-of snapshot is present"
            )
    elif fingerprint is not None:
        raise ReportInputError(
            "evaluation.top10_goal.current_config_fingerprint must be null when "
            "the as-of snapshot is absent"
        )
    current = _validated_number(
        goal.get("current_streak_days"),
        "evaluation.top10_goal.current_streak_days",
        minimum=0,
        integer=True,
    )
    maximum = _validated_number(
        goal.get("max_streak_days"),
        "evaluation.top10_goal.max_streak_days",
        minimum=0,
        integer=True,
    )
    required = _validated_number(
        goal.get("required_days"),
        "evaluation.top10_goal.required_days",
        minimum=1,
        integer=True,
    )
    framework_required = int(
        _framework_contract()["primary_goal"][
            "required_consecutive_complete_days"
        ]
    )
    if required != framework_required or required != REQUIRED_STREAK_DAYS:
        raise ReportInputError(
            "evaluation.top10_goal.required_days differs from the canonical KPI "
            "framework"
        )
    if current > maximum:
        raise ReportInputError(
            "evaluation.top10_goal.current_streak_days exceeds max_streak_days"
        )
    if not present and current != 0:
        raise ReportInputError(
            "evaluation.top10_goal.current_streak_days must be zero without an "
            "as-of snapshot"
        )
    achieved = goal.get("goal_achieved")
    if not isinstance(achieved, bool) or achieved != (maximum >= required):
        raise ReportInputError(
            "evaluation.top10_goal.goal_achieved conflicts with max_streak_days"
        )
    achieved_on = goal.get("first_achieved_on")
    achieved_fingerprint = goal.get("first_achieved_config_fingerprint")
    if achieved:
        achieved_date = _validated_date(
            achieved_on, "evaluation.top10_goal.first_achieved_on"
        )
        if achieved_date > as_of:
            raise ReportInputError(
                "evaluation.top10_goal.first_achieved_on is after evaluation.as_of"
            )
        if not isinstance(achieved_fingerprint, str) or not achieved_fingerprint:
            raise ReportInputError(
                "evaluation.top10_goal.first_achieved_config_fingerprint is required"
            )
    elif achieved_on is not None or achieved_fingerprint is not None:
        raise ReportInputError(
            "evaluation.top10_goal first-achieved fields require goal_achieved=true"
        )


def _validate_rank_improvement(payload: dict[str, Any], as_of: date) -> None:
    ranks = _mapping(
        payload.get("rank_improvement"), "evaluation.rank_improvement"
    )
    fingerprint = ranks.get("config_fingerprint")
    if fingerprint is not None and (
        not isinstance(fingerprint, str) or not fingerprint
    ):
        raise ReportInputError(
            "evaluation.rank_improvement.config_fingerprint must be null or non-empty"
        )
    rows = _list(
        ranks.get("comparable_surfaces"),
        "evaluation.rank_improvement.comparable_surfaces",
    )
    seen: set[str] = set()
    improvements: list[float] = []
    for position, raw in enumerate(rows):
        item = _mapping(
            raw, f"evaluation.rank_improvement.comparable_surfaces[{position}]"
        )
        identifier = item.get("surface_id")
        if identifier not in COMPARABLE_SURFACE_IDS:
            raise ReportInputError(
                f"unsupported comparable rank surface {identifier!r}"
            )
        if identifier in seen:
            raise ReportInputError(f"duplicate comparable rank surface {identifier}")
        seen.add(str(identifier))
        baseline_date = _validated_date(
            item.get("baseline_date"), f"rank comparison {identifier}.baseline_date"
        )
        current_date = _validated_date(
            item.get("current_date"), f"rank comparison {identifier}.current_date"
        )
        if baseline_date > current_date or current_date > as_of:
            raise ReportInputError(
                f"rank comparison {identifier} has an invalid date window"
            )
        baseline = _validated_number(
            item.get("baseline_rank"),
            f"rank comparison {identifier}.baseline_rank",
            minimum=1,
            integer=True,
        )
        current = _validated_number(
            item.get("current_rank"),
            f"rank comparison {identifier}.current_rank",
            minimum=1,
            integer=True,
        )
        improvement = _validated_number(
            item.get("improvement"),
            f"rank comparison {identifier}.improvement",
        )
        if improvement != baseline - current:
            raise ReportInputError(
                f"rank comparison {identifier}.improvement conflicts with ranks"
            )
        improvements.append(improvement)
    expected_max = max(improvements) if improvements else None
    actual_max = _validated_number(
        ranks.get("max_improvement"),
        "evaluation.rank_improvement.max_improvement",
        allow_none=True,
    )
    if actual_max != expected_max:
        raise ReportInputError(
            "evaluation.rank_improvement.max_improvement conflicts with rows"
        )
    if rows and fingerprint is None:
        raise ReportInputError(
            "evaluation.rank_improvement.config_fingerprint is required with rows"
        )
    goal = _mapping(payload["top10_goal"], "evaluation.top10_goal")
    current_fingerprint = goal.get("current_config_fingerprint")
    if current_fingerprint is not None and fingerprint != current_fingerprint:
        raise ReportInputError(
            "rank-improvement fingerprint differs from current goal fingerprint"
        )


def _validate_driver_results(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    drivers = _mapping(payload.get("drivers"), "evaluation.drivers")
    framework_definitions = {
        str(item["id"]): item for item in _framework_contract()["drivers"]
    }
    indexed = _indexed_items(
        drivers.get("results"),
        "evaluation.drivers.results",
        EXPECTED_DRIVER_IDS,
    )
    for identifier, item in indexed.items():
        definition_id = identifier
        if definition_id not in framework_definitions:
            definition_id = identifier.removeprefix("apple_").removeprefix("google_")
        definition = framework_definitions.get(definition_id)
        if not isinstance(definition, dict):
            raise ReportInputError(
                f"driver {identifier} has no canonical framework definition"
            )
        operator = item.get("operator")
        if (
            operator not in ALLOWED_OPERATORS
            or operator != definition.get("operator")
        ):
            raise ReportInputError(
                f"driver {identifier}.operator differs from the KPI framework"
            )
        maximum = 100.0 if identifier in PERCENT_DRIVER_IDS else None
        if identifier in RATING_DRIVER_IDS:
            maximum = 5.0
        value = _validated_number(
            item.get("value"),
            f"driver {identifier}.value",
            allow_none=True,
            minimum=0,
            maximum=maximum,
            integer=identifier in COUNT_DRIVER_IDS,
        )
        target = _validated_number(
            item.get("target"),
            f"driver {identifier}.target",
            minimum=0,
            maximum=maximum,
            integer=identifier in COUNT_DRIVER_IDS,
        )
        if target != float(definition["target"]):
            raise ReportInputError(
                f"driver {identifier}.target differs from the KPI framework"
            )
        sufficient = item.get("sufficient")
        if not isinstance(sufficient, bool):
            raise ReportInputError(f"driver {identifier}.sufficient must be boolean")
        expected_sufficient = value is not None
        if "minimum_denominator" in item or "denominator" in item:
            denominator = _validated_number(
                item.get("denominator"),
                f"driver {identifier}.denominator",
                allow_none=True,
                minimum=0,
            )
            minimum_denominator = _validated_number(
                item.get("minimum_denominator"),
                f"driver {identifier}.minimum_denominator",
                minimum=0,
            )
            if (
                "minimum_denominator" not in definition
                or minimum_denominator
                != float(definition["minimum_denominator"])
            ):
                raise ReportInputError(
                    f"driver {identifier}.minimum_denominator differs from the "
                    "KPI framework"
                )
            expected_sufficient = (
                value is not None
                and denominator is not None
                and denominator >= minimum_denominator
            )
        elif "minimum_denominator" in definition:
            raise ReportInputError(
                f"driver {identifier} is missing its canonical denominator gate"
            )
        if sufficient != expected_sufficient:
            raise ReportInputError(
                f"driver {identifier}.sufficient conflicts with its evidence"
            )
        expected_status = (
            "unknown"
            if not sufficient or value is None
            else "pass"
            if _compare(value, str(operator), target)
            else "fail"
        )
        if item.get("status") != expected_status:
            raise ReportInputError(
                f"driver {identifier}.status conflicts with value and target"
            )
    below = _list(
        drivers.get("sufficient_conversion_or_retention_below_target"),
        "evaluation.drivers.sufficient_conversion_or_retention_below_target",
    )
    expected_below = {
        identifier
        for identifier, item in indexed.items()
        if item.get("status") == "fail"
        and (
            "conversion" in identifier
            or "ctr" in identifier
            or "retention" in identifier
        )
    }
    if len(below) != len(set(below)) or set(below) != expected_below:
        raise ReportInputError(
            "evaluation.drivers sufficient-below-target list conflicts with results"
        )
    _list(drivers.get("decision_exclusions"), "evaluation.drivers.decision_exclusions")
    return indexed


def _validate_guardrails(payload: dict[str, Any]) -> dict[str, Any]:
    guardrails = _mapping(payload.get("guardrails"), "evaluation.guardrails")
    framework = _framework_contract()
    gate_definitions = {str(item["id"]): item for item in framework["scale_gates"]}
    guardrail_definitions = {
        str(item["id"]): item for item in framework["guardrails"]
    }
    gates = _indexed_items(
        guardrails.get("scale_gates"),
        "evaluation.guardrails.scale_gates",
        EXPECTED_GATE_IDS,
    )
    for identifier, item in gates.items():
        expected_required = gate_definitions.get(identifier, {}).get(
            "required_status"
        )
        if item.get("required") != expected_required:
            raise ReportInputError(
                f"scale gate {identifier}.required differs from the KPI framework"
            )
        actual = item.get("actual")
        if not isinstance(actual, str) or not actual:
            raise ReportInputError(f"scale gate {identifier}.actual must be non-empty")
        expected_status = "pass" if actual == "pass" else "fail"
        if item.get("status") != expected_status:
            raise ReportInputError(
                f"scale gate {identifier}.status conflicts with actual"
            )
    metrics = _indexed_items(
        guardrails.get("metric_guardrails"),
        "evaluation.guardrails.metric_guardrails",
        EXPECTED_GUARDRAIL_IDS,
    )
    for identifier, item in metrics.items():
        definition = guardrail_definitions.get(identifier)
        if not isinstance(definition, dict):
            raise ReportInputError(
                f"metric guardrail {identifier} has no framework definition"
            )
        metric_ids = _list(
            item.get("metric_ids"), f"metric guardrail {identifier}.metric_ids"
        )
        if tuple(metric_ids) != GUARDRAIL_METRIC_IDS[identifier]:
            raise ReportInputError(
                f"metric guardrail {identifier}.metric_ids are not canonical"
            )
        operator = item.get("operator")
        if operator not in ALLOWED_OPERATORS or operator != definition.get("operator"):
            raise ReportInputError(
                f"metric guardrail {identifier}.operator differs from the framework"
            )
        maximum = None if identifier == "open_policy_issues" else 100.0
        threshold = _validated_number(
            item.get("threshold"),
            f"metric guardrail {identifier}.threshold",
            minimum=0,
            maximum=maximum,
        )
        if threshold != float(definition["threshold"]):
            raise ReportInputError(
                f"metric guardrail {identifier}.threshold differs from the framework"
            )
        values = _list(item.get("values"), f"metric guardrail {identifier}.values")
        normalized_values = [
            _validated_number(
                value,
                f"metric guardrail {identifier}.values[{position}]",
                minimum=0,
                maximum=maximum,
                integer=identifier == "open_policy_issues",
            )
            for position, value in enumerate(values)
        ]
        raw_missing_metric_ids = item.get("missing_metric_ids")
        if raw_missing_metric_ids is None:
            # Schema-v1 evaluations produced before missing-metric provenance was
            # added remain readable only when the provenance is unambiguous.
            if not normalized_values:
                missing_metric_ids = list(metric_ids)
            elif len(metric_ids) == 1 or len(normalized_values) == len(metric_ids):
                missing_metric_ids = []
            else:
                raise ReportInputError(
                    f"metric guardrail {identifier} legacy composite values lack "
                    "metric provenance"
                )
            item["missing_metric_ids"] = missing_metric_ids
        else:
            missing_metric_ids = _list(
                raw_missing_metric_ids,
                f"metric guardrail {identifier}.missing_metric_ids",
            )
        if any(not isinstance(metric_id, str) for metric_id in missing_metric_ids):
            raise ReportInputError(
                f"metric guardrail {identifier}.missing_metric_ids must contain strings"
            )
        canonical_missing = [
            metric_id for metric_id in metric_ids if metric_id in missing_metric_ids
        ]
        if missing_metric_ids != canonical_missing:
            raise ReportInputError(
                f"metric guardrail {identifier}.missing_metric_ids are not canonical"
            )
        present_metric_count = len(metric_ids) - len(missing_metric_ids)
        if (
            (present_metric_count == 0 and normalized_values)
            or (present_metric_count > 0 and not normalized_values)
            or (len(metric_ids) > 1 and len(normalized_values) != present_metric_count)
        ):
            raise ReportInputError(
                f"metric guardrail {identifier}.values conflict with missing_metric_ids"
            )
        critical = item.get("critical")
        if not isinstance(critical, bool):
            raise ReportInputError(
                f"metric guardrail {identifier}.critical must be boolean"
            )
        if critical != definition.get("critical"):
            raise ReportInputError(
                f"metric guardrail {identifier}.critical differs from the framework"
            )
        if (
            item.get("unknown_policy") not in ALLOWED_UNKNOWN_POLICIES
            or item.get("unknown_policy") != definition.get("unknown_policy")
        ):
            raise ReportInputError(
                f"metric guardrail {identifier}.unknown_policy differs from the framework"
            )
        passed = all(
            _compare(value, str(operator), threshold)
            for value in normalized_values
        )
        expected_status = (
            "fail"
            if not passed
            else "unknown"
            if missing_metric_ids
            else "pass"
        )
        if item.get("status") != expected_status:
            raise ReportInputError(
                f"metric guardrail {identifier}.status conflicts with values"
            )
    expected_ready = all(item["status"] == "pass" for item in gates.values()) and all(
        item["status"] == "pass"
        for item in metrics.values()
        if item["critical"] is True
    )
    if guardrails.get("critical_quality_gates_pass") is not expected_ready:
        raise ReportInputError(
            "evaluation.guardrails.critical_quality_gates_pass conflicts with results"
        )
    return guardrails


def _validate_decision(payload: dict[str, Any]) -> None:
    decision = _mapping(
        payload.get("decision_90_day_rule"), "evaluation.decision_90_day_rule"
    )
    identifier = decision.get("decision")
    if identifier not in DECISION_LABELS:
        raise ReportInputError(f"unsupported evaluation decision {identifier!r}")
    reason = decision.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        raise ReportInputError("evaluation decision reason must be non-empty")
    if decision.get("paid_spend_authorized") is not False:
        raise ReportInputError("evaluation cannot authorize paid spend")
    if decision.get("external_action_authorized") is not False:
        raise ReportInputError("evaluation cannot authorize external action")
    guardrails = _mapping(payload["guardrails"], "evaluation.guardrails")
    drivers = _mapping(payload["drivers"], "evaluation.drivers")
    ranks = _mapping(payload["rank_improvement"], "evaluation.rank_improvement")
    if guardrails["critical_quality_gates_pass"] is not True:
        expected = "hold_acquisition_and_fix_gate"
    elif drivers["decision_exclusions"]:
        expected = "continue_measurement_no_paid_decision"
    elif drivers["sufficient_conversion_or_retention_below_target"]:
        expected = "iterate_product_and_store_listing"
    elif ranks["max_improvement"] is None:
        expected = "continue_measurement_no_paid_decision"
    elif float(ranks["max_improvement"]) >= float(
        _framework_contract()["decision_thresholds"][
            "comparable_rank_improvement_positions"
        ]
    ):
        expected = "continue_organic_program"
    else:
        expected = "prepare_paid_pilot_and_provider_cost_only_no_spend"
    if identifier != expected:
        raise ReportInputError(
            f"evaluation decision {identifier!r} conflicts with evaluated evidence; "
            f"expected {expected!r}"
        )


def _validate_evaluation(payload: dict[str, Any]) -> date:
    if payload.get("schema_version") != SUPPORTED_SCHEMA_VERSION:
        raise ReportInputError(
            "evaluation schema_version must be "
            f"{SUPPORTED_SCHEMA_VERSION}, got {payload.get('schema_version')!r}"
        )
    if "as_of" not in payload:
        raise ReportInputError("evaluation is missing as_of")
    as_of = _validated_date(payload["as_of"], "evaluation.as_of")
    _validate_top10_goal(payload, as_of)
    _validate_rank_improvement(payload, as_of)
    _validate_driver_results(payload)
    _validate_guardrails(payload)
    _validate_decision(payload)
    return as_of


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    result = float(value)
    return result if math.isfinite(result) else None


def _format_number(value: Any) -> str:
    numeric = _number(value)
    if numeric is None:
        return "Unknown"
    if numeric.is_integer():
        return f"{int(numeric):,}"
    return f"{numeric:,.2f}".rstrip("0").rstrip(".")


def _format_percent(value: Any) -> str:
    rendered = _format_number(value)
    return rendered if rendered == "Unknown" else f"{rendered}%"


def _format_status(value: Any) -> str:
    normalized = str(value or "unknown").strip().upper()
    return normalized if normalized else "UNKNOWN"


def _escape(value: Any) -> str:
    return " ".join(str(value or "Unknown").split()).replace("|", "\\|")


def _source_label(path: Path | None) -> str:
    if path is None:
        return "Not available"
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.name


def _safe_load_optional(path: Path | None, label: str) -> dict[str, Any] | None:
    if path is None:
        return None
    try:
        return _mapping(load_json(path), label)
    except (OSError, ValueError) as exc:
        raise ReportInputError(f"cannot read {label} {path}: {exc}") from exc


def _rank_surface_status(surface: dict[str, Any]) -> str:
    if surface.get("status") != "ok":
        return "unknown"
    rank = surface.get("target_rank")
    bound = surface.get("target_rank_bound")
    if isinstance(rank, bool):
        return "unknown"
    if isinstance(rank, int):
        if rank < 1 or bound is not None:
            return "unknown"
        return "pass" if rank <= RANK_THRESHOLD else "fail"
    if rank is not None:
        return "unknown"
    if not isinstance(bound, str):
        return "unknown"
    match = re.fullmatch(r">([1-9][0-9]*)", bound)
    if match is None:
        return "unknown"
    return "fail" if int(match.group(1)) >= RANK_THRESHOLD else "unknown"


def _conjunction_status(statuses: list[str]) -> str:
    if any(status == "fail" for status in statuses):
        return "fail"
    if statuses and all(status == "pass" for status in statuses):
        return "pass"
    return "unknown"


def _derived_generic_status(snapshot: dict[str, Any]) -> tuple[str, list[str]]:
    surfaces = _mapping(snapshot.get("surfaces"), "rank snapshot.surfaces")
    google = _mapping(surfaces.get("google"), "rank snapshot.surfaces.google")
    searches = google.get("search")
    if not isinstance(searches, dict):
        return "unknown", []
    profiles = ("uz-UZ", "ru-UZ", "en-UZ")
    methodology = snapshot.get("methodology")
    query_ids: list[str] = []
    if isinstance(methodology, dict) and isinstance(
        methodology.get("fixed_query_ids"), list
    ):
        query_ids = [
            value
            for value in methodology["fixed_query_ids"]
            if isinstance(value, str) and value
        ]
    if not query_ids:
        query_ids = sorted(
            {
                query_id
                for profile in profiles
                for query_id in (
                    searches.get(profile, {}).keys()
                    if isinstance(searches.get(profile), dict)
                    else []
                )
                if isinstance(query_id, str) and query_id
            }
        )
    if not query_ids or len(query_ids) != len(set(query_ids)):
        return "unknown", []
    qualifying: list[str] = []
    unresolved = 0
    for query_id in query_ids:
        profile_statuses: list[str] = []
        for profile in profiles:
            profile_searches = searches.get(profile)
            surface = (
                profile_searches.get(query_id, {})
                if isinstance(profile_searches, dict)
                else {}
            )
            profile_statuses.append(
                _rank_surface_status(surface) if isinstance(surface, dict) else "unknown"
            )
        passed = sum(status == "pass" for status in profile_statuses)
        unknown = sum(status == "unknown" for status in profile_statuses)
        if passed >= GENERIC_QUERY_PROFILE_QUORUM:
            qualifying.append(query_id)
        elif passed + unknown >= GENERIC_QUERY_PROFILE_QUORUM:
            unresolved += 1
    if len(qualifying) >= GENERIC_QUERY_REQUIRED:
        status = "pass"
    elif len(qualifying) + unresolved < GENERIC_QUERY_REQUIRED:
        status = "fail"
    else:
        status = "unknown"
    return status, qualifying


def _validate_rank_payload(
    evaluation: dict[str, Any], snapshot: dict[str, Any]
) -> dict[str, Any]:
    requirements = _framework_contract()["primary_goal"]["daily_requirements"]
    if (
        int(requirements["apple_weather_chart_rank_lte"]) != RANK_THRESHOLD
        or int(requirements["google_weather_category_rank_lte"]) != RANK_THRESHOLD
        or int(requirements["generic_query_rank_lte"]) != RANK_THRESHOLD
        or int(requirements["generic_queries_required"])
        != GENERIC_QUERY_REQUIRED
        or int(requirements["generic_query_profile_quorum"])
        != GENERIC_QUERY_PROFILE_QUORUM
        or tuple(requirements["google_required_profiles"])
        != ("uz-UZ", "ru-UZ", "en-UZ")
    ):
        raise ReportInputError(
            "rank-report constants differ from the canonical KPI framework"
        )
    if snapshot.get("schema_version") != SUPPORTED_SCHEMA_VERSION:
        raise ReportInputError(
            "rank snapshot schema_version must be "
            f"{SUPPORTED_SCHEMA_VERSION}, got {snapshot.get('schema_version')!r}"
        )
    if snapshot.get("date") != evaluation.get("as_of"):
        raise ReportInputError(
            "rank snapshot date does not match evaluation.as_of"
        )
    fingerprint = snapshot.get("config_fingerprint")
    if not isinstance(fingerprint, str) or not fingerprint:
        raise ReportInputError("rank snapshot config_fingerprint must be non-empty")
    goal = _mapping(evaluation["top10_goal"], "evaluation.top10_goal")
    if goal.get("as_of_snapshot_present") is not True:
        raise ReportInputError(
            "evaluation does not reference an as-of rank snapshot; rerun evaluation"
        )
    if fingerprint != goal.get("current_config_fingerprint"):
        raise ReportInputError(
            "rank snapshot config_fingerprint differs from the evaluation"
        )
    for field in (
        "capture_complete",
        "diagnostic_capture_complete",
        "goal_evidence_complete",
    ):
        if field in snapshot and not isinstance(snapshot[field], bool):
            raise ReportInputError(f"rank snapshot {field} must be boolean")
    if (
        "diagnostic_capture_complete" in snapshot
        and "capture_complete" in snapshot
        and snapshot["diagnostic_capture_complete"] != snapshot["capture_complete"]
    ):
        raise ReportInputError(
            "rank snapshot diagnostic_capture_complete conflicts with capture_complete"
        )
    snapshot_evaluation = _mapping(
        snapshot.get("evaluation"), "rank snapshot.evaluation"
    )
    reasons = _list(
        snapshot_evaluation.get("reasons"), "rank snapshot.evaluation.reasons"
    )
    if any(not isinstance(reason, str) or not reason for reason in reasons):
        raise ReportInputError("rank snapshot evaluation reasons must be strings")
    if "source_errors" in snapshot:
        _list(snapshot["source_errors"], "rank snapshot.source_errors")
    complete = snapshot_evaluation.get("complete")
    if not isinstance(complete, bool):
        raise ReportInputError("rank snapshot evaluation.complete must be boolean")
    if (
        "goal_evidence_complete" in snapshot
        and snapshot["goal_evidence_complete"] != complete
    ):
        raise ReportInputError(
            "rank snapshot goal_evidence_complete conflicts with evaluation.complete"
        )
    surfaces = _mapping(snapshot.get("surfaces"), "rank snapshot.surfaces")
    apple = _mapping(surfaces.get("apple"), "rank snapshot.surfaces.apple")
    google = _mapping(surfaces.get("google"), "rank snapshot.surfaces.google")
    apple_category = _mapping(
        apple.get("category"), "rank snapshot Apple category"
    )
    google_categories = _mapping(
        google.get("category"), "rank snapshot Google categories"
    )
    surface_statuses = {
        "apple.category": _rank_surface_status(apple_category),
    }
    for profile in ("uz-UZ", "ru-UZ", "en-UZ"):
        surface_statuses[f"google.category.{profile}"] = _rank_surface_status(
            _mapping(
                google_categories.get(profile),
                f"rank snapshot Google category {profile}",
            )
        )
    reported_apple = snapshot_evaluation.get("apple_weather_chart_top10")
    if not isinstance(reported_apple, bool):
        raise ReportInputError(
            "rank snapshot apple_weather_chart_top10 must be boolean"
        )
    apple_status = surface_statuses["apple.category"]
    if apple_status != "unknown" and reported_apple != (apple_status == "pass"):
        raise ReportInputError(
            "rank snapshot Apple Top-10 status conflicts with its current rank"
        )
    if "apple_weather_chart_status" in snapshot_evaluation and (
        snapshot_evaluation["apple_weather_chart_status"] != apple_status
    ):
        raise ReportInputError(
            "rank snapshot Apple status field conflicts with its current rank"
        )
    reported_profiles = _mapping(
        snapshot_evaluation.get("google_category_top10_by_profile"),
        "rank snapshot google_category_top10_by_profile",
    )
    if set(reported_profiles) != {"uz-UZ", "ru-UZ", "en-UZ"}:
        raise ReportInputError(
            "rank snapshot Google category profiles are not canonical"
        )
    for profile in ("uz-UZ", "ru-UZ", "en-UZ"):
        reported = reported_profiles[profile]
        if not isinstance(reported, bool):
            raise ReportInputError(
                f"rank snapshot Google category {profile} result must be boolean"
            )
        status = surface_statuses[f"google.category.{profile}"]
        if status != "unknown" and reported != (status == "pass"):
            raise ReportInputError(
                f"rank snapshot Google category {profile} status conflicts with rank"
            )
    reported_profile_statuses = snapshot_evaluation.get(
        "google_category_status_by_profile"
    )
    if reported_profile_statuses is not None:
        reported_profile_statuses = _mapping(
            reported_profile_statuses,
            "rank snapshot google_category_status_by_profile",
        )
        if set(reported_profile_statuses) != {"uz-UZ", "ru-UZ", "en-UZ"}:
            raise ReportInputError(
                "rank snapshot Google category status profiles are not canonical"
            )
        for profile in ("uz-UZ", "ru-UZ", "en-UZ"):
            expected = surface_statuses[f"google.category.{profile}"]
            if reported_profile_statuses[profile] != expected:
                raise ReportInputError(
                    f"rank snapshot Google category {profile} status field conflicts"
                )
    google_category_status = _conjunction_status(
        [
            surface_statuses[f"google.category.{profile}"]
            for profile in ("uz-UZ", "ru-UZ", "en-UZ")
        ]
    )
    google_category_top10 = snapshot_evaluation.get(
        "google_weather_category_top10_all_profiles"
    )
    if not isinstance(google_category_top10, bool) or (
        google_category_status != "unknown"
        and google_category_top10 != (google_category_status == "pass")
    ):
        raise ReportInputError(
            "rank snapshot Google category aggregate conflicts with profiles"
        )
    if "google_weather_category_status" in snapshot_evaluation and (
        snapshot_evaluation["google_weather_category_status"]
        != google_category_status
    ):
        raise ReportInputError(
            "rank snapshot Google category status field conflicts with profiles"
        )
    queries = snapshot_evaluation.get("google_generic_top10_queries")
    if not isinstance(queries, list) or any(
        not isinstance(query, str) or not query for query in queries
    ):
        raise ReportInputError(
            "rank snapshot google_generic_top10_queries must contain strings"
        )
    if len(queries) != len(set(queries)):
        raise ReportInputError("rank snapshot generic Top-10 queries are duplicated")
    count = _validated_number(
        snapshot_evaluation.get("google_generic_top10_query_count"),
        "rank snapshot google_generic_top10_query_count",
        minimum=0,
        integer=True,
    )
    if count != len(queries):
        raise ReportInputError(
            "rank snapshot generic query count conflicts with its query list"
        )
    derived_generic, derived_queries = _derived_generic_status(snapshot)
    reported_generic = snapshot_evaluation.get("google_generic_query_status")
    if reported_generic is not None:
        if reported_generic not in ALLOWED_RESULT_STATUSES:
            raise ReportInputError(
                "rank snapshot google_generic_query_status is unsupported"
            )
        if derived_generic != "unknown" and reported_generic != derived_generic:
            raise ReportInputError(
                "rank snapshot generic query status conflicts with search surfaces"
            )
        generic_status = str(reported_generic)
    else:
        generic_status = derived_generic
    if derived_generic != "unknown" and sorted(queries) != sorted(derived_queries):
        raise ReportInputError(
            "rank snapshot generic query list conflicts with search surfaces"
        )
    if generic_status == "pass" and count < GENERIC_QUERY_REQUIRED:
        raise ReportInputError("rank snapshot generic query PASS lacks quorum")
    if generic_status == "fail" and count >= GENERIC_QUERY_REQUIRED:
        raise ReportInputError("rank snapshot generic query FAIL conflicts with quorum")
    overall = _conjunction_status(
        [apple_status]
        + [
            surface_statuses[f"google.category.{profile}"]
            for profile in ("uz-UZ", "ru-UZ", "en-UZ")
        ]
        + [generic_status]
    )
    if snapshot_evaluation.get("status") != overall:
        raise ReportInputError(
            "rank snapshot evaluation.status conflicts with current surfaces"
        )
    if complete != (overall != "unknown"):
        raise ReportInputError(
            "rank snapshot evaluation.complete conflicts with current surfaces"
        )
    requirements_pass = snapshot_evaluation.get("requirements_pass")
    if not isinstance(requirements_pass, bool) or requirements_pass != (
        overall == "pass"
    ):
        raise ReportInputError(
            "rank snapshot requirements_pass conflicts with current surfaces"
        )
    snapshot["_report_surface_statuses"] = surface_statuses
    snapshot["_report_generic_status"] = generic_status
    return snapshot


def _validated_rank_snapshot(
    evaluation: dict[str, Any],
    snapshot: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, list[str]]:
    if snapshot is None:
        return None, ["The public-rank snapshot for the evaluation date is missing."]
    try:
        return _validate_rank_payload(evaluation, deepcopy(snapshot)), []
    except (ValueError, ReportInputError) as exc:
        return None, [
            f"The supplied public-rank snapshot was rejected ({exc}); current ranks "
            "and rank comparisons were suppressed."
        ]


def _validate_weekly_record(
    raw: Any,
    *,
    context: str,
    week_start: str,
    week_end: str,
    metric_catalog: dict[str, Any],
    derived: bool,
) -> tuple[str, ...]:
    record = _mapping(raw, context)
    required = {
        "week_start",
        "week_end",
        "platform",
        "storefront",
        "source_scope",
        "device",
        "app_version",
        "metric",
        "value",
        "unit",
    }
    if not derived:
        required |= {"source_ref", "source_as_of", "notes"}
    missing = sorted(required - record.keys())
    if missing:
        raise ReportInputError(f"{context} is missing fields {missing}")
    if record["week_start"] != week_start or record["week_end"] != week_end:
        raise ReportInputError(f"{context} period differs from the weekly envelope")
    platform = record.get("platform")
    if platform not in {"apple", "google"}:
        raise ReportInputError(f"{context}.platform must be apple or google")
    for field in ("storefront", "source_scope", "device", "app_version", "metric"):
        if not isinstance(record.get(field), str) or not record[field]:
            raise ReportInputError(f"{context}.{field} must be non-empty")
    if "decision_eligible" in record and not isinstance(
        record["decision_eligible"], bool
    ):
        raise ReportInputError(f"{context}.decision_eligible must be boolean")
    metric = str(record["metric"])
    unit = record.get("unit")
    if derived:
        expected_unit = DERIVED_METRIC_UNITS.get(metric)
        if expected_unit is None:
            raise ReportInputError(f"{context} has unknown derived metric {metric!r}")
        if unit != expected_unit:
            raise ReportInputError(f"{context}.unit must be {expected_unit}")
        if (str(platform), metric) not in DERIVED_FORMULAS:
            raise ReportInputError(
                f"{context} derived metric is not valid for {platform}"
            )
        for field in ("numerator_metric", "denominator_metric"):
            if not isinstance(record.get(field), str) or not record[field]:
                raise ReportInputError(f"{context}.{field} must be non-empty")
    else:
        definition = metric_catalog.get(metric)
        if not isinstance(definition, dict):
            raise ReportInputError(f"{context} has unknown metric {metric!r}")
        if definition.get("platform") != platform:
            raise ReportInputError(f"{context} metric belongs to another platform")
        expected_unit = definition.get("unit")
        if unit != expected_unit:
            raise ReportInputError(f"{context}.unit must be {expected_unit}")
        if not isinstance(record.get("source_ref"), str) or not record["source_ref"]:
            raise ReportInputError(f"{context}.source_ref must be non-empty")
        source_as_of = _validated_date(
            record.get("source_as_of"), f"{context}.source_as_of"
        )
        if source_as_of < _validated_date(week_end, f"{context}.week_end"):
            raise ReportInputError(f"{context}.source_as_of predates week_end")
        if not isinstance(record.get("notes"), str):
            raise ReportInputError(f"{context}.notes must be a string")
        if metric in MODEL_VITAL_METRICS and (
            record.get("source_scope") != "device"
            or not is_concrete_device(record.get("device"))
        ):
            raise ReportInputError(
                f"{context} model vital requires a concrete device scope"
            )
    maximum = 100.0 if unit == "percent" else 5.0 if unit == "rating_5" else None
    _validated_number(
        record.get("value"),
        f"{context}.value",
        minimum=0,
        maximum=maximum,
        integer=unit == "count",
    )
    return (
        week_start,
        week_end,
        str(platform),
        str(record["storefront"]),
        str(record["source_scope"]),
        str(record["device"]),
        str(record["app_version"]),
        metric,
    )


def _validate_weekly_payload(
    weekly: dict[str, Any], expected_end: str
) -> dict[str, Any]:
    if weekly.get("schema_version") != SUPPORTED_SCHEMA_VERSION:
        raise ReportInputError(
            "weekly schema_version must be "
            f"{SUPPORTED_SCHEMA_VERSION}, got {weekly.get('schema_version')!r}"
        )
    start = _validated_date(weekly.get("week_start"), "weekly.week_start")
    end = _validated_date(weekly.get("week_end"), "weekly.week_end")
    if end - start != timedelta(days=6):
        raise ReportInputError("weekly envelope must contain seven inclusive days")
    if end.isoformat() != expected_end:
        raise ReportInputError(
            "weekly.week_end does not match evaluation.latest_weekly_period_end "
            f"({expected_end})"
        )
    source_file = weekly.get("source_file")
    if not isinstance(source_file, str) or not source_file:
        raise ReportInputError("weekly.source_file must be non-empty")
    for field in ("warnings", "decision_exclusions", "caveats"):
        _list(weekly.get(field), f"weekly.{field}")
    _mapping(weekly.get("coverage"), "weekly.coverage")
    catalog_payload = _mapping(
        load_json(GROWTH_ROOT / "metric-catalog.json"), "metric catalog"
    )
    if catalog_payload.get("schema_version") != SUPPORTED_SCHEMA_VERSION:
        raise ReportInputError("metric catalog schema_version is unsupported")
    metric_catalog = _mapping(catalog_payload.get("metrics"), "metric catalog.metrics")
    start_text = start.isoformat()
    end_text = end.isoformat()
    for field, derived in (("records", False), ("derived_metrics", True)):
        records = _list(weekly.get(field), f"weekly.{field}")
        if field == "records" and not records:
            raise ReportInputError("weekly.records must not be empty")
        seen: set[tuple[str, ...]] = set()
        for position, record in enumerate(records):
            key = _validate_weekly_record(
                record,
                context=f"weekly.{field}[{position}]",
                week_start=start_text,
                week_end=end_text,
                metric_catalog=metric_catalog,
                derived=derived,
            )
            if key in seen:
                raise ReportInputError(f"weekly.{field} contains duplicate scope {key}")
            seen.add(key)
    scope_fields = (
        "week_start",
        "week_end",
        "platform",
        "storefront",
        "source_scope",
        "device",
        "app_version",
    )
    raw_by_scope: dict[tuple[str, ...], dict[str, float]] = {}
    for record in weekly["records"]:
        scope = tuple(str(record[field]) for field in scope_fields)
        raw_by_scope.setdefault(scope, {})[str(record["metric"])] = float(
            record["value"]
        )
    derived_keys: set[tuple[tuple[str, ...], str]] = set()
    for position, record in enumerate(weekly["derived_metrics"]):
        scope = tuple(str(record[field]) for field in scope_fields)
        metric = str(record["metric"])
        numerator_metric, denominator_metric, multiplier = DERIVED_FORMULAS[
            (str(record["platform"]), metric)
        ]
        if (
            record.get("numerator_metric") != numerator_metric
            or record.get("denominator_metric") != denominator_metric
        ):
            raise ReportInputError(
                f"weekly.derived_metrics[{position}] formula metadata is invalid"
            )
        raw_values = raw_by_scope.get(scope, {})
        numerator = raw_values.get(numerator_metric)
        denominator = raw_values.get(denominator_metric)
        if numerator is None or denominator is None or denominator <= 0:
            raise ReportInputError(
                f"weekly.derived_metrics[{position}] lacks a valid raw ratio"
            )
        expected = round(numerator / denominator * multiplier, 2)
        if abs(float(record["value"]) - expected) > 0.001:
            raise ReportInputError(
                f"weekly.derived_metrics[{position}] conflicts with its raw ratio"
            )
        derived_keys.add((scope, metric))
    for scope, values in raw_by_scope.items():
        platform = scope[2]
        for (formula_platform, metric), (
            numerator_metric,
            denominator_metric,
            _,
        ) in DERIVED_FORMULAS.items():
            if formula_platform != platform:
                continue
            if (
                numerator_metric in values
                and denominator_metric in values
                and values[denominator_metric] > 0
                and (scope, metric) not in derived_keys
            ):
                raise ReportInputError(
                    f"weekly.derived_metrics is missing {metric} for scope {scope}"
                )
    return weekly


def _validated_weekly(
    evaluation: dict[str, Any],
    weekly: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, list[str]]:
    expected_end = evaluation.get("latest_weekly_period_end")
    if expected_end is not None:
        _validated_date(expected_end, "evaluation.latest_weekly_period_end")
    if expected_end is None:
        if weekly is None:
            return None, ["No validated seven-day UZ console import is referenced."]
        return None, [
            "A weekly import was supplied, but the evaluation does not reference a "
            "weekly period; all weekly KPI and quality results were suppressed."
        ]
    if weekly is None:
        return None, [
            f"The referenced weekly UZ console import for {expected_end} is missing; "
            "all weekly KPI and quality results were suppressed."
        ]
    try:
        return _validate_weekly_payload(weekly, expected_end), []
    except (OSError, ValueError, ReportInputError) as exc:
        return None, [
            f"The supplied weekly import was rejected ({exc}); all weekly KPI and "
            "quality results were suppressed."
        ]


def _driver_index(evaluation: dict[str, Any]) -> dict[str, dict[str, Any]]:
    drivers = _mapping(evaluation["drivers"], "evaluation.drivers")
    results: dict[str, dict[str, Any]] = {}
    for position, raw in enumerate(
        _list(drivers["results"], "evaluation.drivers.results")
    ):
        item = _mapping(raw, f"evaluation.drivers.results[{position}]")
        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier:
            raise ReportInputError(f"driver at index {position} is missing id")
        if identifier in results:
            raise ReportInputError(f"duplicate driver result {identifier}")
        results[identifier] = item
    return results


def _weekly_record_values(weekly: dict[str, Any] | None) -> dict[tuple[str, str], Any]:
    if weekly is None:
        return {}
    grouped: dict[tuple[str, str], list[Any]] = {}
    for raw in weekly.get("records", []):
        if not isinstance(raw, dict):
            continue
        if (
            raw.get("storefront") != "UZ"
            or raw.get("source_scope") != "summary"
            or raw.get("device") != "all"
            or raw.get("app_version") != "all"
            or raw.get("decision_eligible", True) is not True
        ):
            continue
        key = (str(raw.get("platform")), str(raw.get("metric")))
        grouped.setdefault(key, []).append(raw.get("value"))
    return {key: values[0] for key, values in grouped.items() if len(values) == 1}


def _weekly_metric_values(
    weekly: dict[str, Any],
    *,
    platform: str,
    metric: str,
    derived: bool = False,
) -> list[float]:
    source = weekly["derived_metrics"] if derived else weekly["records"]
    return [
        float(record["value"])
        for record in source
        if record.get("platform") == platform
        and record.get("metric") == metric
        and record.get("storefront") == "UZ"
        and record.get("source_scope") == "summary"
        and record.get("device") == "all"
        and record.get("app_version") == "all"
        and record.get("decision_eligible", True) is True
    ]


def _one_weekly_metric(
    weekly: dict[str, Any],
    *,
    platform: str,
    metric: str,
    derived: bool = False,
) -> float | None:
    values = _weekly_metric_values(
        weekly, platform=platform, metric=metric, derived=derived
    )
    return values[0] if len(values) == 1 else None


def _ratio_evidence(
    identifier: str,
    weekly_values: dict[tuple[str, str], Any],
) -> tuple[float | None, str | None]:
    definition = RATIO_METRICS.get(identifier)
    if definition is None:
        return None, None
    platform, numerator_id, denominator_id = definition
    numerator = _number(weekly_values.get((platform, numerator_id)))
    denominator = _number(weekly_values.get((platform, denominator_id)))
    if numerator is None or denominator is None:
        return None, None
    if denominator <= 0:
        return None, None
    derived = round(numerator / denominator * 100.0, 2)
    if derived > 100:
        return None, None
    return derived, f"{_format_number(numerator)} / {_format_number(denominator)}"


def _expected_driver_evidence(
    identifier: str,
    weekly: dict[str, Any],
    weekly_values: dict[tuple[str, str], Any],
) -> tuple[float | None, float | None, str | None]:
    if identifier in RATIO_METRICS:
        value, detail = _ratio_evidence(identifier, weekly_values)
        platform, _, denominator_metric = RATIO_METRICS[identifier]
        denominator = (
            _number(weekly_values.get((platform, denominator_metric)))
            if identifier == "google_store_listing_ctr_pct"
            else None
        )
        return value, denominator, detail
    direct: dict[str, tuple[str, str, bool]] = {
        "apple_conversion_rate_pct": (
            "apple",
            "apple_conversion_rate_pct",
            False,
        ),
        "google_store_listing_ctr_pct": (
            "google",
            "google_store_listing_ctr_pct",
            False,
        ),
        "apple_ratings_count": ("apple", "apple_ratings_count", False),
        "apple_average_rating": ("apple", "apple_average_rating", False),
        "google_ratings_count": ("google", "google_ratings_count", False),
        "google_average_rating": ("google", "google_average_rating", False),
    }
    platform, metric, derived = direct[identifier]
    value = _one_weekly_metric(
        weekly, platform=platform, metric=metric, derived=derived
    )
    if identifier == "google_store_listing_ctr_pct" and value is None:
        value = _one_weekly_metric(
            weekly,
            platform="google",
            metric="google_store_listing_ctr_pct_derived",
            derived=True,
        )
    denominator: float | None = None
    if identifier == "apple_conversion_rate_pct":
        denominator = _one_weekly_metric(
            weekly,
            platform="apple",
            metric="apple_unique_impressions",
        )
    elif identifier == "google_store_listing_ctr_pct":
        denominator = _one_weekly_metric(
            weekly,
            platform="google",
            metric="google_store_listing_visitors",
        )
    return value, denominator, None


def _values_match(left: Any, right: Any, tolerance: float = 0.001) -> bool:
    left_number = _number(left)
    right_number = _number(right)
    if left_number is None or right_number is None:
        return left_number is None and right_number is None
    return abs(left_number - right_number) <= tolerance


def _reconciled_drivers(
    evaluation: dict[str, Any],
    weekly: dict[str, Any] | None,
) -> tuple[dict[str, dict[str, Any]], dict[str, str], list[str], bool]:
    source = _driver_index(evaluation)
    effective = {identifier: deepcopy(item) for identifier, item in source.items()}
    details: dict[str, str] = {}
    gaps: list[str] = []
    if weekly is None:
        for item in effective.values():
            item["value"] = None
            item["status"] = "unknown"
            item["sufficient"] = False
            if "denominator" in item:
                item["denominator"] = None
        return effective, details, gaps, False

    exclusions = _mapping(evaluation["drivers"], "evaluation.drivers")[
        "decision_exclusions"
    ]
    if exclusions != weekly["decision_exclusions"]:
        gaps.append(
            "The evaluation decision exclusions differ from the linked weekly import."
        )
        for item in effective.values():
            item["value"] = None
            item["status"] = "conflict"
            item["sufficient"] = False
            if "denominator" in item:
                item["denominator"] = None
        return effective, details, gaps, True

    weekly_values = _weekly_record_values(weekly)
    conflict_found = False
    for identifier, item in effective.items():
        expected_value, expected_denominator, detail = _expected_driver_evidence(
            identifier, weekly, weekly_values
        )
        tolerance = 0.11 if identifier in PERCENT_DRIVER_IDS else 0.001
        conflicts: list[str] = []
        if not _values_match(item.get("value"), expected_value, tolerance):
            conflicts.append("actual")
        if "denominator" in item and not _values_match(
            item.get("denominator"), expected_denominator
        ):
            conflicts.append("denominator")
        if conflicts:
            conflict_found = True
            label = DRIVER_LABELS.get(identifier, identifier)
            gaps.append(
                f"{label} conflicts with the linked weekly "
                f"{', '.join(conflicts)} evidence; its result was suppressed."
            )
            item["value"] = None
            item["status"] = "conflict"
            item["sufficient"] = False
            if "denominator" in item:
                item["denominator"] = None
        elif detail is not None:
            details[identifier] = detail
    return effective, details, gaps, conflict_found


def _driver_cell(
    identifier: str,
    driver: dict[str, Any] | None,
    details: dict[str, str],
) -> str:
    if driver is None or _number(driver.get("value")) is None:
        return f"Unknown — {_format_status(driver.get('status') if driver else None)}"
    status = _format_status(driver.get("status"))
    rendered = f"{_format_percent(driver.get('value'))} — {status}"
    if identifier in details:
        rendered += f"; {details[identifier]}"
    if "minimum_denominator" in driver:
        denominator = _format_number(driver.get("denominator"))
        minimum = _format_number(driver.get("minimum_denominator"))
        rendered += f"; denominator {denominator} / minimum {minimum}"
    return rendered


def _ratings_cell(
    platform: str,
    drivers: dict[str, dict[str, Any]],
) -> str:
    count = drivers.get(f"{platform}_ratings_count")
    average = drivers.get(f"{platform}_average_rating")
    count_value = _format_number(count.get("value") if count else None)
    average_value = _format_number(average.get("value") if average else None)
    count_status = _format_status(count.get("status") if count else None)
    average_status = _format_status(average.get("status") if average else None)
    return (
        f"{count_value} ratings — {count_status}; "
        f"{average_value} / 5 — {average_status}"
    )


def _rank_surface(snapshot: dict[str, Any] | None, surface_id: str) -> dict[str, Any]:
    if snapshot is None:
        return {}
    surfaces = snapshot.get("surfaces", {})
    if surface_id == "apple.category":
        return surfaces.get("apple", {}).get("category", {})
    if surface_id.startswith("google.category."):
        profile = surface_id.removeprefix("google.category.")
        return surfaces.get("google", {}).get("category", {}).get(profile, {})
    return {}


def _rank_display(surface: dict[str, Any]) -> str:
    if surface.get("status") != "ok":
        return "Unknown"
    rank = surface.get("target_rank")
    if isinstance(rank, int) and not isinstance(rank, bool) and rank >= 1:
        return f"#{rank}"
    bound = surface.get("target_rank_bound")
    if isinstance(bound, str) and re.fullmatch(r">[1-9][0-9]*", bound):
        return bound
    return "Unknown"


def _comparison_index(
    evaluation: dict[str, Any],
    snapshot: dict[str, Any] | None,
    gaps: list[str],
) -> dict[str, dict[str, Any]]:
    if snapshot is None:
        return {}
    ranks = _mapping(evaluation["rank_improvement"], "evaluation.rank_improvement")
    if ranks.get("config_fingerprint") != snapshot.get("config_fingerprint"):
        gaps.append(
            "Rank comparison configuration differs from the accepted current "
            "snapshot; comparisons were suppressed."
        )
        return {}
    comparisons: dict[str, dict[str, Any]] = {}
    for raw in ranks.get("comparable_surfaces", []):
        if not isinstance(raw, dict):
            continue
        identifier = raw.get("surface_id")
        if not isinstance(identifier, str) or identifier not in dict(RANK_ROWS).values():
            continue
        surface = _rank_surface(snapshot, identifier)
        current_rank = surface.get("target_rank")
        if (
            raw.get("current_date") != snapshot.get("date")
            or isinstance(current_rank, bool)
            or not isinstance(current_rank, int)
            or raw.get("current_rank") != current_rank
        ):
            gaps.append(
                f"Rank comparison for {identifier} does not end at the accepted "
                "current observation; that comparison was suppressed."
            )
            continue
        comparisons[identifier] = raw
    return comparisons


def _rank_complete(snapshot: dict[str, Any] | None, surface_id: str) -> str:
    if snapshot is None:
        return "Unknown"
    statuses = snapshot.get("_report_surface_statuses", {})
    status = statuses.get(surface_id)
    return status.upper() if status in ALLOWED_RESULT_STATUSES else "Unknown"


def _target_text(driver: dict[str, Any] | None, *, rating: bool = False) -> str:
    if driver is None:
        return "Unknown"
    operator = str(driver.get("operator", "?"))
    target = _format_number(driver.get("target"))
    suffix = " / 5" if rating and target != "Unknown" else "%"
    return f"{operator} {target}{suffix}"


def _weekly_guardrail_values_by_metric(
    weekly: dict[str, Any], identifier: str
) -> dict[str, list[float]]:
    values_by_metric: dict[str, list[float]] = {}
    for metric_id in GUARDRAIL_METRIC_IDS[identifier]:
        values: list[float] = []
        for record in weekly["records"]:
            if (
                record.get("metric") != metric_id
                or record.get("decision_eligible", True) is not True
                or record.get("storefront")
                != ("ALL" if metric_id in POLICY_METRICS else "UZ")
                or record.get("app_version") != "all"
            ):
                continue
            if metric_id in MODEL_VITAL_METRICS:
                if record.get("source_scope") != "device" or not is_concrete_device(
                    record.get("device")
                ):
                    continue
            elif (
                record.get("source_scope") != "summary"
                or record.get("device") != "all"
            ):
                continue
            values.append(float(record["value"]))
        values_by_metric[metric_id] = values
    return values_by_metric


def _reconciled_metric_guardrails(
    evaluation: dict[str, Any],
    weekly: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], list[str], bool]:
    guardrails = _mapping(evaluation["guardrails"], "evaluation.guardrails")
    effective = [deepcopy(item) for item in guardrails["metric_guardrails"]]
    if weekly is None:
        for item in effective:
            item["values"] = []
            item["missing_metric_ids"] = list(
                GUARDRAIL_METRIC_IDS[str(item["id"])]
            )
            item["status"] = "unknown"
        return effective, [], False
    gaps: list[str] = []
    conflict_found = False
    for item in effective:
        identifier = str(item["id"])
        expected_by_metric = _weekly_guardrail_values_by_metric(weekly, identifier)
        expected = sorted(
            value
            for metric_id in GUARDRAIL_METRIC_IDS[identifier]
            for value in expected_by_metric[metric_id]
        )
        actual = sorted(float(value) for value in item["values"])
        expected_missing = [
            metric_id
            for metric_id in GUARDRAIL_METRIC_IDS[identifier]
            if not expected_by_metric[metric_id]
        ]
        actual_missing = item.get("missing_metric_ids")
        if len(expected) != len(actual) or any(
            abs(left - right) > 0.001
            for left, right in zip(expected, actual, strict=True)
        ) or actual_missing != expected_missing:
            conflict_found = True
            label = GUARDRAIL_LABELS.get(identifier, identifier)
            gaps.append(
                f"{label} conflicts with the linked weekly evidence; its result was "
                "suppressed."
            )
            item["values"] = []
            item["missing_metric_ids"] = list(GUARDRAIL_METRIC_IDS[identifier])
            item["status"] = "conflict"
    return effective, gaps, conflict_found


def _guardrail_values(item: dict[str, Any]) -> str:
    values = item.get("values")
    if not isinstance(values, list) or not values:
        return "Unknown"
    identifier = str(item.get("id", ""))
    formatter = _format_number if identifier == "open_policy_issues" else _format_percent
    return ", ".join(formatter(value) for value in values)


def _guardrail_requirement(item: dict[str, Any]) -> str:
    operator = str(item.get("operator", "?"))
    threshold = _format_number(item.get("threshold"))
    if str(item.get("id")) != "open_policy_issues" and threshold != "Unknown":
        threshold += "%"
    return f"{operator} {threshold}"


def _unknown_driver_detail(item: dict[str, Any]) -> str | None:
    if item.get("status") != "unknown":
        return None
    identifier = str(item.get("id", "unknown_driver"))
    label = DRIVER_LABELS.get(identifier, identifier)
    if _number(item.get("value")) is None:
        return f"{label}: actual is missing"
    if "minimum_denominator" in item:
        denominator = _number(item.get("denominator"))
        minimum = _format_number(item.get("minimum_denominator"))
        if denominator is None:
            return f"{label}: denominator is missing (minimum {minimum})"
        return (
            f"{label}: denominator {_format_number(denominator)} is below minimum "
            f"{minimum}"
        )
    return f"{label}: evidence is insufficient"


def _next_actions(
    evaluation: dict[str, Any],
    as_of: date,
    drivers: dict[str, dict[str, Any]],
    metric_guardrails: list[dict[str, Any]],
) -> list[tuple[str, str, date]]:
    guardrails = _mapping(evaluation["guardrails"], "evaluation.guardrails")
    actions: list[tuple[str, str, date]] = []
    for raw in guardrails["scale_gates"]:
        item = _mapping(raw, "scale gate")
        if item.get("status") == "pass":
            continue
        action = GATE_ACTIONS.get(str(item.get("id")))
        if action:
            actions.append((action[1], action[0], as_of + timedelta(days=7)))
        if len(actions) == 3:
            return actions

    unknown_critical = [
        item
        for item in metric_guardrails
        if isinstance(item, dict)
        and item.get("critical") is True
        and item.get("status") != "pass"
    ]
    if unknown_critical and len(actions) < 3:
        names = ", ".join(
            GUARDRAIL_LABELS.get(str(item.get("id")), str(item.get("id")))
            for item in unknown_critical
        )
        actions.append(
            (
                "Import or reconcile same-scope console evidence for the critical "
                f"quality guardrails: {names}.",
                "Growth operations",
                as_of + timedelta(days=7),
            )
        )

    if (
        any(
            item.get("status") in {"unknown", "conflict"}
            for item in drivers.values()
        )
        and len(actions) < 3
    ):
        actions.append(
            (
                "Import one validated seven-day UZ console export so KPI actuals and "
                "denominators can be evaluated.",
                "Growth operations",
                as_of + timedelta(days=7),
            )
        )

    goal = _mapping(evaluation["top10_goal"], "evaluation.top10_goal")
    if goal.get("goal_achieved") is not True and len(actions) < 3:
        actions.append(
            (
                "Capture the next complete public-rank snapshot and rerun the "
                "evaluation without changing the monitor configuration.",
                "Growth operations",
                as_of + timedelta(days=1),
            )
        )
    return actions[:3]


def render_weekly_report(
    evaluation: dict[str, Any],
    *,
    evaluation_source: str,
    rank_snapshot: dict[str, Any] | None = None,
    rank_source: str = "Not available",
    weekly: dict[str, Any] | None = None,
    weekly_source: str = "Not available",
) -> str:
    """Return Markdown derived only from supplied, locally validated evidence."""

    as_of = _validate_evaluation(evaluation)
    rank_snapshot, evidence_gaps = _validated_rank_snapshot(
        evaluation, rank_snapshot
    )
    weekly, weekly_gaps = _validated_weekly(evaluation, weekly)
    evidence_gaps.extend(weekly_gaps)
    drivers, driver_details, driver_gaps, driver_conflict = _reconciled_drivers(
        evaluation, weekly
    )
    evidence_gaps.extend(driver_gaps)
    metric_guardrails, guardrail_gaps, guardrail_conflict = (
        _reconciled_metric_guardrails(evaluation, weekly)
    )
    evidence_gaps.extend(guardrail_gaps)
    comparisons = _comparison_index(evaluation, rank_snapshot, evidence_gaps)

    decision = _mapping(
        evaluation["decision_90_day_rule"],
        "evaluation.decision_90_day_rule",
    )
    decision_id = str(decision.get("decision", ""))
    verdict = DECISION_LABELS.get(decision_id, "INSUFFICIENT DATA")
    decision_reason = _escape(decision.get("reason"))
    linked_evidence_incomplete = weekly is None or rank_snapshot is None
    if (driver_conflict or guardrail_conflict or linked_evidence_incomplete) and verdict != "HOLD":
        verdict = "INSUFFICIENT DATA"
        decision_reason = (
            "Linked weekly or rank evidence is missing, rejected, or conflicts with "
            "the evaluation; affected conclusions are suppressed."
        )
    goal = _mapping(evaluation["top10_goal"], "evaluation.top10_goal")
    current_streak = (
        _format_number(goal.get("current_streak_days"))
        if rank_snapshot is not None
        else "Unknown"
    )
    required_streak = _format_number(goal.get("required_days"))
    if rank_snapshot is None:
        goal_status = "not verifiable from the accepted current evidence"
    else:
        goal_status = (
            "achieved" if goal.get("goal_achieved") is True else "not achieved"
        )
    paid_status = (
        "authorized"
        if decision.get("paid_spend_authorized") is True
        else "not authorized"
    )
    external_status = (
        "authorized"
        if decision.get("external_action_authorized") is True
        else "not authorized"
    )

    weekly_acceptance = "ACCEPTED" if weekly is not None else "NOT ACCEPTED"
    rank_acceptance = "ACCEPTED" if rank_snapshot is not None else "NOT ACCEPTED"
    kpi_period = (
        f"{weekly['week_start']} through {weekly['week_end']}"
        if weekly is not None
        else "Unknown"
    )
    comparison_dates = sorted(
        {
            str(value)
            for item in comparisons.values()
            for value in (item.get("baseline_date"), item.get("current_date"))
            if value
        }
    )
    comparison_provenance = (
        ", ".join(comparison_dates) if comparison_dates else "Unknown"
    )
    goal_evidence = (
        "complete"
        if rank_snapshot is not None
        and rank_snapshot.get("evaluation", {}).get("complete") is True
        else "incomplete"
        if rank_snapshot is not None
        else "unknown"
    )

    lines = [
        f"# Nimbo weekly growth review — {as_of.isoformat()}",
        "",
        f"Report as of: `{as_of.isoformat()}` (`{TIMEZONE}`)",
        f"KPI evidence period: `{kpi_period}`",
        f"Evaluation artifact: `{_escape(evaluation_source)}`",
        f"Weekly evidence: `{_escape(weekly_source)}` — {weekly_acceptance}",
        f"Current rank evidence: `{_escape(rank_source)}` — {rank_acceptance}",
        f"Rank comparison observation dates: `{comparison_provenance}`",
        f"Goal evidence completeness: `{goal_evidence}`",
        "",
        "## Executive summary",
        "",
        f"**{verdict}.** {decision_reason}",
        "",
        (
            f"The simultaneous Top-10 goal is {goal_status}: the current verified "
            f"streak is **{current_streak} / {required_streak} complete days**. "
            f"Paid spend is **{paid_status}**; external action is "
            f"**{external_status}**."
        ),
        "",
        "## KPI status",
        "",
        "| Metric | Apple | Google | Target | Evidence / caveat |",
        "| --- | --- | --- | --- | --- |",
    ]

    apple_conversion = drivers.get("apple_conversion_rate_pct")
    google_conversion = drivers.get("google_store_listing_ctr_pct")
    apple_conversion_cell = _driver_cell(
        "apple_conversion_rate_pct",
        apple_conversion,
        driver_details,
    )
    google_conversion_cell = _driver_cell(
        "google_store_listing_ctr_pct",
        google_conversion,
        driver_details,
    )
    lines.append(
        "| Conversion / listing CTR | "
        f"{_escape(apple_conversion_cell)} | "
        f"{_escape(google_conversion_cell)} "
        "| Apple "
        f"{_escape(_target_text(apple_conversion))}; Google "
        f"{_escape(_target_text(google_conversion))} | "
        "Conversion status is valid only after its recorded minimum denominator. |"
    )

    for label, suffix in (
        ("First launch / install", "first_launch_rate_pct"),
        ("D7 retention", "d7_retention_pct"),
        ("DAU / MAU", "dau_mau_pct"),
    ):
        apple_id = f"apple_{suffix}"
        google_id = f"google_{suffix}"
        apple_driver = drivers.get(apple_id)
        google_driver = drivers.get(google_id)
        target = _target_text(apple_driver or google_driver)
        lines.append(
            f"| {label} | "
            f"{_escape(_driver_cell(apple_id, apple_driver, driver_details))} | "
            f"{_escape(_driver_cell(google_id, google_driver, driver_details))} | "
            f"{_escape(target)} | Exact numerator / denominator is shown only "
            "from the referenced weekly import. |"
        )

    ratings_target = (
        f"count {_target_text(drivers.get('apple_ratings_count')).removesuffix('%')}; "
        f"average {_target_text(drivers.get('apple_average_rating'), rating=True)}"
    )
    lines.extend(
        [
            "| Ratings | "
            f"{_escape(_ratings_cell('apple', drivers))} | "
            f"{_escape(_ratings_cell('google', drivers))} | "
            f"{_escape(ratings_target)} | Point-in-time storefront values; "
            "not additive across breakdowns. |",
            "",
            "## Rank and search",
            "",
            "| Surface | Current | Comparison observation | Change | Complete? |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )

    for label, surface_id in RANK_ROWS:
        surface = _rank_surface(rank_snapshot, surface_id)
        comparison = comparisons.get(surface_id)
        if comparison:
            comparison_text = (
                f"#{_format_number(comparison.get('baseline_rank'))} "
                f"({comparison.get('baseline_date', 'date unknown')})"
            )
            change_text = _format_number(comparison.get("improvement"))
        else:
            comparison_text = "Unknown"
            change_text = "Unknown"
        lines.append(
            f"| {label} | {_escape(_rank_display(surface))} | "
            f"{_escape(comparison_text)} | {_escape(change_text)} | "
            f"{_rank_complete(rank_snapshot, surface_id)} |"
        )

    snapshot_evaluation = (
        rank_snapshot.get("evaluation", {}) if rank_snapshot is not None else {}
    )
    generic_queries = snapshot_evaluation.get("google_generic_top10_queries")
    generic_count = snapshot_evaluation.get("google_generic_top10_query_count")
    if isinstance(generic_queries, list) and generic_queries:
        generic_text = f"{_format_number(generic_count)} ({', '.join(map(str, generic_queries))})"
    elif _number(generic_count) is not None:
        generic_text = _format_number(generic_count)
    else:
        generic_text = "Unknown"
    generic_status = (
        rank_snapshot.get("_report_generic_status")
        if rank_snapshot is not None
        else None
    )
    generic_complete = (
        str(generic_status).upper()
        if generic_status in ALLOWED_RESULT_STATUSES
        else "Unknown"
    )
    lines.extend(
        [
            "| Generic queries in Top 10 | "
            f"{_escape(generic_text)} | Unknown | Unknown | {generic_complete} |",
            "",
            "Current verified Top-10 streak: "
            f"**{current_streak} / {required_streak} complete days**.",
            "",
            "Rank comparisons include only exact numeric observations under the "
            "current monitor configuration. Bounded absences are not converted "
            "into synthetic ranks.",
            "",
            "## Scale gates",
            "",
            "| Gate | Actual | Evaluation | Required | Evidence / required action |",
            "| --- | --- | --- | --- | --- |",
        ]
    )

    guardrails = _mapping(evaluation["guardrails"], "evaluation.guardrails")
    for raw in guardrails["scale_gates"]:
        item = _mapping(raw, "scale gate")
        identifier = str(item.get("id", "unknown_gate"))
        reason = item.get("reason") or "No reason is recorded."
        if item.get("status") == "pass":
            action_text = "Maintain dated evidence and recheck at the next cutoff."
        else:
            action = GATE_ACTIONS.get(identifier)
            action_text = (
                action[1]
                if action
                else "Record a reviewed action for this gate."
            )
        lines.append(
            f"| {_escape(GATE_LABELS.get(identifier, identifier))} | "
            f"{_escape(item.get('actual'))} | {_format_status(item.get('status'))} | "
            f"{_escape(item.get('required'))} | {_escape(reason)} Required action: "
            f"{_escape(action_text)} |"
        )

    lines.extend(
        [
            "",
            "## Quality guardrails",
            "",
            "| Guardrail | Actual | Requirement | Status | Evidence policy |",
            "| --- | ---: | ---: | --- | --- |",
        ]
    )
    for raw in metric_guardrails:
        item = _mapping(raw, "metric guardrail")
        identifier = str(item.get("id", "unknown_guardrail"))
        lines.append(
            f"| {_escape(GUARDRAIL_LABELS.get(identifier, identifier))} | "
            f"{_escape(_guardrail_values(item))} | "
            f"{_escape(_guardrail_requirement(item))} | "
            f"{_format_status(item.get('status'))} | "
            f"{_escape(item.get('unknown_policy'))} |"
        )

    unknown_drivers = [
        detail
        for item in drivers.values()
        if (detail := _unknown_driver_detail(item)) is not None
    ]
    if unknown_drivers:
        evidence_gaps.append("KPI evidence: " + "; ".join(unknown_drivers) + ".")
    unknown_guardrails = [
        GUARDRAIL_LABELS.get(str(item.get("id")), str(item.get("id")))
        for item in metric_guardrails
        if isinstance(item, dict) and item.get("status") == "unknown"
    ]
    if unknown_guardrails:
        evidence_gaps.append(
            "Unknown quality guardrails: " + ", ".join(unknown_guardrails) + "."
        )
    exclusions = _mapping(evaluation["drivers"], "evaluation.drivers").get(
        "decision_exclusions", []
    )
    if exclusions:
        evidence_gaps.append(
            f"{len(exclusions)} driver conflict(s) are excluded from decision eligibility."
        )
    if rank_snapshot is not None:
        reasons = snapshot_evaluation.get("reasons")
        if isinstance(reasons, list) and reasons:
            evidence_gaps.append(
                "Rank evidence is incomplete for the goal: "
                + "; ".join(_escape(reason) for reason in reasons)
                + "."
            )

    lines.extend(["", "## Unknown or missing evidence", ""])
    if evidence_gaps:
        lines.extend(f"- {_escape(gap)}" for gap in evidence_gaps)
    else:
        lines.append("- No unknown or missing evidence is recorded in the supplied inputs.")

    lines.extend(
        [
            "",
            "## Next actions",
            "",
            "| Priority | Action | Suggested owner | Suggested due |",
            "| ---: | --- | --- | --- |",
        ]
    )
    actions = _next_actions(evaluation, as_of, drivers, metric_guardrails)
    if actions:
        for position, (action, owner, due) in enumerate(actions, start=1):
            lines.append(
                f"| {position} | {_escape(action)} | {_escape(owner)} | {due.isoformat()} |"
            )
    else:
        lines.append(
            "| 1 | No additional action is derived from this evaluation. | "
            "Unassigned | Not set |"
        )

    lines.extend(
        [
            "",
            "Suggested owners and due dates are operating recommendations calculated "
            "from the report date, not recorded commitments.",
            "",
            "## Operating boundary",
            "",
            "This review does not send outreach, publish store changes, authorize "
            "spend, switch provider infrastructure, or claim a release or rank "
            "outcome that is not present in the supplied evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def _default_sources(
    evaluation: dict[str, Any],
) -> tuple[Path | None, Path | None]:
    as_of = _validate_evaluation(evaluation)
    rank_path = GROWTH_ROOT / "data/public-rank" / f"{as_of.isoformat()}.json"
    weekly_end = evaluation.get("latest_weekly_period_end")
    weekly_path = (
        GROWTH_ROOT / "data/weekly" / f"{weekly_end}.json"
        if isinstance(weekly_end, str) and weekly_end
        else None
    )
    return (
        rank_path if rank_path.is_file() else None,
        weekly_path if weekly_path and weekly_path.is_file() else None,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evaluation", type=Path)
    parser.add_argument("--rank-snapshot", type=Path)
    parser.add_argument("--weekly", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--replace", action="store_true")
    return parser


def _write_report_atomic(output: Path, report: str, *, replace: bool) -> None:
    """Write one complete report without a check-then-clobber race."""

    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.", suffix=".tmp", dir=output.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(report)
            handle.flush()
            os.fsync(handle.fileno())
        if replace:
            os.replace(temporary, output)
        else:
            os.link(temporary, output)
            temporary.unlink()
    finally:
        temporary.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        evaluation = _mapping(load_json(args.evaluation), "evaluation")
        as_of = _validate_evaluation(evaluation)
        default_rank, default_weekly = _default_sources(evaluation)
        rank_path = args.rank_snapshot or default_rank
        weekly_path = args.weekly or default_weekly
        if args.rank_snapshot is not None and not args.rank_snapshot.is_file():
            raise ReportInputError(
                f"explicit public-rank snapshot does not exist: {args.rank_snapshot}"
            )
        if args.weekly is not None and not args.weekly.is_file():
            raise ReportInputError(f"explicit weekly import does not exist: {args.weekly}")
        rank_snapshot = _safe_load_optional(rank_path, "public-rank snapshot")
        weekly = _safe_load_optional(weekly_path, "weekly import")
        report = render_weekly_report(
            evaluation,
            evaluation_source=_source_label(args.evaluation),
            rank_snapshot=rank_snapshot,
            rank_source=_source_label(rank_path),
            weekly=weekly,
            weekly_source=_source_label(weekly_path),
        )
    except (OSError, ValueError, ReportInputError) as exc:
        print(f"Weekly report generation failed: {exc}", file=sys.stderr)
        return 1

    output = args.output or GROWTH_ROOT / "reports" / f"weekly-{as_of.isoformat()}.md"
    try:
        _write_report_atomic(output, report, replace=args.replace)
    except FileExistsError:
        print(f"weekly report already exists: {output}; pass --replace", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"weekly report write failed: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {output}.")
    return 0


def verdict_summary(evaluation: dict[str, Any]) -> str:
    decision = evaluation.get("decision_90_day_rule", {}).get("decision")
    return DECISION_LABELS.get(str(decision), "INSUFFICIENT DATA")


if __name__ == "__main__":
    raise SystemExit(main())
