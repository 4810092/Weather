#!/usr/bin/env python3
"""Verify one complete signed candidate before manifest promotion."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tarfile
import tempfile
from pathlib import Path

try:
    from scripts.release_artifact_verifier import (
        SignedCandidateVerification,
        load_manifest,
        _snapshot_candidate_tree,
        verification_summary,
        verify_signed_candidate_artifacts,
    )
except ModuleNotFoundError:
    from release_artifact_verifier import (  # type: ignore[no-redef]
        SignedCandidateVerification,
        load_manifest,
        _snapshot_candidate_tree,
        verification_summary,
        verify_signed_candidate_artifacts,
    )


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ARTIFACT_IDS = {"android_phone", "wear_os", "apple"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Verify signed Android phone, Wear OS, and Apple candidate bytes "
            "while the committed upload manifest remains fail-closed."
        )
    )
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=ROOT,
        help="Checkout containing the committed manifest and evidence records",
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        help=(
            "Clean detached checkout used to build the manifest source revision; "
            "defaults to --repository-root"
        ),
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "store/upload-manifest-1.1.0.json",
    )
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--bundletool-jar", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Write the verified JSON receipt outside the candidate byte root",
    )
    parser.add_argument(
        "--package-output",
        type=Path,
        required=True,
        help="Write a tar.gz that preserves the verified candidate tree and modes",
    )
    return parser.parse_args()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _atomic_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        text=True,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _package_candidate(
    artifact_root: Path,
    package_output: Path,
    candidate_set: dict[str, object],
    source_observation_sha256: str | None,
    failures: list[str],
) -> dict[str, object] | None:
    expected_tree_sha256 = candidate_set.get("tree_sha256")
    expected_top_level = candidate_set.get("top_level_entries")
    if not isinstance(expected_tree_sha256, str) or not isinstance(
        expected_top_level, list
    ) or not all(isinstance(value, str) for value in expected_top_level):
        failures.append("signed candidate package: candidate-set receipt is incomplete")
        return None
    package_output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=package_output.parent,
        prefix=f".{package_output.name}.",
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        with tarfile.open(temporary, "w:gz", format=tarfile.PAX_FORMAT) as archive:
            archive.add(artifact_root, arcname="bytes", recursive=True)
        with temporary.open("rb") as source:
            os.fsync(source.fileno())
        with tempfile.TemporaryDirectory(
            prefix="nimbo-signed-candidate-package-check-"
        ) as directory:
            extracted_root = Path(directory)
            with tarfile.open(temporary, "r:gz") as archive:
                archive.extractall(extracted_root, filter="data")
            extracted_snapshot = _snapshot_candidate_tree(
                extracted_root / "bytes",
                failures,
                "packaged signed candidate",
                expected_top_level=set(expected_top_level),
            )
            if (
                extracted_snapshot is None
                or extracted_snapshot.tree_sha256 != expected_tree_sha256
            ):
                failures.append(
                    "signed candidate package: extracted tree differs from verified tree"
                )
        source_after = _snapshot_candidate_tree(
            artifact_root,
            failures,
            "signed candidate after packaging",
            expected_top_level=set(expected_top_level),
        )
        if (
            source_after is None
            or source_after.tree_sha256 != expected_tree_sha256
            or source_after.observation_sha256 != source_observation_sha256
        ):
            failures.append(
                "signed candidate package: source tree changed after verification"
            )
        if failures:
            return None
        temporary.replace(package_output)
        return {
            "filename": package_output.name,
            "format": "tar.gz",
            "sha256": _sha256_file(package_output),
            "candidate_tree_sha256": expected_tree_sha256,
        }
    finally:
        temporary.unlink(missing_ok=True)


def _build_receipt(
    manifest: dict[str, object],
    verification: SignedCandidateVerification,
    package: dict[str, object] | None,
) -> dict[str, object]:
    results = verification.artifacts
    summary = verification_summary(results)
    return {
        **summary,
        "schema_version": 2,
        "release": manifest.get("release"),
        "source_revision": manifest.get("source_revision"),
        "state": (
            "candidate-bytes-verified-not-manifest-promoted"
            if (
                verification.byte_verified
                and package is not None
                and set(results) == EXPECTED_ARTIFACT_IDS
                and all(result.byte_verified for result in results.values())
            )
            else "candidate-verification-failed"
        ),
        "candidate_set": verification.candidate_set,
        "package": package,
        "boundary": (
            "This receipt proves staged signed bytes only. It does not promote "
            "the committed upload manifest, prove physical QA, upload a build, "
            "or establish store availability."
        ),
    }


def main() -> int:
    arguments = parse_args()
    failures: list[str] = []
    manifest = load_manifest(arguments.manifest, failures)
    artifact_root = arguments.artifact_root.resolve()
    output = arguments.output.resolve()
    package_output = arguments.package_output.resolve()
    if output == package_output:
        failures.append(
            "signed candidate receipt and package must use distinct output paths"
        )
    if _is_within(output, artifact_root) or _is_within(package_output, artifact_root):
        failures.append(
            "signed candidate receipt and package must remain outside artifact root"
        )
    verification = verify_signed_candidate_artifacts(
        arguments.repository_root.resolve(),
        manifest,
        failures,
        artifact_root=artifact_root,
        bundletool_jar=arguments.bundletool_jar.resolve(),
        source_repository_root=(
            arguments.source_root.resolve()
            if arguments.source_root is not None
            else arguments.repository_root.resolve()
        ),
    )
    package = None
    if not failures and verification.byte_verified:
        package = _package_candidate(
            artifact_root,
            package_output,
            verification.candidate_set,
            verification.source_observation_sha256,
            failures,
        )
    receipt = _build_receipt(manifest, verification, package)
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if not failures and receipt["state"] == "candidate-bytes-verified-not-manifest-promoted":
        _atomic_text(output, rendered)
        expected_package_sha = package.get("sha256") if package is not None else None
        if (
            not package_output.is_file()
            or not isinstance(expected_package_sha, str)
            or _sha256_file(package_output) != expected_package_sha
        ):
            failures.append(
                "signed candidate package changed or disappeared after receipt write"
            )
    if failures:
        package_output.unlink(missing_ok=True)
        output.unlink(missing_ok=True)
        for failure in failures:
            print(f"signed candidate verification failed: {failure}", file=sys.stderr)
        return 1
    if receipt["state"] != "candidate-bytes-verified-not-manifest-promoted":
        package_output.unlink(missing_ok=True)
        output.unlink(missing_ok=True)
        print("signed candidate verification failed: incomplete candidate", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
