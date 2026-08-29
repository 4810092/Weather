from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.check_release_qa_matrix import (
    AUTHORITY_BLOCK_END,
    AUTHORITY_BLOCK_START,
    AUTHORITY_DOCUMENTS,
    DOCUMENT,
    HISTORICAL_HEADING,
    ROOT,
    expected_authority_block,
    expected_current_block,
    validate,
)


class ReleaseQaMatrixCheckTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self._write_text(
            "app/build.gradle.kts",
            'versionCode = 8\nversionName = "1.1.0"\n',
        )
        self._write_text(
            "wearApp/build.gradle.kts",
            'versionCode = 1_000_008\nversionName = "1.1.0"\n',
        )
        self._write_text(
            "iosApp/project.yml",
            "MARKETING_VERSION: 1.1.0\nCURRENT_PROJECT_VERSION: 6\n",
        )
        self.source_revision = self._commit_release_source()
        self._write_text("growth/evidence.md", "fixture evidence\n")
        self._write_json(
            "store/upload-manifest-1.1.0.json",
            {
                "release": "1.1.0",
                "source_revision": self.source_revision,
                "artifacts": {
                    "android_phone": {
                        "version_code": 8,
                        "source_sync": "blocked",
                        "sha256": "a" * 64,
                        "signing_evidence": "growth/evidence.md",
                        "physical_qa_evidence": "growth/evidence.md",
                        "source_sync_evidence": "growth/evidence.md",
                        "historical_candidate": {"version_code": 7},
                    },
                    "wear_os": {
                        "version_code": 1_000_008,
                        "source_sync": "blocked",
                        "sha256": "b" * 64,
                        "signing_evidence": "growth/evidence.md",
                        "physical_qa_evidence": "growth/evidence.md",
                        "source_sync_evidence": "growth/evidence.md",
                        "historical_candidate": {"version_code": 1_000_008},
                    },
                    "apple": {
                        "build": 6,
                        "source_sync": "blocked",
                        "sha256": "c" * 64,
                        "signing_evidence": "growth/evidence.md",
                        "physical_qa_evidence": "growth/evidence.md",
                        "source_sync_evidence": "growth/evidence.md",
                        "historical_candidate": {"build": 5},
                    },
                },
            },
        )
        self._write_json(
            "growth/quality/gates.json",
            {
                "gates": {
                    "release_artifact_source_sync": self._gate(
                        "blocked", source_revision=self.source_revision
                    ),
                    "android_physical_smoke": self._gate("blocked"),
                    "ios_physical_smoke": self._gate("blocked"),
                }
            },
        )
        self._write_document()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    @staticmethod
    def _gate(
        status: str, *, source_revision: str | None = None
    ) -> dict[str, object]:
        gate: dict[str, object] = {
            "status": status,
            "blocks_publication": True,
            "reason": "fixture gate evidence",
        }
        if source_revision is not None:
            gate["source_revision"] = source_revision
        return gate

    def _commit_release_source(self) -> str:
        commands = (
            ["init", "--quiet"],
            ["config", "user.email", "release-test@example.invalid"],
            ["config", "user.name", "Release test"],
            ["add", "app", "wearApp", "iosApp"],
            ["commit", "--quiet", "-m", "Fixture release source"],
        )
        for command in commands:
            subprocess.run(
                ["git", *command],
                cwd=self.root,
                check=True,
                capture_output=True,
                text=True,
            )
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=self.root, text=True
        ).strip()

    def _write_text(self, relative: str | Path, content: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _write_json(self, relative: str, payload: object) -> None:
        self._write_text(relative, json.dumps(payload, indent=2) + "\n")

    def _read_json(self, relative: str) -> dict:
        return json.loads((self.root / relative).read_text(encoding="utf-8"))

    def _write_document(self) -> None:
        block, failures, historical_identities = expected_current_block(self.root)
        self.assertEqual(failures, [])
        self.assertIsNotNone(block)
        authority_block, authority_failures = expected_authority_block(self.root)
        self.assertEqual(authority_failures, [])
        self.assertIsNotNone(authority_block)
        assert authority_block is not None
        for relative in AUTHORITY_DOCUMENTS:
            if relative != DOCUMENT:
                self._write_text(
                    relative,
                    f"# Fixture narrative\n\n{authority_block}\n",
                )
        historical_rows = "\n".join(f"- {identity}" for identity in historical_identities)
        self._write_text(
            DOCUMENT,
            "# Release QA matrix\n\n"
            f"{authority_block}\n\n"
            "## Exact-current candidate\n\n"
            f"{block}\n\n"
            f"{HISTORICAL_HEADING}\n\n"
            "Historical evidence cannot satisfy exact-current QA.\n\n"
            f"{historical_rows}\n",
        )

    def _set_ready_authority(self) -> None:
        manifest = self._read_json("store/upload-manifest-1.1.0.json")
        for artifact in manifest["artifacts"].values():
            artifact["source_sync"] = "verified-current"
        self._write_json("store/upload-manifest-1.1.0.json", manifest)
        gates = self._read_json("growth/quality/gates.json")
        for gate in gates["gates"].values():
            gate["status"] = "pass"
        self._write_json("growth/quality/gates.json", gates)

    def test_repository_matrix_matches_current_authority(self) -> None:
        self.assertEqual(validate(ROOT), [])

    def test_fixture_contract_passes(self) -> None:
        self.assertEqual(validate(self.root), [])

    def test_narrative_source_revision_drift_fails_closed(self) -> None:
        path = self.root / "growth/README.md"
        document = path.read_text(encoding="utf-8")
        path.write_text(
            document.replace(self.source_revision, "f" * 40),
            encoding="utf-8",
        )

        failures = validate(self.root)

        self.assertIn(
            "growth/README.md: current authority block differs from upload manifest/gates",
            failures,
        )

    def test_narrative_physical_gate_drift_fails_closed(self) -> None:
        path = self.root / "docs/GROWTH_RELEASE.md"
        document = path.read_text(encoding="utf-8")
        path.write_text(
            document.replace(
                "physical_gate:android_physical_smoke=blocked",
                "physical_gate:android_physical_smoke=pass",
            ),
            encoding="utf-8",
        )

        failures = validate(self.root)

        self.assertIn(
            "docs/GROWTH_RELEASE.md: current authority block differs from upload manifest/gates",
            failures,
        )

    def test_physical_gate_reason_change_invalidates_narratives(self) -> None:
        gates = self._read_json("growth/quality/gates.json")
        gates["gates"]["android_physical_smoke"]["reason"] = (
            "new bounded physical evidence"
        )
        self._write_json("growth/quality/gates.json", gates)

        failures = validate(self.root)

        self.assertIn(
            "docs/QA_MATRIX.md: current authority block differs from upload manifest/gates",
            failures,
        )

    def test_manifest_physical_evidence_change_invalidates_narratives(self) -> None:
        self._write_text("growth/second-evidence.md", "new fixture evidence\n")
        manifest = self._read_json("store/upload-manifest-1.1.0.json")
        manifest["artifacts"]["android_phone"]["physical_qa_evidence"] = (
            "growth/second-evidence.md"
        )
        self._write_json("store/upload-manifest-1.1.0.json", manifest)

        failures = validate(self.root)

        self.assertIn(
            "docs/RELEASE.md: current authority block differs from upload manifest/gates",
            failures,
        )

    def test_each_narrative_requires_exact_authority_markers(self) -> None:
        path = self.root / "docs/RELEASE.md"
        document = path.read_text(encoding="utf-8")
        start = document.index(AUTHORITY_BLOCK_START)
        end = document.index(AUTHORITY_BLOCK_END, start) + len(AUTHORITY_BLOCK_END)
        path.write_text(document[:start] + document[end:], encoding="utf-8")

        failures = validate(self.root)

        self.assertIn(
            "docs/RELEASE.md: current authority block markers must each appear once",
            failures,
        )

    def test_manifest_identity_drift_fails_closed(self) -> None:
        manifest = self._read_json("store/upload-manifest-1.1.0.json")
        manifest["artifacts"]["android_phone"]["version_code"] = 9
        self._write_json("store/upload-manifest-1.1.0.json", manifest)

        failures = validate(self.root)

        self.assertIn(
            "android_phone: manifest version_code 9 differs from build 8",
            failures,
        )

    def test_release_source_change_makes_recorded_revision_stale(self) -> None:
        path = self.root / "app/build.gradle.kts"
        path.write_text(path.read_text(encoding="utf-8") + "// product change\n")

        failures = validate(self.root)

        self.assertTrue(
            any(
                failure.startswith(
                    "upload manifest: source_revision "
                    f"{self.source_revision} is stale for release source: "
                )
                and "app/build.gradle.kts" in failure
                for failure in failures
            )
        )

    def test_release_gate_revision_must_match_manifest(self) -> None:
        gates = self._read_json("growth/quality/gates.json")
        gates["gates"]["release_artifact_source_sync"]["source_revision"] = "f" * 40
        self._write_json("growth/quality/gates.json", gates)

        failures = validate(self.root)

        self.assertIn(
            "quality gates: release_artifact_source_sync source_revision "
            f"{'f' * 40!r} differs from upload manifest {self.source_revision!r}",
            failures,
        )

    def test_source_revision_requires_full_lowercase_commit(self) -> None:
        manifest = self._read_json("store/upload-manifest-1.1.0.json")
        manifest["source_revision"] = self.source_revision[:12]
        self._write_json("store/upload-manifest-1.1.0.json", manifest)

        failures = validate(self.root)

        self.assertIn(
            "upload manifest: source_revision must be a full lowercase 40-hex commit",
            failures,
        )

    def test_source_revision_must_be_a_commit_object(self) -> None:
        tree_revision = subprocess.check_output(
            ["git", "rev-parse", f"{self.source_revision}^{{tree}}"],
            cwd=self.root,
            text=True,
        ).strip()
        manifest = self._read_json("store/upload-manifest-1.1.0.json")
        manifest["source_revision"] = tree_revision
        self._write_json("store/upload-manifest-1.1.0.json", manifest)
        gates = self._read_json("growth/quality/gates.json")
        gates["gates"]["release_artifact_source_sync"][
            "source_revision"
        ] = tree_revision
        self._write_json("growth/quality/gates.json", gates)

        failures = validate(self.root)

        self.assertIn(
            "upload manifest: source_revision "
            f"{tree_revision} must identify a commit object, got tree",
            failures,
        )

    def test_untracked_release_source_fails_closed(self) -> None:
        self._write_text("shared/src/new-product-file.kt", "package fixture\n")

        failures = validate(self.root)

        self.assertIn(
            "upload manifest: untracked release source prevents exact-source proof: "
            "shared/src/new-product-file.kt",
            failures,
        )

    def test_ignored_untracked_release_source_fails_closed(self) -> None:
        ignored_path = "shared/src/commonMain/kotlin/IgnoredProductFile.kt"
        self._write_text(".gitignore", f"/{ignored_path}\n")
        self._write_text(ignored_path, "package fixture\n")

        failures = validate(self.root)

        self.assertIn(
            "upload manifest: untracked release source prevents exact-source proof: "
            f"{ignored_path}",
            failures,
        )

    def test_gate_change_invalidates_a_stale_ready_block(self) -> None:
        self._set_ready_authority()
        gates = self._read_json("growth/quality/gates.json")
        self._write_document()
        self.assertEqual(validate(self.root), [])

        gates["gates"]["android_physical_smoke"]["status"] = "blocked"
        self._write_json("growth/quality/gates.json", gates)

        failures = validate(self.root)

        self.assertIn(
            "docs/QA_MATRIX.md: exact-current block differs from build/manifest/gate authority",
            failures,
        )

    def test_unknown_source_sync_is_not_rendered_as_blocked_or_ready(self) -> None:
        manifest = self._read_json("store/upload-manifest-1.1.0.json")
        manifest["artifacts"]["wear_os"]["source_sync"] = "probably-current"
        self._write_json("store/upload-manifest-1.1.0.json", manifest)

        failures = validate(self.root)

        self.assertIn("wear_os: invalid source_sync 'probably-current'", failures)

    def test_historical_identity_must_remain_in_non_transferable_section(self) -> None:
        path = self.root / "docs/QA_MATRIX.md"
        document = path.read_text(encoding="utf-8")
        path.write_text(document.replace("- `1.1.0 (7)`\n", ""), encoding="utf-8")

        failures = validate(self.root)

        self.assertIn(
            "docs/QA_MATRIX.md: historical section is missing manifest identity `1.1.0 (7)`",
            failures,
        )

    def test_missing_source_sync_evidence_fails_closed(self) -> None:
        (self.root / "growth/evidence.md").unlink()

        failures = validate(self.root)

        self.assertTrue(
            any("source_sync_evidence is missing" in failure for failure in failures)
        )

    def test_ready_requires_a_64_hex_sha256(self) -> None:
        self._set_ready_authority()
        manifest = self._read_json("store/upload-manifest-1.1.0.json")
        manifest["artifacts"]["android_phone"]["sha256"] = "not-a-digest"
        self._write_json("store/upload-manifest-1.1.0.json", manifest)

        failures = validate(self.root)

        self.assertIn(
            "android_phone: READY requires sha256 to be 64 hexadecimal characters",
            failures,
        )

    def test_ready_requires_existing_signing_evidence(self) -> None:
        self._set_ready_authority()
        manifest = self._read_json("store/upload-manifest-1.1.0.json")
        manifest["artifacts"]["wear_os"]["signing_evidence"] = None
        self._write_json("store/upload-manifest-1.1.0.json", manifest)

        failures = validate(self.root)

        self.assertIn(
            "wear_os: READY signing_evidence must be an existing repository-relative file path",
            failures,
        )

    def test_ready_requires_existing_physical_qa_evidence(self) -> None:
        self._set_ready_authority()
        manifest = self._read_json("store/upload-manifest-1.1.0.json")
        manifest["artifacts"]["apple"]["physical_qa_evidence"] = (
            "growth/missing-physical-evidence.md"
        )
        self._write_json("store/upload-manifest-1.1.0.json", manifest)

        failures = validate(self.root)

        self.assertIn(
            "apple: READY physical_qa_evidence is missing: "
            "growth/missing-physical-evidence.md",
            failures,
        )


if __name__ == "__main__":
    unittest.main()
