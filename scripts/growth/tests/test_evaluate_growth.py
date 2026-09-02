from __future__ import annotations

import copy
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from scripts.growth.common import GROWTH_ROOT, load_json
from scripts.growth.evaluate_growth import (
    calculate_streak,
    decide_90_day,
    evaluate_drivers,
    evaluate_guardrails,
    rank_improvements,
)
from scripts.growth.import_weekly import import_csv


FIXTURES = Path(__file__).parent / "fixtures"


def snapshot(day: date, status: str = "pass", weather_rank: int = 81) -> dict:
    return {
        "date": day.isoformat(),
        "config_fingerprint": "same-config",
        "evaluation": {"status": status},
        "surfaces": {
            "apple": {
                "category": {"target_rank": None},
                "search": {"weather": {"target_rank": weather_rank}},
            },
            "google": {
                "category": {
                    "uz-UZ": {"target_rank": None},
                    "ru-UZ": {"target_rank": None},
                    "en-UZ": {"target_rank": None},
                }
            },
        },
    }


class GrowthEvaluationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.framework = load_json(GROWTH_ROOT / "kpi-framework.json")

    def test_seven_consecutive_complete_passes_achieve_goal(self) -> None:
        start = date(2026, 8, 28)
        snapshots = [snapshot(start + timedelta(days=offset)) for offset in range(7)]
        result = calculate_streak(snapshots, start + timedelta(days=6), 7)
        self.assertTrue(result["goal_achieved"])
        self.assertEqual(result["current_streak_days"], 7)

    def test_unknown_breaks_streak(self) -> None:
        start = date(2026, 8, 28)
        snapshots = [snapshot(start + timedelta(days=offset)) for offset in range(7)]
        snapshots[3]["evaluation"]["status"] = "unknown"
        result = calculate_streak(snapshots, start + timedelta(days=6), 7)
        self.assertFalse(result["goal_achieved"])
        self.assertEqual(result["current_streak_days"], 3)

    def test_config_change_breaks_streak(self) -> None:
        start = date(2026, 8, 28)
        snapshots = [snapshot(start + timedelta(days=offset)) for offset in range(7)]
        for item in snapshots[3:]:
            item["config_fingerprint"] = "new-config"
        result = calculate_streak(snapshots, start + timedelta(days=6), 7)
        self.assertFalse(result["goal_achieved"])
        self.assertEqual(result["max_streak_days"], 4)
        self.assertEqual(result["current_streak_days"], 4)
        self.assertEqual(result["current_config_fingerprint"], "new-config")

    def test_rank_improvement_requires_comparable_exact_points(self) -> None:
        first = snapshot(date(2026, 8, 28), weather_rank=81)
        second = snapshot(date(2026, 11, 26), weather_rank=55)
        result = rank_improvements([first, second])
        self.assertEqual(result["max_improvement"], 26)

    def test_decision_order_is_fail_closed(self) -> None:
        guardrails_failed = {"critical_quality_gates_pass": False}
        drivers_clear = {"sufficient_conversion_or_retention_below_target": []}
        ranks = {"max_improvement": 30}
        self.assertEqual(
            decide_90_day(
                guardrails_failed, drivers_clear, ranks, self.framework
            )[0],
            "hold_acquisition_and_fix_gate",
        )

        guardrails_pass = {"critical_quality_gates_pass": True}
        drivers_below = {
            "sufficient_conversion_or_retention_below_target": ["apple_conversion_rate_pct"]
        }
        self.assertEqual(
            decide_90_day(
                guardrails_pass, drivers_below, ranks, self.framework
            )[0],
            "iterate_product_and_store_listing",
        )
        self.assertEqual(
            decide_90_day(
                guardrails_pass,
                drivers_clear,
                {"max_improvement": 10},
                self.framework,
            )[0],
            "iterate_organic_program",
        )

    def test_evaluator_reads_driver_and_rank_thresholds_from_framework(self) -> None:
        weekly = import_csv(
            FIXTURES / "weekly_metrics.csv",
            load_json(GROWTH_ROOT / "metric-catalog.json"),
        )
        framework = copy.deepcopy(self.framework)
        apple_conversion = next(
            definition
            for definition in framework["drivers"]
            if definition["id"] == "apple_conversion_rate_pct"
        )
        apple_conversion["target"] = 13.0
        apple_conversion["minimum_denominator"] = 700
        drivers = evaluate_drivers(weekly, framework)
        apple_result = next(
            result
            for result in drivers["results"]
            if result["id"] == "apple_conversion_rate_pct"
        )
        self.assertEqual(apple_result["target"], 13.0)
        self.assertEqual(apple_result["minimum_denominator"], 700.0)
        self.assertEqual(apple_result["status"], "unknown")

        google_ctr = next(
            definition
            for definition in framework["drivers"]
            if definition["id"] == "google_store_listing_ctr_pct"
        )
        google_ctr["target"] = 45.0
        google_ctr["minimum_denominator"] = 550
        drivers = evaluate_drivers(weekly, framework)
        google_result = next(
            result
            for result in drivers["results"]
            if result["id"] == "google_store_listing_ctr_pct"
        )
        self.assertEqual(google_result["target"], 45.0)
        self.assertEqual(google_result["minimum_denominator"], 550.0)
        self.assertEqual(google_result["status"], "fail")

        first_launch = next(
            definition
            for definition in framework["drivers"]
            if definition["id"] == "first_launch_rate_pct"
        )
        first_launch["target"] = 95.0
        drivers = evaluate_drivers(weekly, framework)
        first_launch_results = [
            result
            for result in drivers["results"]
            if result["id"].endswith("_first_launch_rate_pct")
        ]
        self.assertEqual(len(first_launch_results), 2)
        self.assertTrue(
            all(result["target"] == 95.0 for result in first_launch_results)
        )
        self.assertTrue(
            all(result["status"] == "fail" for result in first_launch_results)
        )

        framework["decision_thresholds"][
            "comparable_rank_improvement_positions"
        ] = 40
        decision = decide_90_day(
            {"critical_quality_gates_pass": True},
            {
                "sufficient_conversion_or_retention_below_target": [],
                "decision_exclusions": [],
            },
            {"max_improvement": 30},
            framework,
        )
        self.assertEqual(
            decision[0], "iterate_organic_program"
        )

    def test_conflicting_driver_evidence_blocks_paid_decision(self) -> None:
        content = (FIXTURES / "weekly_metrics.csv").read_text()
        content = content.replace(
            "google_store_listing_ctr_pct,40,percent",
            "google_store_listing_ctr_pct,45,percent",
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "conflicting-ratio.csv"
            path.write_text(content)
            weekly = import_csv(
                path,
                load_json(GROWTH_ROOT / "metric-catalog.json"),
            )
        drivers = evaluate_drivers(weekly, self.framework)
        google_ctr = next(
            result
            for result in drivers["results"]
            if result["id"] == "google_store_listing_ctr_pct"
        )
        self.assertEqual(google_ctr["status"], "unknown")
        decision = decide_90_day(
            {"critical_quality_gates_pass": True},
            drivers,
            {"max_improvement": 30},
            self.framework,
        )
        self.assertEqual(decision[0], "continue_measurement_no_paid_decision")

    def test_guardrails_pass_only_with_all_critical_evidence(self) -> None:
        weekly = import_csv(
            FIXTURES / "weekly_metrics.csv",
            load_json(GROWTH_ROOT / "metric-catalog.json"),
        )
        framework = self.framework
        gates = {
            "gates": {
                requirement["id"]: {"status": "pass"}
                for requirement in framework["scale_gates"]
            }
        }
        result = evaluate_guardrails(weekly, framework, gates)
        self.assertTrue(result["critical_quality_gates_pass"])

    def test_policy_guardrail_requires_both_store_values(self) -> None:
        weekly = import_csv(
            FIXTURES / "weekly_metrics.csv",
            load_json(GROWTH_ROOT / "metric-catalog.json"),
        )
        weekly["records"] = [
            record
            for record in weekly["records"]
            if record["metric"] != "google_policy_issues"
        ]
        gates = {
            "gates": {
                requirement["id"]: {"status": "pass"}
                for requirement in self.framework["scale_gates"]
            }
        }

        result = evaluate_guardrails(weekly, self.framework, gates)

        self.assertFalse(result["critical_quality_gates_pass"])
        policy = next(
            item
            for item in result["metric_guardrails"]
            if item["id"] == "open_policy_issues"
        )
        self.assertEqual(policy["status"], "unknown")
        self.assertEqual(policy["values"], [0.0])
        self.assertEqual(policy["missing_metric_ids"], ["google_policy_issues"])

        apple_policy = next(
            record
            for record in weekly["records"]
            if record["metric"] == "apple_policy_issues"
        )
        apple_policy["value"] = 1
        failed = evaluate_guardrails(weekly, self.framework, gates)
        failed_policy = next(
            item
            for item in failed["metric_guardrails"]
            if item["id"] == "open_policy_issues"
        )
        self.assertEqual(failed_policy["status"], "fail")
        self.assertEqual(
            failed_policy["missing_metric_ids"], ["google_policy_issues"]
        )

    def test_policy_guardrail_uses_app_global_scope(self) -> None:
        weekly = import_csv(
            FIXTURES / "weekly_metrics.csv",
            load_json(GROWTH_ROOT / "metric-catalog.json"),
        )
        apple_policy = next(
            record
            for record in weekly["records"]
            if record["metric"] == "apple_policy_issues"
        )
        apple_policy["storefront"] = "UZ"
        gates = {
            "gates": {
                requirement["id"]: {"status": "pass"}
                for requirement in self.framework["scale_gates"]
            }
        }

        result = evaluate_guardrails(weekly, self.framework, gates)
        policy = next(
            item
            for item in result["metric_guardrails"]
            if item["id"] == "open_policy_issues"
        )

        self.assertEqual(policy["status"], "unknown")
        self.assertEqual(policy["missing_metric_ids"], ["apple_policy_issues"])

    def test_scale_gate_framework_matches_operational_gate_registry(self) -> None:
        gate_registry = load_json(GROWTH_ROOT / "quality/gates.json")["gates"]
        configured_gate_ids = [
            requirement["id"] for requirement in self.framework["scale_gates"]
        ]
        self.assertEqual(len(configured_gate_ids), len(set(configured_gate_ids)))
        self.assertEqual(set(configured_gate_ids), set(gate_registry))
        self.assertTrue(
            all(
                gate.get("blocks_publication") is True
                for gate in gate_registry.values()
            )
        )

    def test_source_sync_and_domain_gates_fail_closed(self) -> None:
        weekly = import_csv(
            FIXTURES / "weekly_metrics.csv",
            load_json(GROWTH_ROOT / "metric-catalog.json"),
        )
        passing_gates = {
            "gates": {
                requirement["id"]: {"status": "pass"}
                for requirement in self.framework["scale_gates"]
            }
        }
        for gate_id in (
            "release_artifact_source_sync",
            "domain_activation",
            "store_policy_console_clearance",
        ):
            with self.subTest(gate_id=gate_id):
                gates = copy.deepcopy(passing_gates)
                gates["gates"][gate_id] = {
                    "status": "blocked",
                    "reason": "test blocker",
                }
                result = evaluate_guardrails(weekly, self.framework, gates)
                self.assertFalse(result["critical_quality_gates_pass"])
                gate_result = next(
                    item for item in result["scale_gates"] if item["id"] == gate_id
                )
                self.assertEqual(gate_result["actual"], "blocked")
                self.assertEqual(gate_result["status"], "fail")

    def test_guardrails_ignore_aggregate_model_vitals(self) -> None:
        weekly = import_csv(
            FIXTURES / "weekly_metrics.csv",
            load_json(GROWTH_ROOT / "metric-catalog.json"),
        )
        for record in weekly["records"]:
            if record["metric"].endswith("model_crash_rate_pct") or record[
                "metric"
            ].endswith("model_anr_rate_pct"):
                record["source_scope"] = "summary"
                record["device"] = "all"
        gates = {
            "gates": {
                requirement["id"]: {"status": "pass"}
                for requirement in self.framework["scale_gates"]
            }
        }
        result = evaluate_guardrails(weekly, self.framework, gates)
        self.assertFalse(result["critical_quality_gates_pass"])
        phone_crash = next(
            item
            for item in result["metric_guardrails"]
            if item["id"] == "android_phone_model_crash_rate_pct"
        )
        self.assertEqual(phone_crash["status"], "unknown")


if __name__ == "__main__":
    unittest.main()
