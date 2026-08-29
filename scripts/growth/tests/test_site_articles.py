from __future__ import annotations

import importlib.util
import csv
import json
import re
import shutil
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("build_site", ROOT / "scripts/build_site.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

EXPECTED_PLANNED_DATES = {
    "september-heat-uv": "2026-09-07",
    "autumn-swings-aqi": "2026-09-21",
    "october-rain-windows": "2026-10-05",
    "october-wind-gusts": "2026-10-19",
    "november-cold-mornings": "2026-11-02",
    "november-ten-day-planning": "2026-11-16",
}


class SiteArticlesTest(unittest.TestCase):
    def test_blocked_articles_are_excluded_from_public_build(self) -> None:
        self.assertEqual(MODULE.load_articles(include_drafts=False), [])
        self.assertEqual(len(MODULE.load_articles(include_drafts=True)), 6)

    def test_backlog_has_two_localized_drafts_per_month_through_november(self) -> None:
        payload = json.loads(MODULE.ARTICLES_SOURCE.read_text(encoding="utf-8"))
        articles = payload["items"]
        self.assertEqual(
            Counter(article["target_month"] for article in articles),
            Counter({"2026-09": 2, "2026-10": 2, "2026-11": 2}),
        )
        self.assertEqual(
            {article["id"] for article in articles},
            set(EXPECTED_PLANNED_DATES),
        )
        for article in articles:
            self.assertEqual(article["id"], article["slug"])
            self.assertEqual(article["status"], "draft-blocked")
            self.assertIsNone(article["published_on"])
            self.assertEqual(set(article["locales"]), set(MODULE.LOCALE_ORDER))
            self.assertGreaterEqual(len(article["source_urls"]), 2)

    def test_article_copy_matches_the_visible_product_contract(self) -> None:
        payload = json.loads(MODULE.ARTICLES_SOURCE.read_text(encoding="utf-8"))
        articles = {article["id"]: article for article in payload["items"]}
        all_copy = json.dumps(payload, ensure_ascii=False)

        unsupported_phrases = (
            "24 soatlik vaqt chizig‘i",
            "24-часовая шкала",
            "24-часовой шкале",
            "24-hour timeline",
            "tanlangan kunning soatlik o‘zgarishlarini",
            "почасовые изменения выбранного дня",
            "selected day’s hourly changes",
            "vaqt tamg‘asini",
            "время данных",
            "data timestamp",
            "Saqlangan prognoz yoshini",
            "Проверьте возраст сохранённого прогноза",
            "Check the age of a saved forecast",
            "11 km",
            "11 км",
        )
        for phrase in unsupported_phrases:
            self.assertNotIn(phrase, all_copy)

        timeline_articles = (
            "september-heat-uv",
            "autumn-swings-aqi",
            "october-rain-windows",
            "october-wind-gusts",
            "november-ten-day-planning",
        )
        timeline_markers = {
            "uz": "24 soat oldin · hozir · 24 soat keyin",
            "ru": "24 часа назад · сейчас · 24 часа вперёд",
            "en": "48-hour timeline",
        }
        for article_id in timeline_articles:
            for locale, marker in timeline_markers.items():
                localized_copy = json.dumps(
                    articles[article_id]["locales"][locale],
                    ensure_ascii=False,
                )
                self.assertIn(marker, localized_copy)

        ten_day = articles["november-ten-day-planning"]["locales"]
        self.assertIn("keyingi 24 soat oynasiga", json.dumps(ten_day["uz"], ensure_ascii=False))
        self.assertIn("в пределах следующих 24 часов", json.dumps(ten_day["ru"], ensure_ascii=False))
        self.assertIn("next-24-hour window", json.dumps(ten_day["en"], ensure_ascii=False))

        aqi = articles["autumn-swings-aqi"]["locales"]
        for locale in MODULE.LOCALE_ORDER:
            self.assertIn("45", json.dumps(aqi[locale], ensure_ascii=False))

    def test_calendar_urls_match_generated_guide_routes(self) -> None:
        with MODULE.CONTENT_CALENDAR_SOURCE.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 18)
        for row in rows:
            self.assertEqual(
                row["canonical_url"],
                MODULE.article_canonical_url(
                    MODULE.CANONICAL_BASE_URL,
                    row["locale"],
                    row["slug"],
                ),
            )

    def test_calendar_uses_one_deterministic_date_per_localized_article(self) -> None:
        with MODULE.CONTENT_CALENDAR_SOURCE.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        dates_by_article: dict[str, set[str]] = {}
        locales_by_article: dict[str, set[str]] = {}
        for row in rows:
            dates_by_article.setdefault(row["content_id"], set()).add(
                row["planned_date"]
            )
            locales_by_article.setdefault(row["content_id"], set()).add(row["locale"])
        self.assertEqual(
            dates_by_article,
            {article_id: {date} for article_id, date in EXPECTED_PLANNED_DATES.items()},
        )
        self.assertEqual(
            locales_by_article,
            {
                article_id: set(MODULE.LOCALE_ORDER)
                for article_id in EXPECTED_PLANNED_DATES
            },
        )

    def test_calendar_requires_every_publication_gate(self) -> None:
        with MODULE.CONTENT_CALENDAR_SOURCE.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        gates = MODULE.load_quality_gates()
        expected = MODULE.publication_gate_ids(gates)
        for row in rows:
            self.assertEqual(expected, set(row["blocked_by"].split("|")))

    def test_new_publication_gate_cannot_bypass_calendar(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            gates_path = Path(directory) / "gates.json"
            gates = json.loads(MODULE.QUALITY_GATES_SOURCE.read_text(encoding="utf-8"))
            gates["gates"]["future_critical_gate"] = {
                "status": "blocked",
                "blocks_publication": True,
                "reason": "synthetic publication blocker",
            }
            gates_path.write_text(json.dumps(gates), encoding="utf-8")

            with mock.patch.object(MODULE, "QUALITY_GATES_SOURCE", gates_path):
                with self.assertRaisesRegex(ValueError, "publication gate set differs"):
                    MODULE.load_articles(include_drafts=False)

    def test_non_publication_gate_is_not_required_in_calendar(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            gates_path = Path(directory) / "gates.json"
            gates = json.loads(MODULE.QUALITY_GATES_SOURCE.read_text(encoding="utf-8"))
            gates["gates"]["internal_only_gate"] = {
                "status": "blocked",
                "blocks_publication": False,
                "reason": "synthetic internal-only blocker",
            }
            gates_path.write_text(json.dumps(gates), encoding="utf-8")

            with mock.patch.object(MODULE, "QUALITY_GATES_SOURCE", gates_path):
                self.assertEqual(MODULE.load_articles(include_drafts=False), [])

    def test_published_status_cannot_bypass_blocked_quality_gates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            articles_path = temporary / "articles.json"
            calendar_path = temporary / "calendar.csv"
            gates_path = temporary / "gates.json"

            articles = json.loads(MODULE.ARTICLES_SOURCE.read_text(encoding="utf-8"))
            for article in articles["items"]:
                article["status"] = "published"
                article["published_on"] = "2026-09-07"
            articles_path.write_text(
                json.dumps(articles, ensure_ascii=False),
                encoding="utf-8",
            )

            with MODULE.CONTENT_CALENDAR_SOURCE.open(
                encoding="utf-8", newline=""
            ) as handle:
                reader = csv.DictReader(handle)
                fieldnames = reader.fieldnames
                rows = list(reader)
            self.assertIsNotNone(fieldnames)
            for row in rows:
                row["status"] = "published"
            with calendar_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            gates_path.write_bytes(MODULE.QUALITY_GATES_SOURCE.read_bytes())

            with (
                mock.patch.object(MODULE, "ARTICLES_SOURCE", articles_path),
                mock.patch.object(MODULE, "CONTENT_CALENDAR_SOURCE", calendar_path),
                mock.patch.object(MODULE, "QUALITY_GATES_SOURCE", gates_path),
            ):
                with self.assertRaisesRegex(ValueError, "publication blocked by"):
                    MODULE.load_articles(include_drafts=False)

    def test_calendar_date_must_match_article_target_month(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            calendar_path = Path(directory) / "calendar.csv"
            with MODULE.CONTENT_CALENDAR_SOURCE.open(
                encoding="utf-8", newline=""
            ) as handle:
                reader = csv.DictReader(handle)
                fieldnames = reader.fieldnames
                rows = list(reader)
            self.assertIsNotNone(fieldnames)
            rows[6]["planned_date"] = "2026-11-05"
            with calendar_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            with mock.patch.object(MODULE, "CONTENT_CALENDAR_SOURCE", calendar_path):
                with self.assertRaisesRegex(ValueError, "differs from target_month"):
                    MODULE.load_articles(include_drafts=True)

    def test_draft_preview_has_localized_routes_and_hreflang(self) -> None:
        build_root = ROOT / "build"
        build_root.mkdir(exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix="site-articles-", dir=build_root))
        shutil.rmtree(output)
        try:
            MODULE.build(
                output,
                "http://127.0.0.1:8765",
                include_drafts=True,
            )
            pages = list(output.glob("**/index.html"))
            self.assertEqual(len(pages), 34)
            article = (
                output / "ru/guides/september-heat-uv/index.html"
            ).read_text(encoding="utf-8")
            self.assertIn(
                'hreflang="uz" href="http://127.0.0.1:8765/guides/september-heat-uv/"',
                article,
            )
            self.assertIn("Публикация заблокирована", article)
            match = re.search(
                r'<script type="application/ld\+json">(.*?)</script>',
                article,
            )
            self.assertIsNotNone(match)
            schema = json.loads(match.group(1))
            self.assertEqual(schema["@type"], "Article")
            self.assertEqual(schema["inLanguage"], "ru")
            self.assertEqual(
                schema["mainEntityOfPage"],
                "http://127.0.0.1:8765/ru/guides/september-heat-uv/",
            )
            self.assertNotIn("datePublished", schema)
            sitemap = (output / "sitemap.xml").read_text(encoding="utf-8")
            self.assertIn("/en/guides/autumn-swings-aqi/", sitemap)
            self.assertIn("/guides/november-cold-mornings/", sitemap)
            self.assertIn("/ru/guides/november-ten-day-planning/", sitemap)
        finally:
            if output.exists():
                shutil.rmtree(output)

    def test_public_site_exposes_factual_search_and_loading_contract(self) -> None:
        build_root = ROOT / "build"
        build_root.mkdir(exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix="site-search-", dir=build_root))
        shutil.rmtree(output)
        try:
            MODULE.build(output, MODULE.CANONICAL_BASE_URL)
            expected = {
                "uz": (
                    output / "index.html",
                    "Nimbo Ob-havo",
                    "hl=uz",
                    True,
                ),
                "ru": (
                    output / "ru/index.html",
                    "Nimbo Погода",
                    "hl=ru",
                    False,
                ),
                "en": (
                    output / "en/index.html",
                    "Nimbo Weather",
                    "hl=en",
                    False,
                ),
            }
            for locale, (path, title_marker, play_locale, has_website) in expected.items():
                document = path.read_text(encoding="utf-8")
                self.assertIn(f"<title>{title_marker}", document)
                self.assertIn(
                    '<meta name="apple-itunes-app" content="app-id=6799886897">',
                    document,
                )
                self.assertIn('<meta name="twitter:image"', document)
                self.assertIn("nimbo-icon-site.png", document)
                self.assertIn('width="1320" height="2868"', document)
                match = re.search(
                    r'<script type="application/ld\+json">(.*?)</script>',
                    document,
                )
                self.assertIsNotNone(match)
                schema = json.loads(match.group(1))
                types = [item["@type"] for item in schema["@graph"]]
                self.assertIn("Organization", types)
                self.assertEqual("WebSite" in types, has_website)
                application = next(
                    item
                    for item in schema["@graph"]
                    if item["@type"] == "SoftwareApplication"
                )
                self.assertEqual(application["inLanguage"], locale)
                self.assertEqual(
                    application["applicationCategory"], "UtilitiesApplication"
                )
                self.assertEqual(application["offers"]["price"], "0")
                self.assertTrue(application["isAccessibleForFree"])
                self.assertIn(play_locale, application["downloadUrl"][1])
                self.assertIn("gl=UZ", application["downloadUrl"][1])
                self.assertNotIn("aggregateRating", json.dumps(schema))

            self.assertLess(MODULE.SITE_ICON_SOURCE.stat().st_size, 64 * 1024)
            self.assertEqual(
                (output / "assets/nimbo-icon-site.png").read_bytes(),
                MODULE.SITE_ICON_SOURCE.read_bytes(),
            )
            press = (output / "press/index.html").read_text(encoding="utf-8")
            self.assertIn('href="../assets/nimbo-icon.png" download', press)
            self.assertGreaterEqual(press.count('loading="lazy"'), 6)
            growth = (output / "growth/index.html").read_text(encoding="utf-8")
            self.assertIn('<meta name="robots" content="noindex,follow">', growth)
            sitemap = (output / "sitemap.xml").read_text(encoding="utf-8")
            self.assertNotIn("/growth/", sitemap)
        finally:
            if output.exists():
                shutil.rmtree(output)


if __name__ == "__main__":
    unittest.main()
