from __future__ import annotations

import copy
import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from scripts.growth.common import GROWTH_ROOT, load_json
from scripts.growth.generate_weekly_report import (
    ReportInputError,
    _write_report_atomic,
    main,
    render_weekly_report,
)
from scripts.growth.import_weekly import import_csv


FIXTURES = Path(__file__).parent / "fixtures"


class WeeklyReportTest(unittest.TestCase):
    def evaluation(self) -> dict:
        return load_json(FIXTURES / "evaluation_weekly_report.json")

    def rank_snapshot(self) -> dict:
        return load_json(FIXTURES / "public_rank_weekly_report.json")

    def weekly(self) -> dict:
        return import_csv(
            FIXTURES / "weekly_metrics.csv",
            load_json(GROWTH_ROOT / "metric-catalog.json"),
        )

    def render(self) -> str:
        return render_weekly_report(
            self.evaluation(),
            evaluation_source="evaluation_weekly_report.json",
            rank_snapshot=self.rank_snapshot(),
            rank_source="public_rank_weekly_report.json",
            weekly=self.weekly(),
            weekly_source="weekly-2026-08-30.json",
        )

    def test_report_matches_deterministic_markdown_fixture(self) -> None:
        expected = (FIXTURES / "weekly_report_expected.md").read_text(
            encoding="utf-8"
        )
        self.assertEqual(self.render(), expected)
        self.assertEqual(self.render(), self.render())

    def test_report_is_answer_first_and_preserves_denominators(self) -> None:
        report = self.render()
        self.assertLess(
            report.index("**HOLD.**"),
            report.index("## KPI status"),
        )
        self.assertIn("14% — FAIL; denominator 600 / minimum 500", report)
        self.assertIn("40% — PASS; 240 / 600", report)
        self.assertIn("85% — PASS; 85 / 100", report)
        self.assertIn("## Unknown or missing evidence", report)
        self.assertIn("User loss rate", report)
        self.assertIn(
            "KPI evidence period: `2026-08-24 through 2026-08-30`", report
        )
        self.assertIn("Weekly evidence: `weekly-2026-08-30.json` — ACCEPTED", report)
        self.assertIn(
            "Current rank evidence: `public_rank_weekly_report.json` — ACCEPTED",
            report,
        )

    def test_report_implements_canonical_template_sections(self) -> None:
        template = (GROWTH_ROOT / "reports/weekly-template.md").read_text(
            encoding="utf-8"
        )
        report = self.render()
        for heading in (
            "## Executive summary",
            "## KPI status",
            "## Rank and search",
            "## Scale gates",
            "## Quality guardrails",
            "## Unknown or missing evidence",
            "## Next actions",
        ):
            with self.subTest(heading=heading):
                self.assertIn(heading, template)
                self.assertIn(heading, report)

    def test_missing_sources_and_metrics_are_explicit_unknowns(self) -> None:
        evaluation = self.evaluation()
        evaluation["latest_weekly_period_end"] = None
        for driver in evaluation["drivers"]["results"]:
            driver["value"] = None
            driver["status"] = "unknown"
            driver["sufficient"] = False
            if "denominator" in driver:
                driver["denominator"] = None
        evaluation["drivers"][
            "sufficient_conversion_or_retention_below_target"
        ] = []
        for guardrail in evaluation["guardrails"]["metric_guardrails"]:
            guardrail["values"] = []
            guardrail["status"] = "unknown"

        report = render_weekly_report(
            evaluation,
            evaluation_source="evaluation.json",
        )

        self.assertIn("Current rank evidence: `Not available` — NOT ACCEPTED", report)
        self.assertIn("No validated seven-day UZ console import is referenced", report)
        self.assertIn("Apple conversion: actual is missing", report)
        self.assertIn("Unknown quality guardrails", report)
        self.assertNotIn("0% — UNKNOWN", report)

    def test_mismatched_rank_snapshot_is_not_reported_as_current(self) -> None:
        rank_snapshot = self.rank_snapshot()
        rank_snapshot["config_fingerprint"] = "different-config"
        report = render_weekly_report(
            self.evaluation(),
            evaluation_source="evaluation.json",
            rank_snapshot=rank_snapshot,
            rank_source="rank.json",
            weekly=self.weekly(),
            weekly_source="weekly.json",
        )
        self.assertIn("config_fingerprint differs from the evaluation", report)
        self.assertIn("| Apple UZ Top Free Weather | Unknown |", report)
        self.assertNotIn("| Apple UZ Top Free Weather | #9 |", report)

    def test_cli_refuses_overwrite_without_replace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evaluation_path = root / "evaluation.json"
            rank_path = root / "rank.json"
            weekly_path = root / "weekly.json"
            output = root / "weekly-2026-08-30.md"
            evaluation_path.write_text(
                json.dumps(self.evaluation()), encoding="utf-8"
            )
            rank_path.write_text(
                json.dumps(self.rank_snapshot()), encoding="utf-8"
            )
            weekly_path.write_text(json.dumps(self.weekly()), encoding="utf-8")
            arguments = [
                str(evaluation_path),
                "--rank-snapshot",
                str(rank_path),
                "--weekly",
                str(weekly_path),
                "--output",
                str(output),
            ]

            self.assertEqual(main(arguments), 0)
            first = output.read_bytes()
            self.assertEqual(main(arguments), 2)
            self.assertEqual(output.read_bytes(), first)
            self.assertEqual(main([*arguments, "--replace"]), 0)
            self.assertEqual(output.read_bytes(), first)

    def test_missing_linked_weekly_suppresses_populated_results(self) -> None:
        report = render_weekly_report(
            self.evaluation(),
            evaluation_source="evaluation.json",
            rank_snapshot=self.rank_snapshot(),
            rank_source="rank.json",
        )

        self.assertIn(
            "| Conversion / listing CTR | Unknown — UNKNOWN | Unknown — UNKNOWN |",
            report,
        )
        self.assertIn(
            "| Ratings | Unknown ratings — UNKNOWN; Unknown / 5 — UNKNOWN",
            report,
        )
        self.assertIn(
            "| iOS crash-free sessions | Unknown | >= 99.8% | UNKNOWN |",
            report,
        )
        self.assertNotIn("40% — PASS", report)
        self.assertNotIn("99.9% | >= 99.8% | PASS", report)
        self.assertIn("all weekly KPI and quality results were suppressed", report)

    def test_invalid_weekly_contract_is_rejected_and_suppressed(self) -> None:
        mutations = {}

        wrong_schema = self.weekly()
        wrong_schema["schema_version"] = 2
        mutations["schema"] = wrong_schema

        wrong_envelope = self.weekly()
        wrong_envelope["week_start"] = "2026-08-25"
        mutations["seven-day-envelope"] = wrong_envelope

        wrong_record_date = self.weekly()
        wrong_record_date["records"][0]["week_end"] = "2020-01-07"
        mutations["record-period"] = wrong_record_date

        duplicate = self.weekly()
        duplicate["records"].append(copy.deepcopy(duplicate["records"][0]))
        mutations["duplicate-scope"] = duplicate

        wrong_unit = self.weekly()
        wrong_unit["records"][0]["unit"] = "percent"
        mutations["unit"] = wrong_unit

        impossible_value = self.weekly()
        next(
            row
            for row in impossible_value["records"]
            if row["metric"] == "google_average_rating"
        )["value"] = 6
        mutations["value-domain"] = impossible_value

        wrong_array = self.weekly()
        wrong_array["records"] = {}
        mutations["array"] = wrong_array

        wrong_derived = self.weekly()
        next(
            row
            for row in wrong_derived["derived_metrics"]
            if row["metric"] == "google_store_listing_ctr_pct_derived"
        )["value"] = 1
        mutations["derived-ratio"] = wrong_derived

        for name, weekly in mutations.items():
            with self.subTest(name=name):
                report = render_weekly_report(
                    self.evaluation(),
                    evaluation_source="evaluation.json",
                    rank_snapshot=self.rank_snapshot(),
                    rank_source="rank.json",
                    weekly=weekly,
                    weekly_source="weekly.json",
                )
                self.assertIn("weekly import was rejected", report)
                self.assertIn("Unknown — UNKNOWN", report)
                self.assertNotIn("40% — PASS", report)

    def test_invalid_rank_schema_or_goal_completeness_is_rejected(self) -> None:
        cases = {}
        wrong_schema = self.rank_snapshot()
        wrong_schema["schema_version"] = 2
        cases["schema"] = wrong_schema

        wrong_date = self.rank_snapshot()
        wrong_date["date"] = "2026-08-29"
        cases["date"] = wrong_date

        wrong_completeness = self.rank_snapshot()
        wrong_completeness["goal_evidence_complete"] = False
        cases["goal-completeness"] = wrong_completeness

        for name, rank_snapshot in cases.items():
            with self.subTest(name=name):
                report = render_weekly_report(
                    self.evaluation(),
                    evaluation_source="evaluation.json",
                    rank_snapshot=rank_snapshot,
                    rank_source="rank.json",
                    weekly=self.weekly(),
                    weekly_source="weekly.json",
                )
                self.assertIn("public-rank snapshot was rejected", report)
                self.assertIn("| Apple UZ Top Free Weather | Unknown |", report)

    def test_conflicting_linked_metrics_render_conflict_not_pass(self) -> None:
        weekly = self.weekly()
        next(
            row
            for row in weekly["records"]
            if row["metric"] == "google_average_rating"
        )["value"] = 4.0
        next(
            row
            for row in weekly["records"]
            if row["metric"] == "ios_crash_free_sessions_pct"
        )["value"] = 99.7
        next(
            row
            for row in weekly["records"]
            if row["metric"] == "google_unique_user_install_clicks"
        )["value"] = 1
        next(
            row
            for row in weekly["derived_metrics"]
            if row["metric"] == "google_store_listing_ctr_pct_derived"
        )["value"] = 0.17

        report = render_weekly_report(
            self.evaluation(),
            evaluation_source="evaluation.json",
            rank_snapshot=self.rank_snapshot(),
            rank_source="rank.json",
            weekly=weekly,
            weekly_source="weekly.json",
        )

        self.assertIn("Unknown / 5 — CONFLICT", report)
        self.assertIn(
            "| Conversion / listing CTR | 14% — FAIL; denominator 600 / minimum 500 "
            "| Unknown — CONFLICT |",
            report,
        )
        self.assertIn(
            "| iOS crash-free sessions | Unknown | >= 99.8% | CONFLICT |", report
        )
        self.assertIn("conflicts with the linked weekly evidence", report)
        self.assertNotIn("4.8 / 5 — PASS", report)
        self.assertNotIn("99.9% | >= 99.8% | PASS", report)

    def test_rank_status_and_current_rank_are_cross_checked(self) -> None:
        rank_snapshot = self.rank_snapshot()
        rank_snapshot["surfaces"]["apple"]["category"]["target_rank"] = 40

        report = render_weekly_report(
            self.evaluation(),
            evaluation_source="evaluation.json",
            rank_snapshot=rank_snapshot,
            rank_source="rank.json",
            weekly=self.weekly(),
            weekly_source="weekly.json",
        )

        self.assertIn("Apple Top-10 status conflicts with its current rank", report)
        self.assertIn("| Apple UZ Top Free Weather | Unknown |", report)
        self.assertNotIn("| Apple UZ Top Free Weather | #40 |", report)

    def test_rank_comparison_requires_the_accepted_current_observation(self) -> None:
        rank_snapshot = self.rank_snapshot()
        rank_snapshot["surfaces"]["apple"]["category"]["target_rank"] = 10

        report = render_weekly_report(
            self.evaluation(),
            evaluation_source="evaluation.json",
            rank_snapshot=rank_snapshot,
            rank_source="rank.json",
            weekly=self.weekly(),
            weekly_source="weekly.json",
        )

        self.assertIn(
            "| Apple UZ Top Free Weather | #10 | Unknown | Unknown | PASS |", report
        )
        self.assertIn("does not end at the accepted current observation", report)

    def test_incomplete_rank_surface_is_unknown_not_fail(self) -> None:
        rank_snapshot = self.rank_snapshot()
        surface = rank_snapshot["surfaces"]["google"]["category"]["ru-UZ"]
        surface.update(
            {
                "status": "error",
                "target_rank": None,
                "target_rank_bound": None,
            }
        )
        rank_snapshot["evaluation"]["google_category_status_by_profile"][
            "ru-UZ"
        ] = "unknown"

        report = render_weekly_report(
            self.evaluation(),
            evaluation_source="evaluation.json",
            rank_snapshot=rank_snapshot,
            rank_source="rank.json",
            weekly=self.weekly(),
            weekly_source="weekly.json",
        )

        self.assertIn(
            "| Google UZ Weather, `ru-UZ` | Unknown | Unknown | Unknown | UNKNOWN |",
            report,
        )
        self.assertNotIn(
            "| Google UZ Weather, `ru-UZ` | Unknown | Unknown | Unknown | FAIL |",
            report,
        )

    def test_semantic_evaluation_contract_rejects_impossible_or_inconsistent_data(
        self,
    ) -> None:
        cases = {}

        impossible = self.evaluation()
        next(
            item
            for item in impossible["drivers"]["results"]
            if item["id"] == "google_average_rating"
        )["value"] = 999
        cases["impossible-domain"] = impossible

        bad_status = self.evaluation()
        next(
            item
            for item in bad_status["drivers"]["results"]
            if item["id"] == "google_average_rating"
        )["status"] = "fail"
        cases["status"] = bad_status

        bad_target = self.evaluation()
        target_item = next(
            item
            for item in bad_target["drivers"]["results"]
            if item["id"] == "apple_conversion_rate_pct"
        )
        target_item["target"] = 14
        target_item["status"] = "pass"
        bad_target["drivers"][
            "sufficient_conversion_or_retention_below_target"
        ] = []
        cases["target"] = bad_target

        missing_driver = self.evaluation()
        missing_driver["drivers"]["results"].pop()
        cases["canonical-driver-set"] = missing_driver

        missing_gate = self.evaluation()
        missing_gate["guardrails"]["scale_gates"].pop()
        cases["canonical-gate-set"] = missing_gate

        bad_decision = self.evaluation()
        bad_decision["decision_90_day_rule"]["decision"] = "continue_organic_program"
        cases["decision"] = bad_decision

        for name, evaluation in cases.items():
            with self.subTest(name=name), self.assertRaises(ReportInputError):
                render_weekly_report(
                    evaluation,
                    evaluation_source="evaluation.json",
                )

    def test_atomic_no_clobber_allows_exactly_one_concurrent_writer(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "weekly.md"

            def write(position: int) -> tuple[str, str]:
                content = f"complete report {position}\n" * 100
                try:
                    _write_report_atomic(output, content, replace=False)
                    return "written", content
                except FileExistsError:
                    return "exists", content

            with ThreadPoolExecutor(max_workers=8) as executor:
                results = list(executor.map(write, range(8)))

            self.assertEqual(sum(status == "written" for status, _ in results), 1)
            self.assertEqual(sum(status == "exists" for status, _ in results), 7)
            written = next(content for status, content in results if status == "written")
            self.assertEqual(output.read_text(encoding="utf-8"), written)
            self.assertEqual(list(output.parent.glob(".weekly.md.*.tmp")), [])

    def test_unsupported_evaluation_schema_is_rejected(self) -> None:
        evaluation = copy.deepcopy(self.evaluation())
        evaluation["schema_version"] = 2
        with self.assertRaisesRegex(ReportInputError, "schema_version"):
            render_weekly_report(
                evaluation,
                evaluation_source="evaluation.json",
            )


if __name__ == "__main__":
    unittest.main()
