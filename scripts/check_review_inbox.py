#!/usr/bin/env python3
"""Validate the aggregate, non-PII store review inbox operating record."""

from __future__ import annotations

import csv
import io
import re
import sys
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README_PATH = Path("growth/reviews/README.md")
LOG_PATH = Path("growth/reviews/review-inbox.csv")
FIELDS = (
    "check_id",
    "platform",
    "scope",
    "source_surface",
    "source_as_of",
    "average_rating",
    "rating_count",
    "text_review_count",
    "substantive_review_count",
    "oldest_substantive_review_at",
    "action_at",
    "action",
    "sla_state",
    "notification_state",
)
SEED_ID = "play-global-20260829t2340+0500"
SEED_EXPECTED = {
    "platform": "google_play",
    "scope": "global_default",
    "source_surface": "play_console_ratings_and_reviews",
    "source_as_of": "2026-08-29T23:40:00+05:00",
    "average_rating": "1.000",
    "rating_count": "1",
    "text_review_count": "0",
    "substantive_review_count": "0",
    "oldest_substantive_review_at": "",
    "action_at": "",
    "action": "none",
    "sla_state": "non_actionable",
    "notification_state": (
        "account_wide_all_1_to_5_star_and_edited_reviews_saved_to_"
        "developer_account_email"
    ),
}
SOURCE_SURFACES = {
    "google_play": "play_console_ratings_and_reviews",
    "app_store": "app_store_connect_reviews",
}
VALID_SCOPES = {"global_default", "uz"}
VALID_ACTIONS = {"none", "pending", "reply_sent"}
VALID_SLA_STATES = {
    "non_actionable",
    "within_48h",
    "overdue",
    "responded_late",
}
VALID_NOTIFICATION_STATES = {
    "account_wide_all_1_to_5_star_and_edited_reviews_saved_to_"
    "developer_account_email",
    "not_checked",
    "unavailable",
}
README_REQUIRED_SNIPPETS = (
    "developer account email",
    "all 1–5-star",
    "nimbo-uz-rank-monitor",
    "once per day after `09:15`",
    "respond within 48",
    "star-only rating is non-actionable",
    "never offer incentives",
    "sentiment gating",
    "ask for a higher rating",
    "do not store reviewer names",
    "when the same issue repeats",
    "add a regression test",
    "current app store review/rating state is unavailable",
    "oldest_substantive_review_at",
    "action_at",
    "derived from timestamps",
)
EMAIL_PATTERN = re.compile(
    r"(?i)(?<![a-z0-9._%+-])[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}(?![a-z0-9.-])"
)
CHECK_ID_PATTERN = re.compile(
    r"(?:play|apple)-(?:global|uz)-\d{8}t\d{4}[+-]\d{4}\Z"
)
RATING_PATTERN = re.compile(r"(?:[0-4]\.\d{3}|5\.000)\Z")
COUNT_PATTERN = re.compile(r"(?:0|[1-9]\d*)\Z")
RESPONSE_SLA = timedelta(hours=48)


def _read_text(path: Path, label: str, failures: list[str]) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        failures.append(f"{label}: cannot read: {error}")
        return None


def _non_negative_count(
    value: str,
    field: str,
    line_number: int,
    failures: list[str],
) -> int | None:
    if COUNT_PATTERN.fullmatch(value) is None:
        failures.append(
            f"{LOG_PATH}:{line_number}: {field} must be a non-negative integer"
        )
        return None
    return int(value)


def _offset_timestamp(
    value: str,
    field: str,
    line_number: int,
    failures: list[str],
    *,
    required: bool,
) -> datetime | None:
    if not value:
        if required:
            failures.append(
                f"{LOG_PATH}:{line_number}: {field} must be an offset-aware ISO-8601 timestamp"
            )
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        parsed = None
    if parsed is None or parsed.utcoffset() is None:
        failures.append(
            f"{LOG_PATH}:{line_number}: {field} must be an offset-aware ISO-8601 timestamp"
        )
        return None
    return parsed


def validate_review_inbox(root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    readme = _read_text(root / README_PATH, str(README_PATH), failures)
    raw_log = _read_text(root / LOG_PATH, str(LOG_PATH), failures)
    if readme is None or raw_log is None:
        return failures

    readme_lower = " ".join(readme.lower().split())
    for snippet in README_REQUIRED_SNIPPETS:
        if snippet not in readme_lower:
            failures.append(f"{README_PATH}: missing operating contract {snippet!r}")
    if EMAIL_PATTERN.search(readme):
        failures.append(f"{README_PATH}: must not contain an email address")
    if EMAIL_PATTERN.search(raw_log):
        failures.append(f"{LOG_PATH}: must not contain an email address or reviewer PII")

    reader = csv.DictReader(io.StringIO(raw_log), strict=True)
    if reader.fieldnames != list(FIELDS):
        failures.append(
            f"{LOG_PATH}: header must be exactly {','.join(FIELDS)}"
        )
        return failures

    try:
        rows = list(reader)
    except csv.Error as error:
        failures.append(f"{LOG_PATH}: malformed CSV: {error}")
        return failures
    if not rows:
        failures.append(f"{LOG_PATH}: at least one aggregate observation is required")
        return failures

    seen_ids: set[str] = set()
    seen_observations: set[tuple[str, str, str]] = set()
    dated_rows: list[tuple[datetime, int]] = []
    seed_rows: list[dict[str, str]] = []

    for line_number, row in enumerate(rows, start=2):
        if None in row or any(value is None for value in row.values()):
            failures.append(f"{LOG_PATH}:{line_number}: row width differs from header")
            continue
        if any(value != value.strip() for value in row.values()):
            failures.append(f"{LOG_PATH}:{line_number}: values must not have edge whitespace")

        check_id = row["check_id"]
        if CHECK_ID_PATTERN.fullmatch(check_id) is None:
            failures.append(f"{LOG_PATH}:{line_number}: invalid check_id {check_id!r}")
        if check_id in seen_ids:
            failures.append(f"{LOG_PATH}:{line_number}: duplicate check_id {check_id!r}")
        seen_ids.add(check_id)

        platform = row["platform"]
        expected_surface = SOURCE_SURFACES.get(platform)
        if expected_surface is None:
            failures.append(f"{LOG_PATH}:{line_number}: invalid platform {platform!r}")
        elif row["source_surface"] != expected_surface:
            failures.append(
                f"{LOG_PATH}:{line_number}: {platform} requires source_surface "
                f"{expected_surface!r}"
            )
        if row["scope"] not in VALID_SCOPES:
            failures.append(
                f"{LOG_PATH}:{line_number}: invalid scope {row['scope']!r}"
            )
        elif expected_surface is not None:
            platform_id = "play" if platform == "google_play" else "apple"
            scope_id = "global" if row["scope"] == "global_default" else "uz"
            if not check_id.startswith(f"{platform_id}-{scope_id}-"):
                failures.append(
                    f"{LOG_PATH}:{line_number}: check_id must match platform and scope"
                )

        source_as_of = row["source_as_of"]
        observed_at = _offset_timestamp(
            source_as_of,
            "source_as_of",
            line_number,
            failures,
            required=True,
        )
        if observed_at is not None:
            dated_rows.append((observed_at, line_number))

        observation_key = (platform, row["scope"], source_as_of)
        if observation_key in seen_observations:
            failures.append(
                f"{LOG_PATH}:{line_number}: duplicate platform/scope/source_as_of observation"
            )
        seen_observations.add(observation_key)

        rating = row["average_rating"]
        if RATING_PATTERN.fullmatch(rating) is None:
            failures.append(
                f"{LOG_PATH}:{line_number}: average_rating must be 0.000 through 5.000"
            )
        else:
            try:
                Decimal(rating)
            except InvalidOperation:
                failures.append(
                    f"{LOG_PATH}:{line_number}: average_rating is not decimal"
                )

        rating_count = _non_negative_count(
            row["rating_count"], "rating_count", line_number, failures
        )
        text_count = _non_negative_count(
            row["text_review_count"], "text_review_count", line_number, failures
        )
        substantive_count = _non_negative_count(
            row["substantive_review_count"],
            "substantive_review_count",
            line_number,
            failures,
        )
        if rating_count is not None and text_count is not None and text_count > rating_count:
            failures.append(
                f"{LOG_PATH}:{line_number}: text_review_count exceeds rating_count"
            )
        if (
            text_count is not None
            and substantive_count is not None
            and substantive_count > text_count
        ):
            failures.append(
                f"{LOG_PATH}:{line_number}: substantive_review_count exceeds text_review_count"
            )

        action = row["action"]
        sla_state = row["sla_state"]
        oldest_review_raw = row["oldest_substantive_review_at"]
        action_at_raw = row["action_at"]
        if action not in VALID_ACTIONS:
            failures.append(f"{LOG_PATH}:{line_number}: invalid action {action!r}")
        if sla_state not in VALID_SLA_STATES:
            failures.append(
                f"{LOG_PATH}:{line_number}: invalid sla_state {sla_state!r}"
            )
        if substantive_count == 0:
            if action != "none" or sla_state != "non_actionable":
                failures.append(
                    f"{LOG_PATH}:{line_number}: zero substantive reviews require "
                    "action=none and sla_state=non_actionable"
                )
            if oldest_review_raw or action_at_raw:
                failures.append(
                    f"{LOG_PATH}:{line_number}: zero substantive reviews require "
                    "empty oldest_substantive_review_at and action_at"
                )
        elif substantive_count is not None:
            oldest_review_at = _offset_timestamp(
                oldest_review_raw,
                "oldest_substantive_review_at",
                line_number,
                failures,
                required=True,
            )
            if action == "pending":
                if action_at_raw:
                    failures.append(
                        f"{LOG_PATH}:{line_number}: pending action requires empty action_at"
                    )
                if observed_at is not None and oldest_review_at is not None:
                    if oldest_review_at > observed_at:
                        failures.append(
                            f"{LOG_PATH}:{line_number}: oldest_substantive_review_at "
                            "cannot be later than source_as_of"
                        )
                    else:
                        expected_sla = (
                            "within_48h"
                            if observed_at - oldest_review_at <= RESPONSE_SLA
                            else "overdue"
                        )
                        if sla_state != expected_sla:
                            failures.append(
                                f"{LOG_PATH}:{line_number}: pending sla_state must be "
                                f"{expected_sla} when derived from timestamps"
                            )
            elif action == "reply_sent":
                action_at = _offset_timestamp(
                    action_at_raw,
                    "action_at",
                    line_number,
                    failures,
                    required=True,
                )
                if oldest_review_at is not None and action_at is not None:
                    if action_at < oldest_review_at:
                        failures.append(
                            f"{LOG_PATH}:{line_number}: action_at cannot be earlier than "
                            "oldest_substantive_review_at"
                        )
                    else:
                        expected_sla = (
                            "within_48h"
                            if action_at - oldest_review_at <= RESPONSE_SLA
                            else "responded_late"
                        )
                        if sla_state != expected_sla:
                            failures.append(
                                f"{LOG_PATH}:{line_number}: reply_sent sla_state must be "
                                f"{expected_sla} when derived from timestamps"
                            )
                if observed_at is not None and action_at is not None and action_at > observed_at:
                    failures.append(
                        f"{LOG_PATH}:{line_number}: action_at cannot be later than source_as_of"
                    )
            elif action == "none":
                failures.append(
                    f"{LOG_PATH}:{line_number}: substantive reviews require pending or reply_sent"
                )

        if row["notification_state"] not in VALID_NOTIFICATION_STATES:
            failures.append(
                f"{LOG_PATH}:{line_number}: invalid notification_state "
                f"{row['notification_state']!r}"
            )
        if check_id == SEED_ID:
            seed_rows.append(row)

    if dated_rows != sorted(dated_rows, key=lambda item: item[0]):
        failures.append(f"{LOG_PATH}: observations must be ordered by source_as_of")

    if len(seed_rows) != 1:
        failures.append(f"{LOG_PATH}: expected exactly one seed observation {SEED_ID!r}")
    else:
        seed = seed_rows[0]
        for field, expected in SEED_EXPECTED.items():
            if seed[field] != expected:
                failures.append(
                    f"{LOG_PATH}: seed {field} {seed[field]!r} differs from {expected!r}"
                )

    return failures


def main() -> int:
    failures = validate_review_inbox()
    if failures:
        for failure in failures:
            print(f"review inbox check failed: {failure}", file=sys.stderr)
        return 1
    print("Review inbox check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
