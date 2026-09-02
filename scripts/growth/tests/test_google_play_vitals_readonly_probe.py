from __future__ import annotations

import importlib.util
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from scripts.growth.common import GROWTH_ROOT, load_json
from scripts.growth.import_weekly import import_csv


ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "google_play_vitals_readonly_probe",
    ROOT / "scripts/google-play-vitals-readonly-probe.py",
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def provider_date(value: date) -> dict:
    return {
        "year": value.year,
        "month": value.month,
        "day": value.day,
        "timeZone": {"id": MODULE.TIMEZONE},
    }


def freshness(latest_end: date) -> dict:
    return {
        "freshnessInfo": {
            "freshnesses": [
                {
                    "aggregationPeriod": "DAILY",
                    "latestEndTime": provider_date(latest_end),
                }
            ]
        }
    }


def row(day: date, metric: str, value: str, **dimensions: str) -> dict:
    return {
        "aggregationPeriod": "DAILY",
        "startTime": provider_date(day),
        "dimensions": [
            {"dimension": key, "stringValue": dimension_value}
            for key, dimension_value in dimensions.items()
        ],
        "metrics": [
            {"metric": metric, "decimalValue": {"value": value}}
        ],
    }


class GooglePlayVitalsProbeTest(unittest.TestCase):
    week_end = date(2026, 8, 31)

    def _response(self, method: str, url: str, token: str, *, payload=None) -> dict:
        self.assertEqual(token, "t" * 30)
        kind = "crash" if "crashRateMetricSet" in url else "anr"
        definition = MODULE.SETS[kind]
        if method == "GET":
            return freshness(self.week_end + MODULE.timedelta(days=1))
        self.assertEqual(method, "POST")
        self.assertEqual(payload["userCohort"], "OS_PUBLIC")
        self.assertEqual(payload["filter"], 'countryCode = "UZ"')
        self.assertEqual(payload["timelineSpec"]["aggregationPeriod"], "DAILY")
        metric = definition["provider_metric"]
        if payload["dimensions"] == ["countryCode"]:
            return {
                "rows": [
                    row(self.week_end, metric, "0.08", countryCode="UZ")
                ]
            }
        self.assertEqual(
            payload["dimensions"], ["countryCode", "deviceType", "deviceModel"]
        )
        return {
            "rows": [
                row(
                    self.week_end,
                    metric,
                    "0.10",
                    countryCode="UZ",
                    deviceType="PHONE",
                    deviceModel="google/coral",
                ),
                row(
                    self.week_end,
                    metric,
                    "0.20",
                    countryCode="UZ",
                    deviceType="WEAR",
                    deviceModel="google/eos",
                ),
            ]
        }

    def test_collects_complete_canonical_guardrail_rows(self) -> None:
        with mock.patch.object(MODULE, "request_json", side_effect=self._response):
            records = MODULE._collect("t" * 30, self.week_end)

        metrics = {(item["source_scope"], item["device"], item["metric"]) for item in records}
        self.assertEqual(
            metrics,
            {
                ("summary", "all", "android_user_perceived_crash_rate_pct"),
                ("summary", "all", "android_user_perceived_anr_rate_pct"),
                ("device", "google/coral", "android_phone_model_crash_rate_pct"),
                ("device", "google/coral", "android_phone_model_anr_rate_pct"),
                ("device", "google/eos", "wear_model_crash_rate_pct"),
                ("device", "google/eos", "wear_model_anr_rate_pct"),
            },
        )
        self.assertTrue(all(item["storefront"] == "UZ" for item in records))
        self.assertTrue(all(item["app_version"] == "all" for item in records))

    def test_output_is_accepted_by_canonical_weekly_importer(self) -> None:
        with (
            mock.patch.object(MODULE, "request_json", side_effect=self._response),
            tempfile.TemporaryDirectory() as directory,
        ):
            output = Path(directory) / "vitals.csv"
            MODULE._write_csv(output, MODULE._collect("t" * 30, self.week_end))
            payload = import_csv(output, load_json(GROWTH_ROOT / "metric-catalog.json"))

        self.assertEqual(payload["week_start"], "2026-08-25")
        self.assertEqual(payload["week_end"], "2026-08-31")
        self.assertEqual(len(payload["records"]), 6)

    def test_missing_wear_rows_fail_closed(self) -> None:
        def without_wear(method: str, url: str, token: str, *, payload=None) -> dict:
            response = self._response(method, url, token, payload=payload)
            if method == "POST" and payload["dimensions"] != ["countryCode"]:
                response["rows"] = [
                    item
                    for item in response["rows"]
                    if MODULE._dimensions(item).get("deviceType") != "WEAR"
                ]
            return response

        with (
            mock.patch.object(MODULE, "request_json", side_effect=without_wear),
            self.assertRaisesRegex(MODULE.ProbeError, "no complete UZ WEAR"),
        ):
            MODULE._collect("t" * 30, self.week_end)

    def test_incomplete_model_pair_fails_closed(self) -> None:
        def missing_wear_anr(method: str, url: str, token: str, *, payload=None) -> dict:
            response = self._response(method, url, token, payload=payload)
            if (
                method == "POST"
                and "anrRateMetricSet" in url
                and payload["dimensions"] != ["countryCode"]
            ):
                response["rows"] = [response["rows"][0]]
            return response

        with (
            mock.patch.object(MODULE, "request_json", side_effect=missing_wear_anr),
            self.assertRaisesRegex(MODULE.ProbeError, "lacks a complete crash/ANR pair"),
        ):
            MODULE._collect("t" * 30, self.week_end)

    def test_stale_provider_freshness_fails_closed(self) -> None:
        def stale(method: str, url: str, token: str, *, payload=None) -> dict:
            if method == "GET":
                return freshness(self.week_end)
            return self._response(method, url, token, payload=payload)

        with (
            mock.patch.object(MODULE, "request_json", side_effect=stale),
            self.assertRaisesRegex(MODULE.ProbeError, "not fresh through"),
        ):
            MODULE._collect("t" * 30, self.week_end)

    def test_request_allowlist_rejects_endpoint_or_query_mutation(self) -> None:
        crash_get = MODULE._resource_url("crashRateMetricSet")
        crash_query = MODULE._resource_url("crashRateMetricSet", query=True)
        self.assertTrue(MODULE._allowed_request("GET", crash_get))
        self.assertTrue(MODULE._allowed_request("POST", crash_query))
        self.assertFalse(MODULE._allowed_request("POST", crash_get))
        self.assertFalse(MODULE._allowed_request("GET", f"{crash_get}?fields=*"))
        self.assertFalse(MODULE._allowed_request("POST", crash_query.replace(MODULE.PACKAGE, "other.app")))

    def test_query_body_rejects_cohort_metric_and_window_mutation(self) -> None:
        url = MODULE._resource_url("crashRateMetricSet", query=True)
        base = MODULE._query_body(
            self.week_end,
            "userPerceivedCrashRate7dUserWeighted",
            ["countryCode"],
        )
        MODULE._validate_query_payload(url, base)
        mutations = []
        cohort = {**base, "userCohort": "APP_TESTERS"}
        mutations.append(cohort)
        metric = {**base, "metrics": ["crashRate"]}
        mutations.append(metric)
        timeline = {
            **base,
            "timelineSpec": {
                **base["timelineSpec"],
                "endTime": provider_date(self.week_end + MODULE.timedelta(days=2)),
            },
        }
        mutations.append(timeline)
        for payload in mutations:
            with self.subTest(payload=payload), self.assertRaises(MODULE.ProbeError):
                MODULE._validate_query_payload(url, payload)

    def test_existing_evidence_is_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "vitals.csv"
            output.write_text("existing\n", encoding="utf-8")
            with self.assertRaisesRegex(MODULE.ProbeError, "refusing to overwrite"):
                MODULE._write_csv(output, [])


if __name__ == "__main__":
    unittest.main()
