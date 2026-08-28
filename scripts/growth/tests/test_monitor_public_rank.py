from __future__ import annotations

import copy
import unittest
from pathlib import Path

from scripts.growth.monitor_public_rank import (
    _rank_surface,
    evaluate_day,
    parse_apple_chart,
    parse_apple_search,
    parse_google_play_html,
)
from scripts.growth.common import GROWTH_ROOT, load_json


FIXTURES = Path(__file__).parent / "fixtures"


class PublicRankParserTest(unittest.TestCase):
    def test_apple_chart_preserves_rank_order(self) -> None:
        items = parse_apple_chart((FIXTURES / "apple_chart.json").read_bytes())
        self.assertEqual([item["identifier"] for item in items], ["111", "6799886897", "333"])
        self.assertEqual(items[1]["name"], "Nimbo Weather")

    def test_apple_search_deduplicates_identifiers(self) -> None:
        items = parse_apple_search((FIXTURES / "apple_search.json").read_text())
        self.assertEqual(len(items), 3)
        self.assertEqual(items[2]["identifier"], "6799886897")

    def test_google_html_uses_first_unique_package_order(self) -> None:
        items = parse_google_play_html((FIXTURES / "google_play.html").read_bytes())
        self.assertEqual(
            [item["identifier"] for item in items],
            ["com.vendor.weather", "uz.ganikhodjaev.weather", "org.vendor.third"],
        )
        self.assertEqual(items[1]["name"], "Nimbo: Ob-havo va prognoz")

    def test_absence_is_bounded_not_unranked(self) -> None:
        surface = _rank_surface(
            surface_id="fixture",
            source_url="https://example.test",
            fetched_at="2026-08-28T00:00:00+05:00",
            response_sha256="abc",
            items=[{"identifier": "other", "name": "Other", "developer": None}],
            target_identifier="target",
            capture_limit=50,
            top_slice_size=10,
            minimum_unique_apps=10,
        )
        self.assertIsNone(surface["target_rank"])
        self.assertEqual(surface["target_rank_bound"], ">1")

    def test_rank_surface_deduplicates_before_counting_depth(self) -> None:
        items = [
            {"identifier": str(index), "name": str(index), "developer": None}
            for index in range(10)
        ]
        items.insert(1, dict(items[0]))
        surface = _rank_surface(
            surface_id="fixture",
            source_url="https://example.test",
            fetched_at="2026-08-28T00:00:00+05:00",
            response_sha256="abc",
            items=items,
            target_identifier="9",
            capture_limit=50,
            top_slice_size=10,
            minimum_unique_apps=10,
        )
        self.assertEqual(surface["status"], "ok")
        self.assertEqual(surface["raw_observed_count"], 11)
        self.assertEqual(surface["unique_observed_count"], 10)
        self.assertEqual(surface["target_rank"], 10)

    def test_rank_surface_is_not_ok_below_required_depth(self) -> None:
        items = [
            {"identifier": str(index), "name": str(index), "developer": None}
            for index in range(9)
        ]
        surface = _rank_surface(
            surface_id="fixture",
            source_url="https://example.test",
            fetched_at="2026-08-28T00:00:00+05:00",
            response_sha256="abc",
            items=items,
            target_identifier="0",
            capture_limit=50,
            top_slice_size=10,
            minimum_unique_apps=10,
        )
        self.assertEqual(surface["status"], "incomplete")
        self.assertEqual(surface["error_type"], "InsufficientUniqueApps")
        self.assertEqual(surface["unique_observed_count"], 9)

    def test_daily_goal_requires_category_and_query_quorum(self) -> None:
        framework = load_json(GROWTH_ROOT / "kpi-framework.json")
        queries = ["ob-havo", "pogoda", "weather", "toshkent-ob-havo", "prognoz"]
        profiles = ["uz-UZ", "ru-UZ", "en-UZ"]
        google_search = {
            profile: {
                query: {
                    "status": "ok",
                    "unique_observed_count": 10,
                    "target_rank": 5
                    if query in {"ob-havo", "pogoda"} and profile != "en-UZ"
                    else None,
                }
                for query in queries
            }
            for profile in profiles
        }
        snapshot = {
            "surfaces": {
                "apple": {
                    "category": {
                        "status": "ok",
                        "unique_observed_count": 10,
                        "target_rank": 7,
                    }
                },
                "google": {
                    "category": {
                        profile: {
                            "status": "ok",
                            "unique_observed_count": 10,
                            "target_rank": 8,
                        }
                        for profile in profiles
                    },
                    "search": google_search,
                },
            }
        }
        result = evaluate_day(snapshot, framework)
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["google_generic_top10_query_count"], 2)

        snapshot["surfaces"]["google"]["category"]["uz-UZ"][
            "unique_observed_count"
        ] = 9
        result = evaluate_day(snapshot, framework)
        self.assertEqual(result["status"], "unknown")
        self.assertFalse(result["google_category_top10_by_profile"]["uz-UZ"])

        snapshot["surfaces"]["google"]["category"]["uz-UZ"][
            "unique_observed_count"
        ] = 10
        google_search["en-UZ"]["weather"]["status"] = "error"
        result = evaluate_day(snapshot, framework)
        self.assertEqual(result["status"], "unknown")

    def test_daily_goal_rejects_a_minimum_depth_below_ten(self) -> None:
        framework = copy.deepcopy(load_json(GROWTH_ROOT / "kpi-framework.json"))
        framework["primary_goal"]["daily_requirements"][
            "minimum_unique_observed_apps"
        ] = 9
        with self.assertRaisesRegex(ValueError, "integer of at least 10"):
            evaluate_day({"surfaces": {}}, framework)


if __name__ == "__main__":
    unittest.main()
