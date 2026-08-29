from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.growth.common import GROWTH_ROOT, load_json
from scripts.growth.import_weekly import ImportValidationError, import_csv


FIXTURES = Path(__file__).parent / "fixtures"


class WeeklyImportTest(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = load_json(GROWTH_ROOT / "metric-catalog.json")

    def test_import_and_derived_rates(self) -> None:
        payload = import_csv(FIXTURES / "weekly_metrics.csv", self.catalog)
        derived = {
            (row["platform"], row["metric"]): row["value"]
            for row in payload["derived_metrics"]
        }
        self.assertEqual(payload["week_end"], "2026-08-30")
        self.assertEqual(derived[("google", "google_store_listing_ctr_pct_derived")], 40.0)
        self.assertEqual(derived[("google", "first_launch_rate_pct")], 90.0)
        self.assertEqual(derived[("apple", "d7_retention_pct")], 25.0)
        self.assertEqual(payload["warnings"], [])

    def test_rejects_wrong_unit(self) -> None:
        content = (FIXTURES / "weekly_metrics.csv").read_text()
        content = content.replace(
            "apple_unique_impressions,600,count", "apple_unique_impressions,600,percent", 1
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.csv"
            path.write_text(content)
            with self.assertRaises(ImportValidationError):
                import_csv(path, self.catalog)

    def test_model_vitals_require_device_scope_and_concrete_model(self) -> None:
        model_metrics = {
            "android_phone_model_crash_rate_pct": "Pixel 8",
            "android_phone_model_anr_rate_pct": "Pixel 8",
            "wear_model_crash_rate_pct": "Pixel Watch 3",
            "wear_model_anr_rate_pct": "Pixel Watch 3",
        }
        fixture = (FIXTURES / "weekly_metrics.csv").read_text()
        for metric, device in model_metrics.items():
            original = f"google,UZ,device,{device},all,{metric}"
            invalid_dimensions = {
                "summary scope": f"google,UZ,summary,{device},all,{metric}",
                "aggregate device": f"google,UZ,device,all,all,{metric}",
            }
            for case, replacement in invalid_dimensions.items():
                with self.subTest(metric=metric, case=case):
                    content = fixture.replace(original, replacement, 1)
                    self.assertNotEqual(content, fixture)
                    with tempfile.TemporaryDirectory() as directory:
                        path = Path(directory) / "bad-model-scope.csv"
                        path.write_text(content)
                        with self.assertRaisesRegex(
                            ImportValidationError,
                            "source_scope=device and a concrete device model",
                        ):
                            import_csv(path, self.catalog)

    def test_policy_metrics_require_app_global_summary_scope(self) -> None:
        fixture = (FIXTURES / "weekly_metrics.csv").read_text()
        original = "apple,ALL,summary,all,all,apple_policy_issues"
        invalid_scopes = {
            "country storefront": "apple,UZ,summary,all,all,apple_policy_issues",
            "device scope": "apple,ALL,device,iPhone 16,all,apple_policy_issues",
        }
        for case, replacement in invalid_scopes.items():
            with self.subTest(case=case):
                content = fixture.replace(original, replacement, 1)
                self.assertNotEqual(content, fixture)
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "bad-policy-scope.csv"
                    path.write_text(content)
                    with self.assertRaisesRegex(
                        ImportValidationError,
                        "requires storefront=ALL, source_scope=summary",
                    ):
                        import_csv(path, self.catalog)

    def test_impossible_derived_percentage_is_rejected(self) -> None:
        content = (FIXTURES / "weekly_metrics.csv").read_text()
        content = content.replace(
            "google_first_launches,90,count",
            "google_first_launches,110,count",
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "impossible-ratio.csv"
            path.write_text(content)
            with self.assertRaisesRegex(
                ImportValidationError,
                "derived first_launch_rate_pct is 110.0%, above the possible 100%",
            ):
                import_csv(path, self.catalog)

    def test_positive_numerator_with_zero_denominator_is_rejected(self) -> None:
        content = (FIXTURES / "weekly_metrics.csv").read_text()
        content = content.replace(
            "google_installations,100,count",
            "google_installations,0,count",
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "zero-denominator.csv"
            path.write_text(content)
            with self.assertRaisesRegex(
                ImportValidationError,
                "google_first_launches is positive while google_installations is zero",
            ):
                import_csv(path, self.catalog)

    def test_material_reported_derived_conflict_is_ineligible(self) -> None:
        content = (FIXTURES / "weekly_metrics.csv").read_text()
        content = content.replace(
            "google_store_listing_ctr_pct,40,percent",
            "google_store_listing_ctr_pct,45,percent",
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "conflicting-ratio.csv"
            path.write_text(content)
            payload = import_csv(path, self.catalog)
        reported = next(
            row
            for row in payload["records"]
            if row["metric"] == "google_store_listing_ctr_pct"
        )
        derived = next(
            row
            for row in payload["derived_metrics"]
            if row["metric"] == "google_store_listing_ctr_pct_derived"
        )
        self.assertFalse(reported["decision_eligible"])
        self.assertFalse(derived["decision_eligible"])
        self.assertEqual(len(payload["decision_exclusions"]), 1)


if __name__ == "__main__":
    unittest.main()
