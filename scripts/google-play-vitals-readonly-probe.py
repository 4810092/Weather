#!/usr/bin/env python3
"""Export one complete, public UZ Google Play vitals window as canonical CSV.

The Google query RPCs use POST but are semantically read-only. Online requests
are restricted to the exact Nimbo crash/ANR metric-set resources. Credentials
must be an ephemeral access token and provider response bodies are never logged.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from typing import Any


PACKAGE = "uz.ganikhodjaev.weather"
ROOT = "https://playdeveloperreporting.googleapis.com"
API_VERSION = "v1beta1"
TIMEZONE = "America/Los_Angeles"
COUNTRY = "UZ"
COHORT = "OS_PUBLIC"
TOKEN_ENV = "NIMBO_GOOGLE_PLAY_REPORTING_ACCESS_TOKEN"
MAX_RESPONSE_BYTES = 1024 * 1024
MAX_PAGES = 10
PAGE_SIZE = 100000
CSV_COLUMNS = (
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
)

SETS = {
    "crash": {
        "resource": "crashRateMetricSet",
        "provider_metric": "userPerceivedCrashRate7dUserWeighted",
        "summary_metric": "android_user_perceived_crash_rate_pct",
        "phone_metric": "android_phone_model_crash_rate_pct",
        "wear_metric": "wear_model_crash_rate_pct",
    },
    "anr": {
        "resource": "anrRateMetricSet",
        "provider_metric": "userPerceivedAnrRate7dUserWeighted",
        "summary_metric": "android_user_perceived_anr_rate_pct",
        "phone_metric": "android_phone_model_anr_rate_pct",
        "wear_metric": "wear_model_anr_rate_pct",
    },
}


class ProbeError(RuntimeError):
    """The provider evidence is unsafe or incomplete."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _resource_url(resource: str, *, query: bool = False) -> str:
    suffix = ":query" if query else ""
    return f"{ROOT}/{API_VERSION}/apps/{PACKAGE}/{resource}{suffix}"


def _allowed_request(method: str, url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "playdeveloperreporting.googleapis.com":
        return False
    if parsed.params or parsed.query or parsed.fragment:
        return False
    metadata_paths = {
        urllib.parse.urlparse(_resource_url(item["resource"])).path
        for item in SETS.values()
    }
    query_paths = {
        urllib.parse.urlparse(_resource_url(item["resource"], query=True)).path
        for item in SETS.values()
    }
    return (method == "GET" and parsed.path in metadata_paths) or (
        method == "POST" and parsed.path in query_paths
    )


def _validate_query_payload(url: str, payload: dict[str, Any]) -> None:
    definition = next(
        (
            item
            for item in SETS.values()
            if url == _resource_url(str(item["resource"]), query=True)
        ),
        None,
    )
    if definition is None:
        raise ProbeError("query body has no matching allowlisted metric set")
    required_keys = {
        "timelineSpec",
        "dimensions",
        "metrics",
        "filter",
        "pageSize",
        "userCohort",
    }
    if set(payload) not in (required_keys, required_keys | {"pageToken"}):
        raise ProbeError("query body keys differ from the exact read-only contract")
    if payload.get("dimensions") not in (
        ["countryCode"],
        ["countryCode", "deviceType", "deviceModel"],
    ):
        raise ProbeError("query dimensions differ from the exact UZ evidence contract")
    if payload.get("metrics") != [definition["provider_metric"]]:
        raise ProbeError("query metric differs from the exact user-perceived contract")
    if (
        payload.get("filter") != 'countryCode = "UZ"'
        or payload.get("pageSize") != PAGE_SIZE
        or payload.get("userCohort") != COHORT
    ):
        raise ProbeError("query scope differs from the exact public UZ contract")
    timeline = payload.get("timelineSpec")
    if not isinstance(timeline, dict) or set(timeline) != {
        "aggregationPeriod",
        "startTime",
        "endTime",
    }:
        raise ProbeError("query timeline differs from the exact daily contract")
    if timeline.get("aggregationPeriod") != "DAILY":
        raise ProbeError("query aggregation must remain DAILY")
    start = _provider_datetime(timeline.get("startTime"), "query startTime")
    end = _provider_datetime(timeline.get("endTime"), "query endTime")
    if end - start != timedelta(days=1):
        raise ProbeError("query timeline must contain exactly one provider day")
    page_token = payload.get("pageToken")
    if page_token is not None and (
        not isinstance(page_token, str) or not page_token or len(page_token) > 4096
    ):
        raise ProbeError("query page token is invalid")


def request_json(
    method: str,
    url: str,
    token: str,
    *,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not _allowed_request(method, url):
        raise ProbeError("refusing request outside the exact read-only allowlist")
    if method == "POST" and payload is None:
        raise ProbeError("query RPC requires an allowlisted JSON body")
    if method == "GET" and payload is not None:
        raise ProbeError("metric-set metadata GET cannot carry a body")
    if payload is not None:
        _validate_query_payload(url, payload)
    data = None
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "nimbo-google-play-vitals-readonly/1",
    }
    if payload is not None:
        data = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, headers=headers, data=data, method=method)
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=30) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise ProbeError("provider response exceeded the safe size limit")
            if response.status != 200:
                raise ProbeError(f"provider request failed with HTTP {response.status}")
    except urllib.error.HTTPError as exc:
        raise ProbeError(f"provider request failed with HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise ProbeError("provider endpoint is unavailable without interaction") from exc
    try:
        parsed = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProbeError("provider returned invalid JSON") from exc
    if not isinstance(parsed, dict):
        raise ProbeError("provider returned a non-object response")
    return parsed


def _provider_datetime(value: Any, label: str) -> date:
    if not isinstance(value, dict):
        raise ProbeError(f"{label} is missing")
    timezone = value.get("timeZone")
    if timezone not in (None, {"id": TIMEZONE}):
        raise ProbeError(f"{label} uses an unexpected timezone")
    try:
        result = date(int(value["year"]), int(value["month"]), int(value["day"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise ProbeError(f"{label} is not a complete calendar date") from exc
    if any(value.get(field, 0) not in (0, None) for field in ("hours", "minutes", "seconds", "nanos")):
        raise ProbeError(f"{label} is not aligned to a daily boundary")
    return result


def _require_fresh(payload: dict[str, Any], required_end: date, label: str) -> None:
    info = payload.get("freshnessInfo")
    values = info.get("freshnesses") if isinstance(info, dict) else None
    daily = [
        item
        for item in values or []
        if isinstance(item, dict) and item.get("aggregationPeriod") == "DAILY"
    ]
    if len(daily) != 1:
        raise ProbeError(f"{label} daily freshness is missing or ambiguous")
    latest_end = _provider_datetime(daily[0].get("latestEndTime"), f"{label} latestEndTime")
    if latest_end < required_end:
        raise ProbeError(f"{label} data is not fresh through the requested week")


def _datetime_payload(value: date) -> dict[str, Any]:
    return {
        "year": value.year,
        "month": value.month,
        "day": value.day,
        "timeZone": {"id": TIMEZONE},
    }


def _query_body(
    week_end: date,
    provider_metric: str,
    dimensions: list[str],
    *,
    page_token: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "timelineSpec": {
            "aggregationPeriod": "DAILY",
            "startTime": _datetime_payload(week_end),
            "endTime": _datetime_payload(week_end + timedelta(days=1)),
        },
        "dimensions": dimensions,
        "metrics": [provider_metric],
        "filter": 'countryCode = "UZ"',
        "pageSize": PAGE_SIZE,
        "userCohort": COHORT,
    }
    if page_token:
        payload["pageToken"] = page_token
    return payload


def _query_rows(
    resource: str,
    provider_metric: str,
    week_end: date,
    dimensions: list[str],
    token: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    page_token: str | None = None
    seen_tokens: set[str] = set()
    for _ in range(MAX_PAGES):
        response = request_json(
            "POST",
            _resource_url(resource, query=True),
            token,
            payload=_query_body(
                week_end, provider_metric, dimensions, page_token=page_token
            ),
        )
        page_rows = response.get("rows", [])
        if not isinstance(page_rows, list) or not all(isinstance(row, dict) for row in page_rows):
            raise ProbeError("provider rows are malformed")
        rows.extend(page_rows)
        next_token = response.get("nextPageToken")
        if next_token in (None, ""):
            return rows
        if not isinstance(next_token, str) or next_token in seen_tokens:
            raise ProbeError("provider pagination token is invalid or repeated")
        seen_tokens.add(next_token)
        page_token = next_token
    raise ProbeError("provider response exceeded the safe pagination limit")


def _dimensions(row: dict[str, Any]) -> dict[str, str]:
    raw = row.get("dimensions")
    if not isinstance(raw, list):
        raise ProbeError("provider row dimensions are missing")
    result: dict[str, str] = {}
    for item in raw:
        if not isinstance(item, dict) or not isinstance(item.get("dimension"), str):
            raise ProbeError("provider row contains a malformed dimension")
        name = item["dimension"]
        values = [item.get("stringValue"), item.get("int64Value")]
        values = [value for value in values if isinstance(value, str) and value]
        if len(values) != 1 or name in result:
            raise ProbeError("provider row contains an ambiguous dimension")
        result[name] = values[0]
    return result


def _metric_value(row: dict[str, Any], metric: str, week_end: date) -> float:
    if row.get("aggregationPeriod") != "DAILY":
        raise ProbeError("provider row is not a daily aggregate")
    if _provider_datetime(row.get("startTime"), "row startTime") != week_end:
        raise ProbeError("provider row is outside the requested evidence day")
    raw_metrics = row.get("metrics")
    matches = [
        item
        for item in raw_metrics or []
        if isinstance(item, dict) and item.get("metric") == metric
    ]
    if len(matches) != 1:
        raise ProbeError(f"provider row has missing or ambiguous {metric}")
    decimal_value = matches[0].get("decimalValue")
    raw_value = decimal_value.get("value") if isinstance(decimal_value, dict) else None
    try:
        value = float(raw_value)
    except (TypeError, ValueError) as exc:
        raise ProbeError(f"provider metric {metric} is not numeric") from exc
    if not math.isfinite(value) or value < 0 or value > 100:
        raise ProbeError(f"provider metric {metric} is outside percent bounds")
    return value


def _collect(token: str, week_end: date) -> list[dict[str, Any]]:
    observations: dict[tuple[str, str, str], float] = {}
    supported_models: dict[str, set[str]] = {"PHONE": set(), "WEAR": set()}
    for kind, definition in SETS.items():
        resource = str(definition["resource"])
        metric = str(definition["provider_metric"])
        metadata = request_json("GET", _resource_url(resource), token)
        _require_fresh(metadata, week_end + timedelta(days=1), kind)

        summary_rows = _query_rows(
            resource, metric, week_end, ["countryCode"], token
        )
        if len(summary_rows) != 1 or _dimensions(summary_rows[0]) != {"countryCode": COUNTRY}:
            raise ProbeError(f"{kind} UZ summary row is missing or ambiguous")
        observations[("summary", "all", str(definition["summary_metric"]))] = (
            _metric_value(summary_rows[0], metric, week_end)
        )

        model_rows = _query_rows(
            resource,
            metric,
            week_end,
            ["countryCode", "deviceType", "deviceModel"],
            token,
        )
        for row in model_rows:
            dimensions = _dimensions(row)
            if dimensions.get("countryCode") != COUNTRY or set(dimensions) != {
                "countryCode",
                "deviceType",
                "deviceModel",
            }:
                raise ProbeError(f"{kind} model row has unexpected dimensions")
            device_type = dimensions["deviceType"]
            if device_type not in supported_models:
                continue
            device = dimensions["deviceModel"].strip()
            if not device or device.casefold() in {"all", "unknown", "unspecified"}:
                raise ProbeError(f"{kind} model row lacks a concrete device model")
            supported_models[device_type].add(device)
            output_metric = str(
                definition["phone_metric" if device_type == "PHONE" else "wear_metric"]
            )
            key = ("device", device, output_metric)
            if key in observations:
                raise ProbeError(f"duplicate {kind} row for device model {device}")
            observations[key] = _metric_value(row, metric, week_end)

    for device_type, models in supported_models.items():
        if not models:
            raise ProbeError(f"no complete UZ {device_type} model evidence is available")
        for device in models:
            required = (
                ("android_phone_model_crash_rate_pct", "android_phone_model_anr_rate_pct")
                if device_type == "PHONE"
                else ("wear_model_crash_rate_pct", "wear_model_anr_rate_pct")
            )
            if any(("device", device, metric) not in observations for metric in required):
                raise ProbeError(f"device model {device} lacks a complete crash/ANR pair")

    source_as_of = date.today().isoformat()
    week_start = (week_end - timedelta(days=6)).isoformat()
    source_ref = (
        "https://playdeveloperreporting.googleapis.com/v1beta1/apps/"
        f"{PACKAGE}/vitals"
    )
    notes = (
        "OS_PUBLIC provider 7-day user-weighted metric ending on the named "
        f"{TIMEZONE} day; missing or privacy-suppressed data is not coerced to zero"
    )
    return [
        {
            "week_start": week_start,
            "week_end": week_end.isoformat(),
            "platform": "google",
            "storefront": COUNTRY,
            "source_scope": scope,
            "device": device,
            "app_version": "all",
            "metric": metric,
            "value": format(value, ".12g"),
            "unit": "percent",
            "source_ref": source_ref,
            "source_as_of": source_as_of,
            "notes": notes,
        }
        for (scope, device, metric), value in sorted(observations.items())
    ]


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", newline="", encoding="utf-8") as output:
            writer = csv.DictWriter(output, fieldnames=CSV_COLUMNS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    except FileExistsError as exc:
        raise ProbeError(f"refusing to overwrite existing evidence file: {path}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--week-end", required=True, help="inclusive YYYY-MM-DD provider day")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        week_end = date.fromisoformat(args.week_end)
    except ValueError:
        print("Google Play vitals probe failed: week_end must be YYYY-MM-DD", file=sys.stderr)
        return 2
    token = os.environ.get(TOKEN_ENV, "")
    if len(token) < 20:
        print(f"Google Play vitals probe failed: {TOKEN_ENV} is missing", file=sys.stderr)
        return 2
    try:
        rows = _collect(token, week_end)
        _write_csv(args.output, rows)
    except (OSError, ProbeError) as exc:
        print(f"Google Play vitals probe failed: {exc}", file=sys.stderr)
        return 1
    print(
        f"google_play_vitals=ok: wrote {len(rows)} aggregate rows for week ending {week_end}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
