#!/usr/bin/env python3
"""Validate and normalize a weekly App Store Connect / Play Console metric CSV."""

from __future__ import annotations

import argparse
import csv
import math
import re
import sys
from collections import defaultdict
from datetime import timedelta
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
    parse_date,
    write_json,
)


COLUMNS = [
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
    "source_ref",
    "source_as_of",
    "notes",
]


class ImportValidationError(ValueError):
    """The canonical weekly import is not safe to use."""


def _numeric_value(raw: str, unit: str, row_number: int) -> int | float:
    try:
        value = float(raw)
    except ValueError as exc:
        raise ImportValidationError(f"row {row_number}: value is not numeric") from exc
    if not math.isfinite(value) or value < 0:
        raise ImportValidationError(
            f"row {row_number}: value must be finite and non-negative"
        )
    if unit == "count":
        if not value.is_integer():
            raise ImportValidationError(f"row {row_number}: count must be an integer")
        return int(value)
    if unit == "percent" and value > 100:
        raise ImportValidationError(f"row {row_number}: percent exceeds 100")
    if unit == "rating_5" and value > 5:
        raise ImportValidationError(f"row {row_number}: rating exceeds 5")
    return value


def _scope_key(record: dict[str, Any]) -> tuple[str, ...]:
    return (
        record["week_start"],
        record["week_end"],
        record["platform"],
        record["storefront"],
        record["source_scope"],
        record["device"],
        record["app_version"],
    )


def _scope_payload(key: tuple[str, ...]) -> dict[str, str]:
    return dict(
        zip(
            (
                "week_start",
                "week_end",
                "platform",
                "storefront",
                "source_scope",
                "device",
                "app_version",
            ),
            key,
            strict=True,
        )
    )


def _derive(
    records: list[dict[str, Any]], metric_catalog: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, ...], dict[str, int | float]] = defaultdict(dict)
    grouped_records: dict[tuple[str, ...], dict[str, dict[str, Any]]] = defaultdict(dict)
    for record in records:
        grouped[_scope_key(record)][record["metric"]] = record["value"]
        grouped_records[_scope_key(record)][record["metric"]] = record

    derived: list[dict[str, Any]] = []
    warnings: list[str] = []
    decision_exclusions: list[dict[str, Any]] = []

    def ratio(
        values: dict[str, int | float], numerator: str, denominator: str
    ) -> float | None:
        if numerator not in values or denominator not in values:
            return None
        denominator_value = values[denominator]
        if denominator_value == 0:
            if values[numerator] > 0:
                raise ImportValidationError(
                    f"scope {_scope_payload(key)}: {numerator} is positive while "
                    f"{denominator} is zero"
                )
            return None
        return round(float(values[numerator]) / float(denominator_value) * 100, 2)

    for key, values in sorted(grouped.items()):
        platform = key[2]
        candidates: list[tuple[str, str, str, str, str | None]] = []
        if platform == "google":
            candidates.extend(
                [
                    (
                        "google_store_listing_ctr_pct_derived",
                        "google_unique_user_install_clicks",
                        "google_store_listing_visitors",
                        "percent",
                        "google_store_listing_ctr_pct",
                    ),
                    (
                        "first_launch_rate_pct",
                        "google_first_launches",
                        "google_installations",
                        "percent",
                        None,
                    ),
                    (
                        "d7_retention_pct",
                        "google_d7_retained",
                        "google_d7_eligible",
                        "percent",
                        None,
                    ),
                    (
                        "dau_mau_pct",
                        "google_average_daily_active_users_30d",
                        "google_monthly_active_users",
                        "percent",
                        None,
                    ),
                ]
            )
        if platform == "apple":
            candidates.extend(
                [
                    (
                        "first_launch_rate_pct",
                        "apple_first_launches",
                        "apple_installations",
                        "percent",
                        None,
                    ),
                    (
                        "d7_retention_pct",
                        "apple_d7_retained",
                        "apple_d7_eligible",
                        "percent",
                        None,
                    ),
                    (
                        "dau_mau_pct",
                        "apple_average_daily_active_devices_30d",
                        "apple_active_devices_30d",
                        "percent",
                        None,
                    ),
                    (
                        "crashes_per_1000_sessions",
                        "apple_crashes",
                        "apple_sessions",
                        "per_1000_sessions",
                        None,
                    ),
                ]
            )
        for metric, numerator, denominator, unit, reported_metric in candidates:
            value = ratio(values, numerator, denominator)
            if value is None:
                continue
            if metric == "crashes_per_1000_sessions":
                value = round(value * 10, 2)
            if unit == "percent" and value > 100:
                raise ImportValidationError(
                    f"scope {_scope_payload(key)}: derived {metric} is {value}%, "
                    "above the possible 100% maximum"
                )

            derived_record = {
                **_scope_payload(key),
                "metric": metric,
                "value": value,
                "unit": unit,
                "numerator_metric": numerator,
                "denominator_metric": denominator,
            }
            derived.append(derived_record)

            if reported_metric is None or reported_metric not in values:
                continue
            definition = metric_catalog[reported_metric]
            tolerance = definition.get(
                "reported_derived_tolerance_percentage_points"
            )
            if not isinstance(tolerance, (int, float)) or tolerance < 0:
                raise ImportValidationError(
                    f"metric catalog {reported_metric}: missing non-negative "
                    "reported_derived_tolerance_percentage_points"
                )
            reported_value = float(values[reported_metric])
            if abs(reported_value - value) <= float(tolerance):
                continue
            reason = (
                f"reported {reported_metric} {reported_value}% differs from derived "
                f"{value}% by more than {tolerance} percentage points"
            )
            grouped_records[key][reported_metric]["decision_eligible"] = False
            derived_record["decision_eligible"] = False
            warnings.append(f"scope {key}: {reason}; excluded from decisions")
            decision_exclusions.append(
                {
                    "scope": _scope_payload(key),
                    "metrics": [reported_metric, metric],
                    "reason": reason,
                }
            )
    return derived, warnings, decision_exclusions


def import_csv(path: Path, catalog: dict[str, Any]) -> dict[str, Any]:
    metric_catalog = catalog["metrics"]
    records: list[dict[str, Any]] = []
    failures: list[str] = []
    duplicate_keys: set[tuple[str, ...]] = set()
    periods: set[tuple[str, str]] = set()

    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != COLUMNS:
            raise ImportValidationError(
                f"expected exact columns {COLUMNS}, got {reader.fieldnames}"
            )
        for row_number, raw in enumerate(reader, start=2):
            try:
                row = {key: (value or "").strip() for key, value in raw.items()}
                missing = [column for column in COLUMNS[:-1] if not row[column]]
                if missing:
                    raise ImportValidationError(
                        f"row {row_number}: missing required {', '.join(missing)}"
                    )
                week_start = parse_date(row["week_start"])
                week_end = parse_date(row["week_end"])
                if week_end - week_start != timedelta(days=6):
                    raise ImportValidationError(
                        f"row {row_number}: weekly window must be seven inclusive days"
                    )
                source_as_of = parse_date(row["source_as_of"])
                if source_as_of < week_end:
                    raise ImportValidationError(
                        f"row {row_number}: source_as_of predates week_end"
                    )
                if row["platform"] not in {"apple", "google"}:
                    raise ImportValidationError(
                        f"row {row_number}: platform must be apple or google"
                    )
                if not re.fullmatch(r"(?:[A-Z]{2}|ALL)", row["storefront"]):
                    raise ImportValidationError(
                        f"row {row_number}: storefront must be ISO alpha-2 or ALL"
                    )
                definition = metric_catalog.get(row["metric"])
                if definition is None:
                    raise ImportValidationError(
                        f"row {row_number}: unknown metric {row['metric']!r}"
                    )
                if definition["platform"] != row["platform"]:
                    raise ImportValidationError(
                        f"row {row_number}: metric belongs to {definition['platform']}"
                    )
                if definition["unit"] != row["unit"]:
                    raise ImportValidationError(
                        f"row {row_number}: unit must be {definition['unit']}"
                    )
                if row["metric"] in POLICY_METRICS and (
                    row["storefront"] != "ALL"
                    or row["source_scope"] != "summary"
                    or row["device"] != "all"
                    or row["app_version"] != "all"
                ):
                    raise ImportValidationError(
                        f"row {row_number}: {row['metric']} requires storefront=ALL, "
                        "source_scope=summary, device=all, and app_version=all"
                    )
                if row["metric"] in MODEL_VITAL_METRICS and (
                    row["source_scope"] != "device"
                    or not is_concrete_device(row["device"])
                ):
                    raise ImportValidationError(
                        f"row {row_number}: {row['metric']} requires "
                        "source_scope=device and a concrete device model"
                    )
                value = _numeric_value(row["value"], row["unit"], row_number)
                record: dict[str, Any] = {
                    **{key: row[key] for key in COLUMNS if key != "value"},
                    "value": value,
                }
                key = _scope_key(record) + (record["metric"],)
                if key in duplicate_keys:
                    raise ImportValidationError(
                        f"row {row_number}: duplicate metric for identical scope"
                    )
                duplicate_keys.add(key)
                periods.add((row["week_start"], row["week_end"]))
                records.append(record)
            except ImportValidationError as exc:
                failures.append(str(exc))

    if failures:
        raise ImportValidationError("\n".join(failures))
    if not records:
        raise ImportValidationError("input contains no metric rows")
    if len(periods) != 1:
        raise ImportValidationError("one import file must contain exactly one weekly period")

    derived, warnings, decision_exclusions = _derive(records, metric_catalog)
    week_start, week_end = next(iter(periods))
    present_dimensions = {
        "platforms": sorted({record["platform"] for record in records}),
        "storefronts": sorted({record["storefront"] for record in records}),
        "source_scopes": sorted({record["source_scope"] for record in records}),
        "devices": sorted({record["device"] for record in records}),
        "app_versions": sorted({record["app_version"] for record in records}),
    }
    return {
        "schema_version": 1,
        "week_start": week_start,
        "week_end": week_end,
        "source_file": path.name,
        "records": records,
        "derived_metrics": derived,
        "warnings": warnings,
        "decision_exclusions": decision_exclusions,
        "coverage": present_dimensions,
        "caveats": [
            "Usage and retention populations can differ by store and opt-in status.",
            "Point-in-time ratings and policy values are not additive across breakdown rows.",
            "Missing metrics are unknown, not zero.",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument(
        "--catalog", type=Path, default=GROWTH_ROOT / "metric-catalog.json"
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--replace", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = import_csv(args.input, load_json(args.catalog))
    except (OSError, ImportValidationError) as exc:
        print(f"Weekly import failed:\n{exc}", file=sys.stderr)
        return 1
    output = args.output or GROWTH_ROOT / "data/weekly" / f"{payload['week_end']}.json"
    if output.exists() and not args.replace:
        print(f"weekly import already exists: {output}; pass --replace", file=sys.stderr)
        return 2
    write_json(output, payload)
    print(
        f"Wrote {output}: {len(payload['records'])} records, "
        f"{len(payload['derived_metrics'])} derived metrics, "
        f"{len(payload['warnings'])} warnings."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
