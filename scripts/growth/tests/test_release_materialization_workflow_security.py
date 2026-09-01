from __future__ import annotations

import unittest
from pathlib import Path

from scripts.release_materialization_workflow_security import (
    validate_release_materialization_workflow,
)


ROOT = Path(__file__).resolve().parents[3]


class ReleaseMaterializationWorkflowSecurityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = (
            ROOT / ".github/workflows/release-materialization.yml"
        ).read_text(encoding="utf-8")

    def assert_rejected(self, mutated: str, needle: str) -> None:
        failures = validate_release_materialization_workflow(mutated)
        self.assertTrue(
            any(needle in failure for failure in failures),
            failures,
        )

    def test_repository_workflow_passes(self) -> None:
        self.assertEqual(
            validate_release_materialization_workflow(self.workflow),
            [],
        )

    def test_non_manual_trigger_is_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace("  workflow_dispatch:\n", "  push:\n", 1),
            "trigger must be exactly manual",
        )

    def test_permission_expansion_and_missing_write_are_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace("  actions: read\n", "  actions: write\n", 1),
            "permissions must be exactly",
        )
        self.assert_rejected(
            self.workflow.replace("  contents: write\n", "  contents: read\n", 1),
            "permissions must be exactly",
        )
        self.assert_rejected(
            self.workflow.replace(
                "  contents: write\n",
                "  contents: write\n  id-token: write\n",
                1,
            ),
            "permissions must be exactly",
        )

    def test_repository_identity_and_master_guards_are_rejected_on_drift(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                " && github.repository_id == '1329018769'",
                "",
                1,
            ),
            "exact repository/id/master guard",
        )
        self.assert_rejected(
            self.workflow.replace(
                "github.ref == 'refs/heads/master'",
                "github.ref == 'refs/heads/attacker'",
                1,
            ),
            "exact repository/id/master guard",
        )

    def test_self_hosted_or_mutable_action_is_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace("runs-on: ubuntu-24.04", "runs-on: self-hosted", 1),
            "standard ubuntu-24.04",
        )
        self.assert_rejected(
            self.workflow.replace(
                "actions/download-artifact@"
                "3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c",
                "actions/download-artifact@v7",
                1,
            ),
            "download action block differs",
        )

    def test_exact_run_and_artifact_action_inputs_are_immutable(self) -> None:
        self.assert_rejected(
            self.workflow.replace('artifact-ids: "9795391062"', 'artifact-ids: "1"', 1),
            "download action block differs",
        )
        self.assert_rejected(
            self.workflow.replace('run-id: "33493356066"', 'run-id: "1"', 1),
            "download action block differs",
        )
        self.assert_rejected(
            self.workflow.replace('digest-mismatch: error', 'digest-mismatch: warn', 1),
            "download action block differs",
        )

    def test_source_artifact_and_receipt_hashes_are_immutable(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "8cd4bdae3f9f7087ce6c4b05b35f0406d3801f59799d195ddef06b92a2c9ec11",
                "0" * 64,
                1,
            ),
            "materialization run block differs",
        )
        self.assert_rejected(
            self.workflow.replace(
                "cb26a7d69fd35676957a6bfa6984f148fbe874959c133c95029e0688132ee023",
                "0" * 64,
                1,
            ),
            "materialization run block differs",
        )

    def test_secret_binding_and_shell_tracing_are_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "GH_TOKEN: ${{ github.token }}",
                "GH_TOKEN: ${{ secrets.RELEASE_TOKEN }}",
                1,
            ),
            "secrets are forbidden",
        )
        self.assert_rejected(
            self.workflow.replace("          set +x\n", "          set -x\n", 1),
            "shell tracing is forbidden",
        )

    def test_extra_step_or_error_suppression_is_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "      - name: Verify exact unpublished materialization\n",
                "      - name: Extra mutation\n"
                "        shell: bash\n"
                "        run: |\n"
                "          true\n"
                "\n"
                "      - name: Verify exact unpublished materialization\n",
                1,
            ),
            "step inventory differs",
        )
        self.assert_rejected(
            self.workflow.replace(
                "        shell: bash\n",
                "        continue-on-error: true\n        shell: bash\n",
                1,
            ),
            "error suppression is forbidden",
        )

    def test_yaml_flow_alias_and_environment_expansion_are_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace("jobs:\n", "attacker: {}\njobs:\n", 1),
            "flow mappings/lists",
        )
        self.assert_rejected(
            self.workflow.replace("        env:\n", "        env: &token_env\n", 1),
            "anchors and aliases",
        )
        self.assert_rejected(
            self.workflow.replace(
                "    runs-on: ubuntu-24.04\n",
                "    environment: release-signing\n    runs-on: ubuntu-24.04\n",
                1,
            ),
            "must not gain environment secrets",
        )

    def test_draft_prerelease_and_exact_target_are_immutable(self) -> None:
        self.assert_rejected(
            self.workflow.replace('"draft": True', '"draft": False', 1),
            "forbidden publication",
        )
        self.assert_rejected(
            self.workflow.replace('"prerelease": True', '"prerelease": False', 1),
            "forbidden publication",
        )
        self.assert_rejected(
            self.workflow.replace(
                '"target_commitish": os.environ["GITHUB_SHA"]',
                '"target_commitish": "master"',
                1,
            ),
            "materialization run block differs",
        )

    def test_publishing_clobbering_and_deletion_are_rejected(self) -> None:
        marker = "          release_root=\"$RUNNER_TEMP/nimbo-materialization-release\"\n"
        self.assert_rejected(
            self.workflow.replace(marker, marker + "          gh release create bad\n", 1),
            "forbidden publication",
        )
        self.assert_rejected(
            self.workflow.replace(marker, marker + "          gh release upload --clobber bad\n", 1),
            "forbidden publication",
        )
        self.assert_rejected(
            self.workflow.replace(marker, marker + "          gh api --method DELETE bad\n", 1),
            "forbidden publication",
        )

    def test_bulk_extraction_or_download_execution_is_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "              infos = archive.infolist()\n",
                "              archive.extractall(asset_root)\n"
                "              infos = archive.infolist()\n",
                1,
            ),
            "must never be executed or bulk-extracted",
        )

    def test_tar_safety_and_exact_final_asset_set_are_immutable(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "          if len(package_members) != 192 or len(set(package_names)) != 192:\n",
                "          if False:\n",
                1,
            ),
            "materialization run block differs",
        )
        self.assert_rejected(
            self.workflow.replace(
                '          if {asset.get("name") for asset in assets} != set(expected):\n',
                "          if False:\n",
                1,
            ),
            "materialization run block differs",
        )

    def test_pre_and_post_tag_absence_checks_are_immutable(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "matching-refs/tags/nimbo-candidate-v1.1.0-8fc43b4-run-33493356066",
                "matching-refs/tags/different",
                1,
            ),
            "candidate Git-tag absence must be checked before and after",
        )


if __name__ == "__main__":
    unittest.main()
