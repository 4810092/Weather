from __future__ import annotations

import unittest
from pathlib import Path

from scripts.hosted_rank_workflow_security import validate_hosted_rank_workflow


ROOT = Path(__file__).resolve().parents[3]


class HostedRankWorkflowSecurityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = (
            ROOT / ".github/workflows/uz-rank-monitor.yml"
        ).read_text(encoding="utf-8")

    def assert_rejected(self, mutated: str, needle: str) -> None:
        failures = validate_hosted_rank_workflow(mutated)
        self.assertTrue(any(needle in failure for failure in failures), failures)

    def test_repository_workflow_passes(self) -> None:
        self.assertEqual(validate_hosted_rank_workflow(self.workflow), [])

    def test_schedule_is_exactly_0005_tashkent(self) -> None:
        self.assert_rejected(
            self.workflow.replace('cron: "5 19 * * *"', 'cron: "0 * * * *"'),
            "daily 19:05 UTC",
        )

    def test_extra_trigger_is_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "  workflow_dispatch:\n",
                "  workflow_dispatch:\n  pull_request:\n",
            ),
            "manual dispatch only",
        )

    def test_capture_cannot_receive_write_token(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "permissions:\n  contents: read\n",
                "permissions:\n  contents: write\n",
            ),
            "top-level permissions",
        )

    def test_write_permission_cannot_expand(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "      contents: write\n",
                "      contents: write\n      issues: write\n",
            ),
            "forbidden workflow construct",
        )

    def test_actions_must_use_reviewed_full_commit_pins(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
                "actions/checkout@v7",
                1,
            ),
            "pin differs",
        )

    def test_non_force_push_is_mandatory(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                'git -C "$state_root" push origin \\\n',
                'git -C "$state_root" push --force origin \\\n',
            ),
            "explicit non-force push",
        )

    def test_replace_escape_hatch_is_forbidden(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                '--output "$snapshot"',
                '--output "$snapshot" --replace',
            ),
            "forbidden workflow construct",
        )

    def test_unknown_capture_must_persist_before_failure(self) -> None:
        marker = "Canonical unknown evidence was persisted; failing closed."
        mutated = self.workflow.replace(marker, "", 1)
        self.assert_rejected(mutated, "marker count differs")

    def test_mutable_state_branch_code_cannot_execute(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "python3 scripts/growth/hosted_rank_state.py install-bundle",
                "python3 $RUNNER_TEMP/state-write/scripts/growth/hosted_rank_state.py "
                "install-bundle",
            ),
            "mutable observation branch",
        )


if __name__ == "__main__":
    unittest.main()
