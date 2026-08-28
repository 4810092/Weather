from __future__ import annotations

import importlib.util
import csv
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("build_site", ROOT / "scripts/build_site.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SiteArticlesTest(unittest.TestCase):
    def test_blocked_articles_are_excluded_from_public_build(self) -> None:
        self.assertEqual(MODULE.load_articles(include_drafts=False), [])
        self.assertEqual(len(MODULE.load_articles(include_drafts=True)), 2)

    def test_calendar_urls_match_generated_guide_routes(self) -> None:
        with MODULE.CONTENT_CALENDAR_SOURCE.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 6)
        for row in rows:
            self.assertEqual(
                row["canonical_url"],
                MODULE.article_canonical_url(
                    MODULE.CANONICAL_BASE_URL,
                    row["locale"],
                    row["slug"],
                ),
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
            self.assertEqual(len(pages), 22)
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
        finally:
            if output.exists():
                shutil.rmtree(output)


if __name__ == "__main__":
    unittest.main()
