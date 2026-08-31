from __future__ import annotations

import contextlib
import hashlib
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.release_artifact_verifier import (
    SignedCandidateVerification,
    VerificationResult,
    _snapshot_candidate_tree,
)
from scripts.verify_signed_candidate import (
    _build_receipt,
    _package_candidate,
    _sha256_file,
    _validate_apple_profile_bindings,
    _validate_provenance,
    main,
)


class VerifySignedCandidatePackageTest(unittest.TestCase):
    def _verified_artifacts(self) -> dict[str, VerificationResult]:
        return {
            artifact_id: VerificationResult(
                artifact_id=artifact_id,
                source_sync="candidate-byte-verified",
                byte_verified=True,
                sha256=character * 64,
            )
            for artifact_id, character in (
                ("android_phone", "a"),
                ("wear_os", "b"),
                ("apple", "c"),
            )
        }

    def _receipt_provenance(self) -> dict[str, object]:
        return {
            "provider": "github-actions",
            "run": {"id": 33375162729, "attempt": 1},
            "source": {
                "head_sha": "1" * 40,
                "ref": "refs/heads/master",
            },
            "workflow": {
                "path": ".github/workflows/signed-candidate.yml",
                "sha256": "2" * 64,
            },
            "verifiers": {
                "verify_signed_candidate.py": {"sha256": "3" * 64},
                "release_artifact_verifier.py": {"sha256": "4" * 64},
            },
        }

    def _apple_profile_bindings(self) -> dict[str, object]:
        profiles: dict[str, dict[str, str]] = {}
        for index, (role, bundle_id) in enumerate(
            (
                ("app", "uz.ganikhodjaev.weather"),
                ("widget", "uz.ganikhodjaev.weather.widget"),
                ("watch", "uz.ganikhodjaev.weather.watchkitapp"),
            ),
            start=1,
        ):
            profiles[role] = {
                "bundle_id": bundle_id,
                "name": f"iOS Team Store Provisioning Profile: {bundle_id}",
                "sha256": str(index) * 64,
                "uuid": f"{index * 11111111:08d}-{index * 1111:04d}-{index * 1111:04d}-"
                f"{index * 1111:04d}-{index * 111111111111:012d}",
            }
        return {"schema_version": 1, "profiles": profiles}

    def _verification_with_apple_profiles(self) -> SignedCandidateVerification:
        artifacts = self._verified_artifacts()
        profiles = self._apple_profile_bindings()["profiles"]
        assert isinstance(profiles, dict)
        products = [
            {
                "role": role,
                "bundle_id": profile["bundle_id"],
                "provisioning_profile": {
                    "name": profile["name"],
                    "sha256": profile["sha256"],
                    "uuid": profile["uuid"],
                },
            }
            for role, profile in profiles.items()
        ]
        artifacts["apple"] = VerificationResult(
            artifact_id="apple",
            source_sync="candidate-byte-verified",
            byte_verified=True,
            sha256="c" * 64,
            details={
                "products": products,
                "archive_products": products,
            },
        )
        return SignedCandidateVerification(
            artifacts=artifacts,
            candidate_set={"tree_sha256": "b" * 64},
            byte_verified=True,
        )

    def test_receipt_schema_three_binds_required_provenance(self) -> None:
        verification = SignedCandidateVerification(
            artifacts=self._verified_artifacts(),
            candidate_set={"tree_sha256": "b" * 64},
            byte_verified=True,
        )

        receipt = _build_receipt(
            {"release": "1.1.0", "source_revision": "c" * 40},
            verification,
            {
                "filename": "signed-candidate-bytes.tar.gz",
                "sha256": "d" * 64,
            },
            self._receipt_provenance(),
            self._apple_profile_bindings(),
        )

        self.assertEqual(receipt["schema_version"], 3)
        self.assertEqual(receipt["provenance"], self._receipt_provenance())
        self.assertEqual(
            receipt["signing_provenance"]["apple_profiles"],
            self._apple_profile_bindings(),
        )
        self.assertEqual(
            receipt["state"],
            "candidate-bytes-verified-not-manifest-promoted",
        )

    def test_receipt_fails_closed_without_provenance(self) -> None:
        verification = SignedCandidateVerification(
            artifacts=self._verified_artifacts(),
            candidate_set={"tree_sha256": "b" * 64},
            byte_verified=True,
        )

        receipt = _build_receipt(
            {"release": "1.1.0", "source_revision": "c" * 40},
            verification,
            {
                "filename": "signed-candidate-bytes.tar.gz",
                "sha256": "d" * 64,
            },
            None,
            self._apple_profile_bindings(),
        )

        self.assertEqual(receipt["schema_version"], 3)
        self.assertIsNone(receipt["provenance"])
        self.assertEqual(receipt["state"], "candidate-verification-failed")

    def test_receipt_fails_closed_without_apple_profile_provenance(self) -> None:
        verification = SignedCandidateVerification(
            artifacts=self._verified_artifacts(),
            candidate_set={"tree_sha256": "b" * 64},
            byte_verified=True,
        )

        receipt = _build_receipt(
            {"release": "1.1.0", "source_revision": "c" * 40},
            verification,
            {
                "filename": "signed-candidate-bytes.tar.gz",
                "sha256": "d" * 64,
            },
            self._receipt_provenance(),
            None,
        )

        self.assertIsNone(
            receipt["signing_provenance"]["apple_profiles"]
        )
        self.assertEqual(receipt["state"], "candidate-verification-failed")

    def test_receipt_rejects_missing_or_extra_artifact_results(self) -> None:
        for artifacts in (
            {},
            {"android_phone": self._verified_artifacts()["android_phone"]},
            {
                **self._verified_artifacts(),
                "unexpected": VerificationResult(
                    artifact_id="unexpected",
                    source_sync="candidate-byte-verified",
                    byte_verified=True,
                    sha256="d" * 64,
                ),
            },
        ):
            with self.subTest(artifact_ids=sorted(artifacts)):
                verification = SignedCandidateVerification(
                    artifacts=artifacts,
                    candidate_set={"tree_sha256": "e" * 64},
                    byte_verified=True,
                )
                receipt = _build_receipt(
                    {"release": "1.1.0", "source_revision": "f" * 40},
                    verification,
                    {
                        "filename": "signed-candidate-bytes.tar.gz",
                        "sha256": "0" * 64,
                    },
                    self._receipt_provenance(),
                    self._apple_profile_bindings(),
                )
                self.assertEqual(receipt["state"], "candidate-verification-failed")

    def test_apple_profile_bindings_match_both_verified_products(self) -> None:
        verification = self._verification_with_apple_profiles()
        bindings = self._apple_profile_bindings()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profiles.json"
            path.write_text(json.dumps(bindings), encoding="utf-8")
            failures: list[str] = []

            validated = _validate_apple_profile_bindings(
                path,
                verification,
                failures,
            )

        self.assertEqual(failures, [])
        self.assertEqual(validated, bindings)

    def test_apple_profile_bindings_reject_secret_or_embedded_mismatch(self) -> None:
        verification = self._verification_with_apple_profiles()
        bindings = self._apple_profile_bindings()
        profiles = bindings["profiles"]
        assert isinstance(profiles, dict)
        profiles["widget"]["sha256"] = "f" * 64
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profiles.json"
            path.write_text(json.dumps(bindings), encoding="utf-8")
            failures: list[str] = []

            validated = _validate_apple_profile_bindings(
                path,
                verification,
                failures,
            )

        self.assertIsNone(validated)
        self.assertTrue(
            any(
                "products widget profile differs from the protected input binding"
                in failure
                for failure in failures
            ),
            failures,
        )

    def _provenance_fixture(
        self,
        root: Path,
        **overrides: object,
    ) -> SimpleNamespace:
        workflow = root / ".github/workflows/signed-candidate.yml"
        workflow.parent.mkdir(parents=True, exist_ok=True)
        workflow.write_text("name: Signed candidate\n", encoding="utf-8")
        values: dict[str, object] = {
            "repository_root": root,
            "workflow_run_id": "33375162729",
            "workflow_run_attempt": "1",
            "workflow_head_sha": "1" * 40,
            "workflow_ref": "refs/heads/master",
            "workflow_path": ".github/workflows/signed-candidate.yml",
            "workflow_sha256": hashlib.sha256(workflow.read_bytes()).hexdigest(),
            "verify_signed_candidate_sha256": _sha256_file(
                Path(__file__).resolve().parents[2] / "verify_signed_candidate.py"
            ),
            "release_artifact_verifier_sha256": _sha256_file(
                Path(__file__).resolve().parents[2] / "release_artifact_verifier.py"
            ),
        }
        values.update(overrides)
        return SimpleNamespace(**values)

    def test_provenance_validation_binds_run_workflow_and_verifier_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            arguments = self._provenance_fixture(root)
            failures: list[str] = []

            with patch(
                "scripts.verify_signed_candidate._git_head_sha",
                return_value="1" * 40,
            ):
                provenance = _validate_provenance(arguments, failures)

        self.assertEqual(failures, [])
        self.assertIsNotNone(provenance)
        assert provenance is not None
        self.assertEqual(provenance["provider"], "github-actions")
        self.assertEqual(provenance["run"], {"id": 33375162729, "attempt": 1})
        self.assertEqual(
            provenance["source"],
            {"head_sha": "1" * 40, "ref": "refs/heads/master"},
        )
        self.assertEqual(
            provenance["workflow"],
            {
                "path": ".github/workflows/signed-candidate.yml",
                "sha256": arguments.workflow_sha256,
            },
        )
        self.assertEqual(
            provenance["verifiers"],
            {
                "verify_signed_candidate.py": {
                    "sha256": arguments.verify_signed_candidate_sha256,
                },
                "release_artifact_verifier.py": {
                    "sha256": arguments.release_artifact_verifier_sha256,
                },
            },
        )

    def test_provenance_validation_rejects_malformed_coordinates(self) -> None:
        cases = (
            ({"workflow_run_id": "0"}, "run id"),
            ({"workflow_run_attempt": "01"}, "run attempt"),
            ({"workflow_head_sha": "A" * 40}, "workflow head SHA"),
            ({"workflow_ref": "refs/heads/../master"}, "workflow ref"),
            ({"workflow_path": "../signed-candidate.yml"}, "workflow path"),
            (
                {"workflow_path": ".github/workflows/other.yml"},
                "workflow path",
            ),
            ({"workflow_sha256": "A" * 64}, "workflow SHA-256"),
        )
        for overrides, expected_failure in cases:
            with self.subTest(overrides=overrides):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    arguments = self._provenance_fixture(root, **overrides)
                    failures: list[str] = []
                    with patch(
                        "scripts.verify_signed_candidate._git_head_sha",
                        return_value="1" * 40,
                    ):
                        provenance = _validate_provenance(arguments, failures)
                self.assertIsNone(provenance)
                self.assertTrue(
                    any(expected_failure in failure for failure in failures),
                    failures,
                )

    def test_provenance_validation_rejects_head_or_file_hash_mismatch(self) -> None:
        cases = (
            ({}, "workflow head SHA differs from repository HEAD", "2" * 40),
            ({"workflow_sha256": "0" * 64}, "workflow SHA-256 differs", "1" * 40),
            (
                {"verify_signed_candidate_sha256": "0" * 64},
                "verify_signed_candidate.py SHA-256 differs",
                "1" * 40,
            ),
            (
                {"release_artifact_verifier_sha256": "0" * 64},
                "release_artifact_verifier.py SHA-256 differs",
                "1" * 40,
            ),
        )
        for overrides, expected_failure, repository_head in cases:
            with self.subTest(overrides=overrides):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    arguments = self._provenance_fixture(root, **overrides)
                    failures: list[str] = []
                    with patch(
                        "scripts.verify_signed_candidate._git_head_sha",
                        return_value=repository_head,
                    ):
                        provenance = _validate_provenance(arguments, failures)
                self.assertIsNone(provenance)
                self.assertTrue(
                    any(expected_failure in failure for failure in failures),
                    failures,
                )

    def test_cli_rejects_receipt_package_path_alias(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact_root = root / "bytes"
            artifact_root.mkdir()
            alias = root / "candidate-output"
            arguments = SimpleNamespace(
                repository_root=root,
                source_root=root,
                manifest=root / "manifest.json",
                artifact_root=artifact_root,
                bundletool_jar=root / "bundletool.jar",
                output=alias,
                package_output=alias,
                apple_profile_bindings=root / "profiles.json",
            )
            verification = SignedCandidateVerification(
                artifacts=self._verified_artifacts(),
                candidate_set={},
                byte_verified=True,
            )
            stderr = io.StringIO()
            with (
                patch(
                    "scripts.verify_signed_candidate.parse_args",
                    return_value=arguments,
                ),
                patch(
                    "scripts.verify_signed_candidate.load_manifest",
                    return_value={
                        "release": "1.1.0",
                        "source_revision": "a" * 40,
                    },
                ),
                patch(
                    "scripts.verify_signed_candidate.verify_signed_candidate_artifacts",
                    return_value=verification,
                ),
                patch(
                    "scripts.verify_signed_candidate._validate_provenance",
                    return_value=self._receipt_provenance(),
                ),
                patch(
                    "scripts.verify_signed_candidate._validate_apple_profile_bindings",
                    return_value=self._apple_profile_bindings(),
                ),
                contextlib.redirect_stderr(stderr),
            ):
                self.assertEqual(main(), 1)
            self.assertIn("distinct output paths", stderr.getvalue())
            self.assertFalse(alias.exists())

    def test_package_preserves_verified_tree_bytes_and_modes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = root / "bytes"
            candidate.mkdir(mode=0o700)
            executable = candidate / "Nimbo.xcarchive/Products/Nimbo"
            executable.parent.mkdir(parents=True)
            executable.write_bytes(b"mach-o")
            executable.chmod(0o755)
            mapping = candidate / "mapping.txt"
            mapping.write_text("mapping\n", encoding="utf-8")
            mapping.chmod(0o600)
            failures: list[str] = []
            snapshot = _snapshot_candidate_tree(
                candidate,
                failures,
                "fixture candidate",
                expected_top_level={"Nimbo.xcarchive", "mapping.txt"},
            )
            self.assertIsNotNone(snapshot)
            assert snapshot is not None

            package_path = root / "package/signed-candidate-bytes.tar.gz"
            package = _package_candidate(
                candidate,
                package_path,
                snapshot.receipt(),
                snapshot.observation_sha256,
                failures,
            )

            self.assertEqual(failures, [])
            self.assertIsNotNone(package)
            self.assertTrue(package_path.is_file())
            with tempfile.TemporaryDirectory() as extracted_directory:
                extracted = Path(extracted_directory)
                with tarfile.open(package_path, "r:gz") as archive:
                    archive.extractall(extracted, filter="data")
                extracted_snapshot = _snapshot_candidate_tree(
                    extracted / "bytes",
                    failures,
                    "extracted fixture candidate",
                    expected_top_level={"Nimbo.xcarchive", "mapping.txt"},
                )
            self.assertEqual(failures, [])
            self.assertIsNotNone(extracted_snapshot)
            assert extracted_snapshot is not None
            self.assertEqual(extracted_snapshot.tree_sha256, snapshot.tree_sha256)


if __name__ == "__main__":
    unittest.main()
