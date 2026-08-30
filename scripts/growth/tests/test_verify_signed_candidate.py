from __future__ import annotations

import contextlib
import io
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
from scripts.verify_signed_candidate import _build_receipt, _package_candidate, main


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

    def test_receipt_keeps_candidate_schema_version_two(self) -> None:
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
        )

        self.assertEqual(receipt["schema_version"], 2)
        self.assertEqual(
            receipt["state"],
            "candidate-bytes-verified-not-manifest-promoted",
        )

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
                )
                self.assertEqual(receipt["state"], "candidate-verification-failed")

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
