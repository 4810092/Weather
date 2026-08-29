from __future__ import annotations

import csv
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.check_review_inbox import FIELDS, ROOT, validate_review_inbox


class ReviewInboxCheckTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        target = self.root / "growth/reviews"
        target.mkdir(parents=True)
        for filename in ("README.md", "review-inbox.csv"):
            shutil.copy2(ROOT / "growth/reviews" / filename, target / filename)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _read_rows(self) -> list[dict[str, str]]:
        with (self.root / "growth/reviews/review-inbox.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            return list(csv.DictReader(handle))

    def _write_rows(self, rows: list[dict[str, str]]) -> None:
        with (self.root / "growth/reviews/review-inbox.csv").open(
            "w", newline="", encoding="utf-8"
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def _reset_log(self) -> None:
        shutil.copy2(
            ROOT / "growth/reviews/review-inbox.csv",
            self.root / "growth/reviews/review-inbox.csv",
        )

    def _actionable_row(self, **overrides: str) -> dict[str, str]:
        row = {
            "check_id": "play-global-20260830t1200+0500",
            "platform": "google_play",
            "scope": "global_default",
            "source_surface": "play_console_ratings_and_reviews",
            "source_as_of": "2026-08-30T12:00:00+05:00",
            "average_rating": "2.000",
            "rating_count": "2",
            "text_review_count": "1",
            "substantive_review_count": "1",
            "oldest_substantive_review_at": "2026-08-29T12:00:00+05:00",
            "action_at": "",
            "action": "pending",
            "sla_state": "within_48h",
            "notification_state": "not_checked",
        }
        row.update(overrides)
        return row

    def test_repository_review_inbox_matches_contract(self) -> None:
        self.assertEqual(validate_review_inbox(ROOT), [])

    def test_fixture_matches_contract(self) -> None:
        self.assertEqual(validate_review_inbox(self.root), [])

    def test_seed_console_facts_are_exact(self) -> None:
        rows = self._read_rows()
        rows[0]["average_rating"] = "2.000"
        self._write_rows(rows)

        failures = validate_review_inbox(self.root)

        self.assertIn(
            "growth/reviews/review-inbox.csv: seed average_rating '2.000' "
            "differs from '1.000'",
            failures,
        )

    def test_log_rejects_email_like_pii(self) -> None:
        rows = self._read_rows()
        rows[0]["notification_state"] = "reviewer@example.invalid"
        self._write_rows(rows)

        failures = validate_review_inbox(self.root)

        self.assertIn(
            "growth/reviews/review-inbox.csv: must not contain an email address or reviewer PII",
            failures,
        )

    def test_source_as_of_requires_an_explicit_offset(self) -> None:
        rows = self._read_rows()
        rows[0]["source_as_of"] = "2026-08-29T23:40:00"
        self._write_rows(rows)

        failures = validate_review_inbox(self.root)

        self.assertIn(
            "growth/reviews/review-inbox.csv:2: source_as_of must be an "
            "offset-aware ISO-8601 timestamp",
            failures,
        )

    def test_substantive_review_cannot_be_marked_non_actionable(self) -> None:
        rows = self._read_rows()
        rows[0]["text_review_count"] = "1"
        rows[0]["substantive_review_count"] = "1"
        self._write_rows(rows)

        failures = validate_review_inbox(self.root)

        self.assertIn(
            "growth/reviews/review-inbox.csv:2: substantive reviews require pending or reply_sent",
            failures,
        )

    def test_pending_sla_expires_after_48_hours(self) -> None:
        rows = self._read_rows()
        rows.append(
            self._actionable_row(
                oldest_substantive_review_at="2026-08-28T11:59:59+05:00",
            )
        )
        self._write_rows(rows)

        failures = validate_review_inbox(self.root)

        self.assertIn(
            "growth/reviews/review-inbox.csv:3: pending sla_state must be overdue "
            "when derived from timestamps",
            failures,
        )

    def test_pending_overdue_state_matches_timestamp_age(self) -> None:
        rows = self._read_rows()
        rows.append(
            self._actionable_row(
                oldest_substantive_review_at="2026-08-28T11:59:59+05:00",
                sla_state="overdue",
            )
        )
        self._write_rows(rows)

        self.assertEqual(validate_review_inbox(self.root), [])

    def test_late_reply_cannot_be_labelled_within_48_hours(self) -> None:
        rows = self._read_rows()
        rows.append(
            self._actionable_row(
                source_as_of="2026-08-30T13:00:00+05:00",
                oldest_substantive_review_at="2026-08-28T11:59:59+05:00",
                action_at="2026-08-30T12:00:00+05:00",
                action="reply_sent",
            )
        )
        self._write_rows(rows)

        failures = validate_review_inbox(self.root)

        self.assertIn(
            "growth/reviews/review-inbox.csv:3: reply_sent sla_state must be "
            "responded_late when derived from timestamps",
            failures,
        )

    def test_late_reply_state_matches_timestamp_age(self) -> None:
        rows = self._read_rows()
        rows.append(
            self._actionable_row(
                source_as_of="2026-08-30T13:00:00+05:00",
                oldest_substantive_review_at="2026-08-28T11:59:59+05:00",
                action_at="2026-08-30T12:00:00+05:00",
                action="reply_sent",
                sla_state="responded_late",
            )
        )
        self._write_rows(rows)

        self.assertEqual(validate_review_inbox(self.root), [])

    def test_actionable_timestamps_require_explicit_offsets(self) -> None:
        for field in ("oldest_substantive_review_at", "action_at"):
            with self.subTest(field=field):
                rows = self._read_rows()
                row = self._actionable_row(
                    action="reply_sent",
                    action_at="2026-08-30T11:00:00+05:00",
                )
                row[field] = "2026-08-30T11:00:00"
                rows.append(row)
                self._write_rows(rows)

                failures = validate_review_inbox(self.root)

                self.assertIn(
                    f"growth/reviews/review-inbox.csv:3: {field} must be an "
                    "offset-aware ISO-8601 timestamp",
                    failures,
                )
                self._reset_log()

    def test_reply_timestamp_must_be_ordered_and_observed(self) -> None:
        cases = (
            (
                {
                    "oldest_substantive_review_at": "2026-08-30T11:30:00+05:00",
                    "action_at": "2026-08-30T11:00:00+05:00",
                },
                "action_at cannot be earlier than oldest_substantive_review_at",
            ),
            (
                {
                    "action_at": "2026-08-30T12:00:01+05:00",
                },
                "action_at cannot be later than source_as_of",
            ),
        )
        for overrides, expected in cases:
            with self.subTest(expected=expected):
                rows = self._read_rows()
                row = self._actionable_row(
                    action="reply_sent",
                    action_at="2026-08-30T11:00:00+05:00",
                )
                row.update(overrides)
                rows.append(row)
                self._write_rows(rows)

                failures = validate_review_inbox(self.root)

                self.assertIn(
                    f"growth/reviews/review-inbox.csv:3: {expected}",
                    failures,
                )
                self._reset_log()

    def test_readme_must_retain_response_policy(self) -> None:
        path = self.root / "growth/reviews/README.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "sentiment gating", "opinion sorting"
            ),
            encoding="utf-8",
        )

        failures = validate_review_inbox(self.root)

        self.assertIn(
            "growth/reviews/README.md: missing operating contract 'sentiment gating'",
            failures,
        )


if __name__ == "__main__":
    unittest.main()
