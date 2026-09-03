from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from scripts.check_featuring_candidate_freshness import (
    validate_featuring_candidate,
)


ROOT = Path(__file__).resolve().parents[3]


class FeaturingCandidateFreshnessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(
            (ROOT / "growth/featuring/manifest.json").read_text(encoding="utf-8")
        )
        cls.upload = json.loads(
            (ROOT / "store/upload-manifest-1.1.0.json").read_text(encoding="utf-8")
        )
        cls.gates = json.loads(
            (ROOT / "growth/quality/gates.json").read_text(encoding="utf-8")
        )
        cls.apple = (ROOT / "growth/featuring/apple-2026-09.md").read_text(
            encoding="utf-8"
        )
        cls.google = (ROOT / "growth/featuring/google-2026-09.md").read_text(
            encoding="utf-8"
        )

    def validate(self, *, manifest=None, upload=None, gates=None, apple=None, google=None):
        return validate_featuring_candidate(
            manifest if manifest is not None else self.manifest,
            upload if upload is not None else self.upload,
            gates if gates is not None else self.gates,
            apple if apple is not None else self.apple,
            google if google is not None else self.google,
            root=ROOT,
        )

    def assert_rejected(self, failures: list[str], needle: str) -> None:
        self.assertTrue(any(needle in failure for failure in failures), failures)

    def test_repository_candidate_is_current_and_blocked(self) -> None:
        self.assertEqual(self.validate(), [])

    def test_upload_identity_drift_invalidates_drafts(self) -> None:
        upload = copy.deepcopy(self.upload)
        upload["artifacts"]["android_phone"]["version_code"] = 12
        self.assert_rejected(
            self.validate(upload=upload),
            "Google phone draft does not name current upload identity",
        )

    def test_candidate_claim_must_preserve_every_unproved_boundary(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        claim = next(
            item
            for item in manifest["verified_claims"]
            if item["id"] == "candidate_artifact_boundary"
        )
        claim["claim"] = claim["claim"].replace("post-delivery Vitals, ", "")
        self.assert_rejected(
            self.validate(manifest=manifest),
            "candidate artifact claim omits: post-delivery Vitals",
        )

    def test_blocker_status_must_match_canonical_gate(self) -> None:
        gates = copy.deepcopy(self.gates)
        gates["gates"]["ios_physical_smoke"]["status"] = "blocked"
        self.assert_rejected(
            self.validate(gates=gates),
            "blocker ios_physical_smoke differs",
        )

    def test_internal_delivery_cannot_be_erased(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["campaign"]["external_actions_performed"] = []
        self.assert_rejected(
            self.validate(manifest=manifest),
            "internal delivery actions differ",
        )

    def test_public_release_cannot_be_claimed_or_unblocked(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["status"] = "ready"
        blocker = next(
            item
            for item in manifest["blockers"]
            if item["id"] == "deliverable.candidate_public_release"
        )
        blocker["status"] = "pass"
        failures = self.validate(manifest=manifest)
        self.assert_rejected(failures, "must remain draft-blocked")
        self.assert_rejected(failures, "public release blocker")

    def test_stale_evidence_list_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        claim = next(
            item
            for item in manifest["verified_claims"]
            if item["id"] == "candidate_artifact_boundary"
        )
        claim["evidence"][-1] = "growth/quality/testflight-ios-build7-smoke-2026-09-01.md"
        self.assert_rejected(
            self.validate(manifest=manifest),
            "evidence list differs",
        )


if __name__ == "__main__":
    unittest.main()
