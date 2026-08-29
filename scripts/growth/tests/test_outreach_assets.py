from __future__ import annotations

import csv
import re
import unittest
from datetime import date

from scripts.growth.common import GROWTH_ROOT


class OutreachAssetsTest(unittest.TestCase):
    def test_research_shortlist_is_concrete_dated_and_unsent(self) -> None:
        path = GROWTH_ROOT / "outreach" / "contact-research.csv"
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

        self.assertEqual(len(rows), 15)
        self.assertEqual(len({row["contact_id"] for row in rows}), 15)

        required = {
            "contact_id",
            "segment",
            "outlet_or_community",
            "role_or_contact_name",
            "official_site_url",
            "official_contact_page_url",
            "public_contact_channel",
            "contact_status",
            "verified_on",
            "why_fit",
            "personalization_hook",
            "hook_source_url",
            "preferred_language",
            "last_contacted",
            "follow_up_due",
        }
        self.assertTrue(required.issubset(rows[0]))

        for row in rows:
            with self.subTest(contact_id=row["contact_id"]):
                for field in required - {"last_contacted", "follow_up_due"}:
                    self.assertTrue(row[field].strip(), field)
                self.assertEqual(row["contact_status"], "verified_public_channel")
                self.assertLessEqual(date.fromisoformat(row["verified_on"]), date.today())
                self.assertTrue(row["official_site_url"].startswith("https://"))
                self.assertTrue(row["official_contact_page_url"].startswith("https://"))
                self.assertTrue(row["hook_source_url"].startswith("https://"))
                self.assertNotIn("research_required", " ".join(row.values()))
                self.assertNotIn("[", row["personalization_hook"])
                self.assertEqual(row["last_contacted"], "")
                self.assertEqual(row["follow_up_due"], "")

    def test_personalized_drafts_cover_shortlist_once_and_remain_unsent(self) -> None:
        outreach_root = GROWTH_ROOT / "outreach"
        with (outreach_root / "contact-research.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            contacts = {row["contact_id"]: row for row in csv.DictReader(handle)}

        with (outreach_root / "draft-manifest.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            manifest = list(csv.DictReader(handle))

        self.assertEqual(len(manifest), 15)
        self.assertEqual({row["contact_id"] for row in manifest}, set(contacts))
        self.assertEqual(len({row["draft_path"] for row in manifest}), 15)
        self.assertEqual(
            {outreach_root / row["draft_path"] for row in manifest},
            set((outreach_root / "drafts").glob("UZ-*.md")),
        )

        placeholder = re.compile(r"\[(?:имя|ism|name|канал|channel|конкрет)", re.I)
        for row in manifest:
            with self.subTest(contact_id=row["contact_id"]):
                source = contacts[row["contact_id"]]
                self.assertEqual(
                    row["outlet_or_community"], source["outlet_or_community"]
                )
                self.assertIn(row["language"], source["preferred_language"].split("/"))
                self.assertEqual(
                    row["public_contact_channel"], source["public_contact_channel"]
                )
                self.assertEqual(row["hook_source_url"], source["hook_source_url"])
                self.assertEqual(row["status"], "draft_only_not_sent")
                self.assertEqual(row["follow_up_count"], "1")
                self.assertEqual(row["last_contacted"], "")

                draft_path = outreach_root / row["draft_path"]
                self.assertTrue(draft_path.is_file())
                text = draft_path.read_text(encoding="utf-8")
                self.assertIn("Status: `draft_only_not_sent`", text)
                self.assertIn(source["public_contact_channel"], text)
                self.assertIn(source["hook_source_url"], text)
                self.assertEqual(text.count("## First message"), 1)
                self.assertEqual(text.count("## Follow-up"), 1)
                self.assertIsNone(placeholder.search(text))


if __name__ == "__main__":
    unittest.main()
