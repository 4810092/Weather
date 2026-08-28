from __future__ import annotations

import csv
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


if __name__ == "__main__":
    unittest.main()
