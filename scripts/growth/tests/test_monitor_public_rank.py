from __future__ import annotations

import copy
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from scripts.growth.monitor_public_rank import (
    _current_check_payload,
    _intraday_observation_path,
    _monitor_exit_code,
    _rank_surface,
    evaluate_day,
    main,
    parse_apple_chart,
    parse_apple_search,
    parse_google_play_html,
)
from scripts.growth.common import GROWTH_ROOT, load_json, now_in, parse_date
from scripts.growth.evaluate_growth import _load_dated_json


FIXTURES = Path(__file__).parent / "fixtures"


def goal_snapshot() -> dict:
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
    return {
        "methodology": {"fixed_query_ids": queries},
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


def captured_snapshot() -> dict:
    framework = load_json(GROWTH_ROOT / "kpi-framework.json")
    snapshot = goal_snapshot()
    snapshot["surfaces"]["apple"]["search"] = {
        "weather": {
            "status": "ok",
            "target_rank": 15,
            "target_rank_bound": None,
        }
    }
    for surface in snapshot["surfaces"]["google"]["category"].values():
        surface["target_rank_bound"] = None
    captured_at = now_in("Asia/Tashkent").replace(microsecond=0)
    snapshot.update(
        {
            "schema_version": 1,
            "date": captured_at.date().isoformat(),
            "captured_at": captured_at.isoformat(timespec="seconds"),
            "timezone": "Asia/Tashkent",
            "config_fingerprint": "fixture-fingerprint",
            "diagnostic_capture_complete": True,
            "goal_evidence_complete": True,
            "source_errors": [],
        }
    )
    snapshot["evaluation"] = evaluate_day(snapshot, framework)
    return snapshot


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
        snapshot = goal_snapshot()
        google_search = snapshot["surfaces"]["google"]["search"]
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
        google_search["uz-UZ"]["weather"]["target_rank"] = 5
        google_search["en-UZ"]["weather"]["status"] = "error"
        result = evaluate_day(snapshot, framework)
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["google_generic_query_status"], "pass")
        self.assertEqual(result["google_query_statuses"]["weather"], "unknown")
        self.assertIn("weather", result["google_generic_unresolved_queries"])

    def test_generic_quorum_is_fail_when_only_one_query_can_still_qualify(self) -> None:
        framework = load_json(GROWTH_ROOT / "kpi-framework.json")
        snapshot = goal_snapshot()
        google_search = snapshot["surfaces"]["google"]["search"]
        for searches in google_search.values():
            for surface in searches.values():
                surface["target_rank"] = None
        google_search["uz-UZ"]["weather"]["target_rank"] = 5
        google_search["en-UZ"]["weather"]["status"] = "error"

        result = evaluate_day(snapshot, framework)

        self.assertEqual(result["google_query_statuses"]["weather"], "unknown")
        self.assertEqual(result["google_generic_query_status"], "fail")
        self.assertEqual(result["status"], "fail")
        self.assertTrue(result["complete"])

    def test_generic_quorum_stays_unknown_when_missing_evidence_can_change_result(self) -> None:
        framework = load_json(GROWTH_ROOT / "kpi-framework.json")
        snapshot = goal_snapshot()
        google_search = snapshot["surfaces"]["google"]["search"]
        for profile, searches in google_search.items():
            for query, surface in searches.items():
                surface["target_rank"] = (
                    5 if query == "ob-havo" and profile != "en-UZ" else None
                )
        google_search["uz-UZ"]["weather"]["target_rank"] = 5
        google_search["en-UZ"]["weather"]["status"] = "error"

        result = evaluate_day(snapshot, framework)

        self.assertEqual(result["google_generic_top10_queries"], ["ob-havo"])
        self.assertEqual(result["google_query_statuses"]["weather"], "unknown")
        self.assertEqual(result["google_generic_query_status"], "unknown")
        self.assertEqual(result["status"], "unknown")
        self.assertFalse(result["complete"])

    def test_entirely_missing_configured_queries_stay_unknown(self) -> None:
        framework = load_json(GROWTH_ROOT / "kpi-framework.json")
        snapshot = goal_snapshot()
        google_search = snapshot["surfaces"]["google"]["search"]
        for profile in google_search:
            google_search[profile] = {"ob-havo": google_search[profile]["ob-havo"]}

        result = evaluate_day(snapshot, framework)

        self.assertEqual(result["google_generic_top10_queries"], ["ob-havo"])
        self.assertEqual(result["google_query_statuses"]["pogoda"], "unknown")
        self.assertEqual(result["google_query_unknown_profile_counts"]["pogoda"], 3)
        self.assertEqual(result["google_generic_query_status"], "unknown")
        self.assertEqual(result["status"], "unknown")
        self.assertFalse(result["complete"])

    def test_legacy_snapshot_infers_expected_queries_from_present_surfaces(self) -> None:
        framework = load_json(GROWTH_ROOT / "kpi-framework.json")
        snapshot = goal_snapshot()
        snapshot.pop("methodology")

        result = evaluate_day(snapshot, framework)

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["google_generic_top10_query_count"], 2)

    def test_malformed_methodology_falls_back_without_crashing(self) -> None:
        framework = load_json(GROWTH_ROOT / "kpi-framework.json")
        snapshot = goal_snapshot()
        snapshot["methodology"] = None

        result = evaluate_day(snapshot, framework)

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["google_generic_top10_query_count"], 2)

    def test_non_positive_or_boolean_ranks_never_count_as_top10(self) -> None:
        framework = load_json(GROWTH_ROOT / "kpi-framework.json")
        for malformed_rank in (True, 0, -1):
            with self.subTest(malformed_rank=malformed_rank):
                snapshot = goal_snapshot()
                snapshot["surfaces"]["apple"]["category"][
                    "target_rank"
                ] = malformed_rank

                result = evaluate_day(snapshot, framework)

                self.assertEqual(result["apple_weather_chart_status"], "unknown")
                self.assertEqual(result["status"], "unknown")
                self.assertFalse(result["complete"])

    def test_malformed_query_rank_is_unknown_not_qualifying(self) -> None:
        framework = load_json(GROWTH_ROOT / "kpi-framework.json")
        for malformed_rank in (True, 0, -1):
            with self.subTest(malformed_rank=malformed_rank):
                snapshot = goal_snapshot()
                google_search = snapshot["surfaces"]["google"]["search"]
                google_search["ru-UZ"]["ob-havo"]["target_rank"] = malformed_rank

                result = evaluate_day(snapshot, framework)

                self.assertEqual(result["google_query_statuses"]["ob-havo"], "unknown")
                self.assertNotIn("ob-havo", result["google_generic_top10_queries"])

    def test_monitor_exit_ignores_auxiliary_diagnostic_incompleteness(self) -> None:
        snapshot = {
            "capture_complete": False,
            "diagnostic_capture_complete": False,
            "evaluation": {"status": "fail"},
        }
        self.assertEqual(_monitor_exit_code(snapshot), 0)
        snapshot["evaluation"]["status"] = "pass"
        self.assertEqual(_monitor_exit_code(snapshot), 0)
        snapshot["evaluation"]["status"] = "unknown"
        self.assertEqual(_monitor_exit_code(snapshot), 1)
        for malformed in (
            {},
            {"evaluation": {}},
            {"evaluation": {"status": "bogus"}},
            {"evaluation": None},
        ):
            with self.subTest(malformed=malformed):
                self.assertEqual(_monitor_exit_code(malformed), 1)

    def test_proven_required_failure_wins_over_another_unknown_surface(self) -> None:
        framework = load_json(GROWTH_ROOT / "kpi-framework.json")
        cases = ("apple", "google-category")
        for failure_component in cases:
            with self.subTest(failure_component=failure_component):
                snapshot = goal_snapshot()
                apple = snapshot["surfaces"]["apple"]["category"]
                google_categories = snapshot["surfaces"]["google"]["category"]
                if failure_component == "apple":
                    apple["target_rank"] = 50
                    google_categories["uz-UZ"]["status"] = "error"
                else:
                    google_categories["uz-UZ"]["target_rank"] = 50
                    apple["status"] = "error"

                result = evaluate_day(snapshot, framework)

                self.assertEqual(result["status"], "fail")
                self.assertTrue(result["complete"])
                self.assertEqual(
                    _monitor_exit_code({"evaluation": result}),
                    0,
                )

    def test_daily_goal_rejects_a_minimum_depth_below_ten(self) -> None:
        framework = copy.deepcopy(load_json(GROWTH_ROOT / "kpi-framework.json"))
        framework["primary_goal"]["daily_requirements"][
            "minimum_unique_observed_apps"
        ] = 9
        with self.assertRaisesRegex(ValueError, "integer of at least 10"):
            evaluate_day({"surfaces": {}}, framework)

    def test_current_check_payload_is_explicitly_non_canonical(self) -> None:
        payload = _current_check_payload(captured_snapshot())

        self.assertEqual(payload["mode"], "check-current")
        self.assertFalse(payload["persisted"])
        self.assertFalse(payload["streak_eligible"])
        self.assertTrue(payload["canonical_daily_snapshot_unchanged"])
        self.assertEqual(payload["ranks"]["apple_weather_category"], 7)
        self.assertEqual(payload["ranks"]["apple_search"]["weather"], 15)
        self.assertEqual(payload["ranks"]["google_generic_top10_query_count"], 2)

    def test_stdout_mode_captures_without_writing(self) -> None:
        snapshot = captured_snapshot()
        stdout = StringIO()
        with (
            patch(
                "scripts.growth.monitor_public_rank.capture",
                return_value=snapshot,
            ),
            patch("scripts.growth.monitor_public_rank.write_json") as write_json,
            redirect_stdout(stdout),
        ):
            exit_code = main(["--stdout"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(stdout.getvalue()), snapshot)
        write_json.assert_not_called()

    def test_check_current_mode_captures_without_writing(self) -> None:
        snapshot = captured_snapshot()
        stdout = StringIO()
        with (
            patch(
                "scripts.growth.monitor_public_rank.capture",
                return_value=snapshot,
            ),
            patch("scripts.growth.monitor_public_rank.write_json") as write_json,
            redirect_stdout(stdout),
        ):
            exit_code = main(["--check-current"])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["mode"], "check-current")
        self.assertFalse(payload["persisted"])
        self.assertFalse(payload["streak_eligible"])
        write_json.assert_not_called()

    def test_intraday_observation_is_append_only_and_not_a_daily_snapshot(self) -> None:
        snapshot = captured_snapshot()
        with tempfile.TemporaryDirectory() as directory:
            daily_root = Path(directory)
            canonical_path = daily_root / f"{snapshot['date']}.json"
            canonical_path.write_text(
                json.dumps(
                    {
                        "date": snapshot["date"],
                        "marker": "canonical",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            intraday_root = daily_root / "intraday"
            arguments = [
                "--append-intraday",
                "--intraday-dir",
                str(intraday_root),
            ]
            with (
                patch(
                    "scripts.growth.monitor_public_rank.capture",
                    return_value=snapshot,
                ),
                redirect_stdout(StringIO()),
            ):
                self.assertEqual(main(arguments), 0)

            observation_path = _intraday_observation_path(
                intraday_root,
                snapshot,
            )
            first_bytes = observation_path.read_bytes()
            observation = json.loads(first_bytes)
            self.assertEqual(observation["observation"]["kind"], "intraday")
            self.assertFalse(observation["observation"]["streak_eligible"])
            self.assertTrue(
                observation["observation"][
                    "canonical_daily_snapshot_unchanged"
                ]
            )
            self.assertEqual(list(daily_root.glob("*.json")), [canonical_path])
            self.assertEqual(
                _load_dated_json(
                    daily_root,
                    parse_date(snapshot["date"]),
                    "date",
                ),
                [{"date": snapshot["date"], "marker": "canonical"}],
            )

            stderr = StringIO()
            with (
                patch(
                    "scripts.growth.monitor_public_rank.capture",
                    return_value=snapshot,
                ),
                redirect_stderr(stderr),
            ):
                self.assertEqual(main(arguments), 2)
            self.assertEqual(observation_path.read_bytes(), first_bytes)
            self.assertIn("refusing overwrite", stderr.getvalue())
            self.assertEqual(list(intraday_root.rglob("*.tmp")), [])

            later_snapshot = copy.deepcopy(snapshot)
            later = datetime.fromisoformat(snapshot["captured_at"]) + timedelta(
                seconds=1
            )
            later_snapshot["captured_at"] = later.isoformat(timespec="seconds")
            with (
                patch(
                    "scripts.growth.monitor_public_rank.capture",
                    return_value=later_snapshot,
                ),
                redirect_stdout(StringIO()),
            ):
                self.assertEqual(main(arguments), 0)
            self.assertEqual(
                len(list((intraday_root / snapshot["date"]).glob("*.json"))),
                2,
            )
            self.assertEqual(list(daily_root.glob("*.json")), [canonical_path])

    def test_default_intraday_path_is_ignored_local_evidence(self) -> None:
        ignore_lines = (GROWTH_ROOT.parent / ".gitignore").read_text(
            encoding="utf-8"
        ).splitlines()
        self.assertIn("growth/data/public-rank/intraday/", ignore_lines)

    def test_daily_snapshot_collision_during_capture_never_overwrites(self) -> None:
        snapshot = captured_snapshot()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "daily.json"
            preserved = b'{"marker":"first-writer"}\n'

            def capture_after_another_writer(*_args: object) -> dict:
                output.write_bytes(preserved)
                return snapshot

            stderr = StringIO()
            with (
                patch(
                    "scripts.growth.monitor_public_rank.capture",
                    side_effect=capture_after_another_writer,
                ),
                redirect_stderr(stderr),
            ):
                exit_code = main(["--output", str(output)])

            self.assertEqual(exit_code, 2)
            self.assertEqual(output.read_bytes(), preserved)
            self.assertIn("pass --replace to overwrite", stderr.getvalue())
            self.assertEqual(list(output.parent.glob("*.tmp")), [])

    def test_live_modes_reject_output_and_replace_options(self) -> None:
        for arguments in (
            ["--stdout", "--output", "unused.json"],
            ["--check-current", "--replace"],
            ["--intraday-dir", "unused"],
        ):
            with self.subTest(arguments=arguments):
                with (
                    patch("scripts.growth.monitor_public_rank.capture") as capture,
                    redirect_stderr(StringIO()),
                    self.assertRaises(SystemExit),
                ):
                    main(arguments)
                capture.assert_not_called()


if __name__ == "__main__":
    unittest.main()
