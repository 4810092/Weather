#!/usr/bin/env python3
"""Verify one complete signed candidate before manifest promotion."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

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
EXPECTED_WORKFLOW_PATH = PurePosixPath(".github/workflows/signed-candidate.yml")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
GIT_COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")
POSITIVE_INTEGER_PATTERN = re.compile(r"[1-9][0-9]*")
GITHUB_REF_PATTERN = re.compile(
    r"refs/(?:heads|tags)/[A-Za-z0-9][A-Za-z0-9._/-]{0,1000}"
)
PROFILE_UUID_PATTERN = re.compile(
    r"[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}"
)
EXPECTED_APPLE_PROFILES = {
    "app": "uz.ganikhodjaev.weather",
    "widget": "uz.ganikhodjaev.weather.widget",
    "watch": "uz.ganikhodjaev.weather.watchkitapp",
}


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
    parser.add_argument("--workflow-run-id", required=True)
    parser.add_argument("--workflow-run-attempt", required=True)
    parser.add_argument("--workflow-head-sha", required=True)
    parser.add_argument("--workflow-ref", required=True)
    parser.add_argument("--workflow-path", required=True)
    parser.add_argument("--workflow-sha256", required=True)
    parser.add_argument("--verify-signed-candidate-sha256", required=True)
    parser.add_argument("--release-artifact-verifier-sha256", required=True)
    parser.add_argument(
        "--apple-profile-bindings",
        type=Path,
        required=True,
        help=(
            "Non-secret JSON binding the protected profile UUIDs and hashes to "
            "the profiles embedded in the signed IPA"
        ),
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


def _positive_integer(
    value: object,
    label: str,
    failures: list[str],
    *,
    maximum_digits: int,
) -> int | None:
    if (
        not isinstance(value, str)
        or len(value) > maximum_digits
        or POSITIVE_INTEGER_PATTERN.fullmatch(value) is None
    ):
        failures.append(
            f"signed candidate provenance: {label} must be a positive integer"
        )
        return None
    return int(value)


def _sha256(
    value: object,
    label: str,
    failures: list[str],
) -> str | None:
    if not isinstance(value, str) or SHA256_PATTERN.fullmatch(value) is None:
        failures.append(
            f"signed candidate provenance: {label} must be a lowercase SHA-256"
        )
        return None
    return value


def _git_head_sha(repository_root: Path, failures: list[str]) -> str | None:
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(repository_root),
                "rev-parse",
                "--verify",
                "HEAD^{commit}",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as error:
        failures.append(
            "signed candidate provenance: cannot resolve repository HEAD "
            f"({type(error).__name__})"
        )
        return None
    head_sha = result.stdout.strip()
    if GIT_COMMIT_PATTERN.fullmatch(head_sha) is None:
        failures.append("signed candidate provenance: repository HEAD is not a commit SHA")
        return None
    return head_sha


def _validate_provenance(
    arguments: argparse.Namespace,
    failures: list[str],
) -> dict[str, object] | None:
    run_id = _positive_integer(
        arguments.workflow_run_id,
        "run id",
        failures,
        maximum_digits=20,
    )
    run_attempt = _positive_integer(
        arguments.workflow_run_attempt,
        "run attempt",
        failures,
        maximum_digits=10,
    )

    head_sha = arguments.workflow_head_sha
    if not isinstance(head_sha, str) or GIT_COMMIT_PATTERN.fullmatch(head_sha) is None:
        failures.append(
            "signed candidate provenance: workflow head SHA must be a lowercase commit SHA"
        )
        head_sha = None

    workflow_ref = arguments.workflow_ref
    if (
        not isinstance(workflow_ref, str)
        or GITHUB_REF_PATTERN.fullmatch(workflow_ref) is None
        or ".." in workflow_ref
        or "//" in workflow_ref
        or workflow_ref.endswith(("/", "."))
    ):
        failures.append(
            "signed candidate provenance: workflow ref must be a canonical branch or tag ref"
        )
        workflow_ref = None

    workflow_path_value = arguments.workflow_path
    workflow_path: PurePosixPath | None = None
    if isinstance(workflow_path_value, str):
        candidate_path = PurePosixPath(workflow_path_value)
        if (
            not candidate_path.is_absolute()
            and str(candidate_path) == workflow_path_value
            and candidate_path.parts[:2] == (".github", "workflows")
            and len(candidate_path.parts) == 3
            and candidate_path == EXPECTED_WORKFLOW_PATH
            and candidate_path.suffix in {".yml", ".yaml"}
            and ".." not in candidate_path.parts
            and re.fullmatch(r"[A-Za-z0-9._-]+\.ya?ml", candidate_path.name)
            is not None
        ):
            workflow_path = candidate_path
    if workflow_path is None:
        failures.append(
            "signed candidate provenance: workflow path must be "
            f"{EXPECTED_WORKFLOW_PATH}"
        )

    workflow_sha256 = _sha256(
        arguments.workflow_sha256,
        "workflow SHA-256",
        failures,
    )
    verifier_sha256 = _sha256(
        arguments.verify_signed_candidate_sha256,
        "verify_signed_candidate.py SHA-256",
        failures,
    )
    artifact_verifier_sha256 = _sha256(
        arguments.release_artifact_verifier_sha256,
        "release_artifact_verifier.py SHA-256",
        failures,
    )

    repository_root = arguments.repository_root.resolve()
    repository_head = _git_head_sha(repository_root, failures)
    if (
        head_sha is not None
        and repository_head is not None
        and head_sha != repository_head
    ):
        failures.append(
            "signed candidate provenance: workflow head SHA differs from repository HEAD"
        )

    files = {
        "workflow": (
            repository_root.joinpath(*workflow_path.parts)
            if workflow_path is not None
            else None,
            workflow_sha256,
        ),
        "verify_signed_candidate.py": (
            Path(__file__).resolve(),
            verifier_sha256,
        ),
        "release_artifact_verifier.py": (
            Path(__file__).resolve().with_name("release_artifact_verifier.py"),
            artifact_verifier_sha256,
        ),
    }
    for label, (path, expected_sha256) in files.items():
        if path is None or expected_sha256 is None:
            continue
        if path.is_symlink() or not path.is_file():
            failures.append(
                f"signed candidate provenance: {label} is not a regular file"
            )
            continue
        if label == "workflow" and not _is_within(path, repository_root):
            failures.append(
                "signed candidate provenance: workflow path escapes repository root"
            )
            continue
        if _sha256_file(path) != expected_sha256:
            failures.append(
                f"signed candidate provenance: {label} SHA-256 differs from file bytes"
            )

    if failures:
        return None
    assert run_id is not None
    assert run_attempt is not None
    assert head_sha is not None
    assert workflow_ref is not None
    assert workflow_path is not None
    assert workflow_sha256 is not None
    assert verifier_sha256 is not None
    assert artifact_verifier_sha256 is not None
    return {
        "provider": "github-actions",
        "run": {
            "id": run_id,
            "attempt": run_attempt,
        },
        "source": {
            "head_sha": head_sha,
            "ref": workflow_ref,
        },
        "workflow": {
            "path": str(workflow_path),
            "sha256": workflow_sha256,
        },
        "verifiers": {
            "verify_signed_candidate.py": {
                "sha256": verifier_sha256,
            },
            "release_artifact_verifier.py": {
                "sha256": artifact_verifier_sha256,
            },
        },
    }


def _validate_apple_profile_bindings(
    path: Path,
    verification: SignedCandidateVerification,
    failures: list[str],
) -> dict[str, object] | None:
    owner = "signed candidate Apple profile provenance"
    if path.is_symlink() or not path.is_file():
        failures.append(f"{owner}: binding input is not a regular file")
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        failures.append(f"{owner}: cannot read binding JSON ({type(error).__name__})")
        return None
    if not isinstance(payload, dict) or set(payload) != {"schema_version", "profiles"}:
        failures.append(f"{owner}: root contract is not exact")
        return None
    if payload.get("schema_version") != 1:
        failures.append(f"{owner}: schema_version must be 1")
    profiles = payload.get("profiles")
    if not isinstance(profiles, dict) or set(profiles) != set(EXPECTED_APPLE_PROFILES):
        failures.append(f"{owner}: profile role inventory is not exact")
        return None

    validated: dict[str, dict[str, str]] = {}
    for role, expected_bundle_id in EXPECTED_APPLE_PROFILES.items():
        profile = profiles.get(role)
        expected_name = f"iOS Team Store Provisioning Profile: {expected_bundle_id}"
        if not isinstance(profile, dict) or set(profile) != {
            "bundle_id",
            "name",
            "sha256",
            "uuid",
        }:
            failures.append(f"{owner}: {role} binding contract is not exact")
            continue
        bundle_id = profile.get("bundle_id")
        name = profile.get("name")
        profile_sha256 = profile.get("sha256")
        profile_uuid = profile.get("uuid")
        if bundle_id != expected_bundle_id:
            failures.append(f"{owner}: {role} bundle identifier differs")
        if name != expected_name:
            failures.append(f"{owner}: {role} profile name differs")
        if not isinstance(profile_sha256, str) or SHA256_PATTERN.fullmatch(
            profile_sha256
        ) is None:
            failures.append(f"{owner}: {role} profile SHA-256 is invalid")
        if not isinstance(profile_uuid, str) or PROFILE_UUID_PATTERN.fullmatch(
            profile_uuid
        ) is None:
            failures.append(f"{owner}: {role} profile UUID is invalid")
        if (
            bundle_id == expected_bundle_id
            and name == expected_name
            and isinstance(profile_sha256, str)
            and SHA256_PATTERN.fullmatch(profile_sha256) is not None
            and isinstance(profile_uuid, str)
            and PROFILE_UUID_PATTERN.fullmatch(profile_uuid) is not None
        ):
            validated[role] = {
                "bundle_id": bundle_id,
                "name": name,
                "sha256": profile_sha256,
                "uuid": profile_uuid,
            }

    apple_result = verification.artifacts.get("apple")
    details = apple_result.details if apple_result is not None else {}
    for collection_name in ("products", "archive_products"):
        collection = details.get(collection_name)
        if not isinstance(collection, list):
            failures.append(f"{owner}: verified Apple {collection_name} are missing")
            continue
        actual_by_role = {
            item.get("role"): item
            for item in collection
            if isinstance(item, dict) and isinstance(item.get("role"), str)
        }
        if set(actual_by_role) != set(EXPECTED_APPLE_PROFILES):
            failures.append(
                f"{owner}: verified Apple {collection_name} role inventory is not exact"
            )
            continue
        for role, expected in validated.items():
            actual_product = actual_by_role[role]
            actual_profile = actual_product.get("provisioning_profile")
            if not isinstance(actual_profile, dict):
                failures.append(
                    f"{owner}: {collection_name} {role} profile details are missing"
                )
                continue
            actual_binding = {
                "bundle_id": actual_product.get("bundle_id"),
                "name": actual_profile.get("name"),
                "sha256": actual_profile.get("sha256"),
                "uuid": actual_profile.get("uuid"),
            }
            if actual_binding != expected:
                failures.append(
                    f"{owner}: {collection_name} {role} profile differs from "
                    "the protected input binding"
                )

    if failures:
        return None
    return {
        "schema_version": 1,
        "profiles": validated,
    }


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
    provenance: dict[str, object] | None,
    apple_profile_bindings: dict[str, object] | None,
) -> dict[str, object]:
    results = verification.artifacts
    summary = verification_summary(results)
    return {
        **summary,
        "schema_version": 3,
        "release": manifest.get("release"),
        "source_revision": manifest.get("source_revision"),
        "state": (
            "candidate-bytes-verified-not-manifest-promoted"
            if (
                verification.byte_verified
                and package is not None
                and provenance is not None
                and apple_profile_bindings is not None
                and set(results) == EXPECTED_ARTIFACT_IDS
                and all(result.byte_verified for result in results.values())
            )
            else "candidate-verification-failed"
        ),
        "candidate_set": verification.candidate_set,
        "package": package,
        "provenance": provenance,
        "signing_provenance": {
            "apple_profiles": apple_profile_bindings,
        },
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
    provenance = _validate_provenance(arguments, failures)
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
    apple_profile_bindings = _validate_apple_profile_bindings(
        arguments.apple_profile_bindings.resolve(),
        verification,
        failures,
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
    receipt = _build_receipt(
        manifest,
        verification,
        package,
        provenance,
        apple_profile_bindings,
    )
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
