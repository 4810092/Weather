from __future__ import annotations

import unittest
from pathlib import Path

from scripts.google_play_vitals_workflow_security import (
    validate_google_play_vitals_workflow,
)


ROOT = Path(__file__).resolve().parents[3]


class GooglePlayVitalsWorkflowSecurityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = (
            ROOT / ".github/workflows/google-play-vitals-readonly.yml"
        ).read_text(encoding="utf-8")

    def assert_rejected(self, mutated: str, needle: str) -> None:
        failures = validate_google_play_vitals_workflow(mutated)
        self.assertTrue(any(needle in failure for failure in failures), failures)

    def test_repository_workflow_passes(self) -> None:
        self.assertEqual(validate_google_play_vitals_workflow(self.workflow), [])

    def test_automatic_trigger_is_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace("  workflow_dispatch:\n", "  workflow_dispatch:\n  schedule:\n", 1),
            "triggers are forbidden",
        )

    def test_write_permission_is_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace("      contents: read\n", "      contents: write\n", 1),
            "forbidden workflow construct",
        )

    def test_wrong_oauth_scope_is_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace("auth/playdeveloperreporting", "auth/androidpublisher"),
            "contract marker count differs",
        )

    def test_action_tag_is_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a",
                "actions/upload-artifact@v4",
            ),
            "reviewed full-commit pins",
        )

    def test_app_testers_cannot_become_canonical(self) -> None:
        self.assert_rejected(self.workflow + "# APP_TESTERS\n", "APP_TESTERS")

    def test_replace_escape_hatch_is_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace('            --output "$normalized"', '            --output "$normalized" --replace'),
            "--replace",
        )


if __name__ == "__main__":
    unittest.main()
