#!/usr/bin/env python3
"""Mutation tests for the trusted hosted verifier and Pages handoff."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.trusted_release_workflow_security import (  # noqa: E402
    validate_pages_workflow,
    validate_trusted_release_workflow,
)


class TrustedReleaseWorkflowSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.trusted = (
            ROOT / ".github/workflows/trusted-release-verification.yml"
        ).read_text(encoding="utf-8")
        cls.pages = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")

    def assert_trusted_rejected(self, mutated: str) -> None:
        self.assertTrue(validate_trusted_release_workflow(mutated))

    def assert_pages_rejected(self, mutated: str) -> None:
        self.assertTrue(validate_pages_workflow(mutated))

    def test_reviewed_workflows_pass(self) -> None:
        self.assertEqual(validate_trusted_release_workflow(self.trusted), [])
        self.assertEqual(validate_pages_workflow(self.pages), [])

    def test_ci_workflow_identity_and_push_guard_are_immutable(self) -> None:
        self.assert_trusted_rejected(
            self.trusted.replace("workflow_id == 330787648", "workflow_id == 1", 1)
        )
        self.assert_trusted_rejected(
            self.trusted.replace("workflow_run.event == 'push'", "workflow_run.event == 'pull_request'", 1)
        )

    def test_same_repository_and_master_guards_are_immutable(self) -> None:
        self.assert_trusted_rejected(
            self.trusted.replace("github.repository_id == '1329018769' &&\n", "", 1)
        )
        self.assert_trusted_rejected(
            self.trusted.replace("workflow_run.head_branch == 'master'", "workflow_run.head_branch == 'attacker'", 1)
        )

    def test_success_guard_and_exact_checkout_are_immutable(self) -> None:
        self.assert_trusted_rejected(
            self.trusted.replace("workflow_run.conclusion == 'success'", "workflow_run.conclusion != 'cancelled'", 1)
        )
        self.assert_trusted_rejected(
            self.trusted.replace("ref: ${{ github.event.workflow_run.head_sha }}\n", "ref: master\n", 1)
        )

    def test_permissions_secrets_and_runner_mutations_are_rejected(self) -> None:
        self.assert_trusted_rejected(
            self.trusted.replace("      contents: write\n", "      contents: read\n", 1)
        )
        self.assert_trusted_rejected(
            self.trusted.replace("      contents: read\n", "      contents: write\n", 1)
        )
        self.assert_trusted_rejected(
            self.trusted.replace("GH_TOKEN: ${{ github.token }}", "GH_TOKEN: ${{ secrets.ADMIN_TOKEN }}", 1)
        )
        self.assert_trusted_rejected(
            self.trusted.replace("runs-on: macos-26", "runs-on: self-hosted", 1)
        )

    def test_upstream_artifact_and_cache_capabilities_are_rejected(self) -> None:
        marker = "      - name: Validate checked-out verifier authority\n"
        self.assert_trusted_rejected(
            self.trusted.replace(
                marker,
                "      - uses: actions/download-artifact@v4\n" + marker,
                1,
            )
        )
        self.assert_trusted_rejected(
            self.trusted.replace(marker, "      - uses: actions/cache@v4\n" + marker, 1)
        )

    def test_staging_job_cannot_checkout_or_mutate_repository(self) -> None:
        marker = "      - name: Stage exact unpublished candidate without repository checkout\n"
        self.assert_trusted_rejected(
            self.trusted.replace(
                marker,
                "      - uses: actions/checkout@v6\n" + marker,
                1,
            )
        )
        self.assert_trusted_rejected(
            self.trusted.replace(
                "          gh api \\\n",
                "          gh api --method DELETE \\\n",
                1,
            )
        )

    def test_verifier_download_is_same_run_and_tokenless(self) -> None:
        marker = "          path: ${{ runner.temp }}/nimbo-trusted-release/downloads\n"
        self.assert_trusted_rejected(
            self.trusted.replace(marker, marker + "          run-id: 1\n", 1)
        )
        self.assert_trusted_rejected(
            self.trusted.replace(
                marker,
                marker + "          github-token: ${{ secrets.ADMIN_TOKEN }}\n",
                1,
            )
        )
        self.assert_trusted_rejected(
            self.trusted.replace("          retention-days: 1\n", "          retention-days: 90\n", 1)
        )

    def test_verifier_requires_successful_staging_job(self) -> None:
        self.assert_trusted_rejected(
            self.trusted.replace(
                "needs.stage.result == 'success' &&\n",
                "always() &&\n",
                1,
            )
        )

    def test_fixed_release_and_asset_endpoints_are_immutable(self) -> None:
        self.assert_trusted_rejected(
            self.trusted.replace("releases/380406897", "releases/latest", 1)
        )
        self.assert_trusted_rejected(
            self.trusted.replace("releases/assets/539393445", "releases/assets/1", 1)
        )
        self.assert_trusted_rejected(
            self.trusted.replace("releases/assets/539393546", "releases/assets/2", 1)
        )

    def test_draft_and_exact_asset_set_cannot_be_weakened(self) -> None:
        self.assert_trusted_rejected(
            self.trusted.replace('"draft": True', '"draft": False', 1)
        )
        self.assert_trusted_rejected(
            self.trusted.replace(
                "if not isinstance(assets, list) or len(assets) != 2:",
                "if False:",
                1,
            )
        )

    def test_tar_safety_cannot_be_replaced_with_bulk_extraction(self) -> None:
        marker = "              members = archive.getmembers()\n"
        self.assert_trusted_rejected(
            self.trusted.replace(
                marker,
                "              archive.extractall(extraction_root)\n" + marker,
                1,
            )
        )
        self.assert_trusted_rejected(
            self.trusted.replace(
                "if not (member.isfile() or member.isdir()):",
                "if False:",
                1,
            )
        )

    def test_bundletool_and_candidate_hashes_are_immutable(self) -> None:
        self.assert_trusted_rejected(
            self.trusted.replace(
                "a099cfa1543f55593bc2ed16a70a7c67fe54b1747bb7301f37fdfd6d91028e29",
                "0" * 64,
                1,
            )
        )
        self.assert_trusted_rejected(
            self.trusted.replace(
                "c11bc62221c11a16b1d6614aae2060af60ca7b98ad989e68dc5f87c224bbcd89",
                "0" * 64,
                1,
            )
        )

    def test_full_verifier_three_of_three_gate_is_immutable(self) -> None:
        self.assert_trusted_rejected(
            self.trusted.replace(
                "if not isinstance(artifacts, dict) or set(artifacts) != set(expected):",
                "if False:",
                1,
            )
        )
        self.assert_trusted_rejected(
            self.trusted.replace(
                'artifact.get("byte_verified") is not True',
                'artifact.get("byte_verified") is False',
                1,
            )
        )

    def test_prepromotion_manifest_contract_and_exact_full_verifier_are_immutable(self) -> None:
        self.assert_trusted_rejected(
            self.trusted.replace(
                "python3 scripts/verify_release_artifacts.py --contract-only",
                "true",
                1,
            )
        )
        self.assert_trusted_rejected(
            self.trusted.replace(
                'if manifest.get("artifacts") != expected_blocked:',
                "if False:",
                1,
            )
        )
        self.assert_trusted_rejected(
            self.trusted.replace(
                '--manifest "$verification_manifest"',
                "--manifest store/upload-manifest-1.1.0.json",
                1,
            )
        )
        self.assert_trusted_rejected(
            self.trusted.replace(
                'artifact["physical_qa_evidence"] = None',
                'artifact["physical_qa_evidence"] = "invented.md"',
                1,
            )
        )

    def test_receipt_upload_cannot_expand_to_signed_bytes(self) -> None:
        self.assert_trusted_rejected(
            self.trusted.replace(
                "path: ${{ runner.temp }}/nimbo-trusted-receipt/trusted-release-verification.json",
                "path: ${{ runner.temp }}/nimbo-trusted-release",
                1,
            )
        )

    def test_pages_direct_triggers_are_rejected(self) -> None:
        self.assert_pages_rejected(
            self.pages.replace("on:\n", "on:\n  push:\n    branches: [master]\n", 1)
        )
        self.assert_pages_rejected(
            self.pages.replace("on:\n", "on:\n  workflow_dispatch:\n", 1)
        )

    def test_pages_requires_exact_successful_trusted_run(self) -> None:
        self.assert_pages_rejected(
            self.pages.replace("workflow_run.conclusion == 'success'", "workflow_run.conclusion != 'failure'", 1)
        )
        self.assert_pages_rejected(
            self.pages.replace(
                "workflow_run.path == '.github/workflows/trusted-release-verification.yml'",
                "workflow_run.path != ''",
                1,
            )
        )

    def test_pages_exact_checkout_and_static_checks_are_immutable(self) -> None:
        self.assert_pages_rejected(
            self.pages.replace("ref: ${{ github.event.workflow_run.head_sha }}\n", "ref: master\n", 1)
        )
        self.assert_pages_rejected(
            self.pages.replace("verify_release_artifacts.py --contract-only", "verify_release_artifacts.py", 1)
        )

    def test_pages_cannot_receive_private_candidate_bytes(self) -> None:
        marker = "      - name: Build and validate localized site\n"
        self.assert_pages_rejected(
            self.pages.replace(
                marker,
                "      - uses: actions/download-artifact@v4\n" + marker,
                1,
            )
        )
        self.assert_pages_rejected(
            self.pages.replace(
                marker,
                "      - name: Read draft\n        run: gh api repos/4810092/Weather/releases/380406897\n" + marker,
                1,
            )
        )

    def test_pages_live_master_checks_are_immutable(self) -> None:
        self.assert_pages_rejected(
            self.pages.replace(
                "repos/4810092/Weather/git/ref/heads/master",
                "repos/4810092/Weather/git/ref/heads/attacker",
                1,
            )
        )


if __name__ == "__main__":
    unittest.main()
