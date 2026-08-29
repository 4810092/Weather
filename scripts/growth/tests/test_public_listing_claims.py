from __future__ import annotations

import copy
import json
import unittest

from scripts import check_google_play_public_claims as public_claims


class PublicListingClaimsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = json.loads(
            public_claims.METADATA.read_text(encoding="utf-8")
        )

    def test_current_repository_contract_passes(self) -> None:
        self.assertEqual(public_claims.validate(), [])

    def test_copy_drift_requires_a_new_audit(self) -> None:
        changed = copy.deepcopy(self.metadata)
        listing = public_claims.audited_listing(changed)
        self.assertIsNotNone(listing)
        listing["custom_listing"]["localizations"]["en-US"][
            "short_description"
        ] += " Yangi."

        failures = public_claims.validate_metadata(changed)

        self.assertTrue(
            any("payload changed after the public-claims audit" in item for item in failures)
        )

    def test_targeting_drift_is_rejected(self) -> None:
        changed = copy.deepcopy(self.metadata)
        listing = public_claims.audited_listing(changed)
        self.assertIsNotNone(listing)
        listing["custom_listing"]["targeting"]["country_targets"] = ["UZ", "KZ"]

        failures = public_claims.validate_metadata(changed)

        self.assertIn(
            "audited listing targeting drifted from country UZ",
            failures,
        )

    def test_creative_set_drift_is_rejected(self) -> None:
        changed = copy.deepcopy(self.metadata)
        listing = public_claims.audited_listing(changed)
        self.assertIsNotNone(listing)
        listing["creative_set"] = "unreviewed-candidate"

        failures = public_claims.validate_metadata(changed)

        self.assertTrue(any("creative_set drifted" in item for item in failures))

    def test_support_url_drift_is_rejected(self) -> None:
        changed = copy.deepcopy(self.metadata)
        listing = public_claims.audited_listing(changed)
        self.assertIsNotNone(listing)
        listing["support_url"] = "https://example.invalid/support"

        failures = public_claims.validate_metadata(changed)

        self.assertTrue(any("support_url drifted" in item for item in failures))

    def test_hold_marker_cannot_be_removed_silently(self) -> None:
        text = public_claims.AUDIT_DOC.read_text(encoding="utf-8")

        failures = public_claims.validate_audit_text(
            text.replace("**Custom-listing Console submission: HOLD.**", "")
        )

        self.assertTrue(any("Console submission: HOLD" in item for item in failures))


if __name__ == "__main__":
    unittest.main()
