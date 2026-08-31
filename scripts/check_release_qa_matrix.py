#!/usr/bin/env python3
"""Fail closed when the human release QA matrix drifts from current authority."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.release_artifact_verifier import (
        VerificationResult,
        evidence_contains_digest,
        validate_manifest_artifact_contract,
        verify_manifest_artifacts,
    )
except ModuleNotFoundError:
    from release_artifact_verifier import (  # type: ignore[no-redef]
        VerificationResult,
        evidence_contains_digest,
        validate_manifest_artifact_contract,
        verify_manifest_artifacts,
    )


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = Path("docs/QA_MATRIX.md")
AUTHORITY_DOCUMENTS = (
    Path("growth/README.md"),
    Path("docs/GROWTH_RELEASE.md"),
    DOCUMENT,
    Path("docs/RELEASE.md"),
)
UPLOAD_MANIFEST = Path("store/upload-manifest-1.1.0.json")
QUALITY_GATES = Path("growth/quality/gates.json")
CURRENT_BLOCK_START = "<!-- release-qa-current:start -->"
CURRENT_BLOCK_END = "<!-- release-qa-current:end -->"
AUTHORITY_BLOCK_START = "<!-- release-authority-current:start -->"
AUTHORITY_BLOCK_END = "<!-- release-authority-current:end -->"
HISTORICAL_HEADING = "## Historical evidence — non-transferable"
VALID_SOURCE_SYNC = {"blocked", "verified-current"}
VALID_GATE_STATUS = {"blocked", "pending", "unknown", "fail", "pass"}
RELEASE_GATE = "release_artifact_source_sync"
SHA256_PATTERN = re.compile(r"[0-9a-fA-F]{64}\Z")
REVISION_PATTERN = re.compile(r"[0-9a-f]{40}\Z")

# These paths define the product/build inputs covered by exact-source release
# evidence. Evidence, reports, and store manifests intentionally live outside
# this list so a documentation-only evidence commit does not invalidate the
# product revision it records.
RELEASE_SOURCE_PATHS = (
    "androidSurfaceContract",
    "app",
    "shared",
    "wearApp",
    "iosApp",
    "build.gradle.kts",
    "settings.gradle.kts",
    "gradle.properties",
    "gradle",
    "gradlew",
    "gradlew.bat",
)

# `git ls-files --others` intentionally omits no standard excludes, so locally
# ignored product source is visible too. Only deterministic build products and
# user-local Xcode state are excluded from the broad module roots.
RELEASE_GENERATED_PATHS = (
    ":(exclude)androidSurfaceContract/build/**",
    ":(exclude)app/build/**",
    ":(exclude)shared/build/**",
    ":(exclude)wearApp/build/**",
    ":(exclude)iosApp/build/**",
    ":(exclude)**/.cxx/**",
    ":(exclude)**/.externalNativeBuild/**",
    ":(exclude)**/.DS_Store",
    ":(exclude)iosApp/**/xcuserdata/**",
    ":(exclude)iosApp/**/DerivedData/**",
)

SURFACES = (
    {
        "artifact": "android_phone",
        "label": "Android phone/tablet",
        "build_file": "app/build.gradle.kts",
        "identity_field": "version_code",
        "physical_gate": "android_physical_smoke",
    },
    {
        "artifact": "wear_os",
        "label": "Wear OS",
        "build_file": "wearApp/build.gradle.kts",
        "identity_field": "version_code",
        "physical_gate": "android_physical_smoke",
    },
    {
        "artifact": "apple",
        "label": "Apple app/widget/watch",
        "build_file": "iosApp/project.yml",
        "identity_field": "build",
        "physical_gate": "ios_physical_smoke",
    },
)


def _load_json_object(path: Path, label: str, failures: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        failures.append(f"{label}: cannot read JSON: {error}")
        return {}
    if not isinstance(payload, dict):
        failures.append(f"{label}: root must be a JSON object")
        return {}
    return payload


def _single_match(
    text: str,
    pattern: str,
    label: str,
    failures: list[str],
) -> str | None:
    matches = {match.replace("_", "") for match in re.findall(pattern, text)}
    if len(matches) != 1:
        failures.append(f"{label}: expected one unambiguous value, found {sorted(matches)}")
        return None
    return next(iter(matches))


def _build_identities(root: Path, failures: list[str]) -> dict[str, tuple[str, int]]:
    sources: dict[str, str] = {}
    for relative in (
        "app/build.gradle.kts",
        "wearApp/build.gradle.kts",
        "iosApp/project.yml",
    ):
        try:
            sources[relative] = (root / relative).read_text(encoding="utf-8")
        except OSError as error:
            failures.append(f"{relative}: cannot read build identity: {error}")

    if len(sources) != 3:
        return {}

    phone_name = _single_match(
        sources["app/build.gradle.kts"],
        r'versionName\s*=\s*"([^"]+)"',
        "Android phone versionName",
        failures,
    )
    phone_code = _single_match(
        sources["app/build.gradle.kts"],
        r"versionCode\s*=\s*([\d_]+)",
        "Android phone versionCode",
        failures,
    )
    wear_name = _single_match(
        sources["wearApp/build.gradle.kts"],
        r'versionName\s*=\s*"([^"]+)"',
        "Wear OS versionName",
        failures,
    )
    wear_code = _single_match(
        sources["wearApp/build.gradle.kts"],
        r"versionCode\s*=\s*([\d_]+)",
        "Wear OS versionCode",
        failures,
    )
    apple_name = _single_match(
        sources["iosApp/project.yml"],
        r"(?m)^\s*MARKETING_VERSION:\s*([^\s]+)\s*$",
        "Apple MARKETING_VERSION",
        failures,
    )
    apple_build = _single_match(
        sources["iosApp/project.yml"],
        r"(?m)^\s*CURRENT_PROJECT_VERSION:\s*([\d_]+)\s*$",
        "Apple CURRENT_PROJECT_VERSION",
        failures,
    )
    values = (phone_name, phone_code, wear_name, wear_code, apple_name, apple_build)
    if any(value is None for value in values):
        return {}
    assert phone_name and phone_code and wear_name and wear_code and apple_name and apple_build
    return {
        "android_phone": (phone_name, int(phone_code)),
        "wear_os": (wear_name, int(wear_code)),
        "apple": (apple_name, int(apple_build)),
    }


def _gate_status(
    gates: dict[str, Any],
    gate_id: str,
    failures: list[str],
) -> str | None:
    gate = gates.get(gate_id)
    if not isinstance(gate, dict):
        failures.append(f"quality gates: missing object {gate_id}")
        return None
    status = gate.get("status")
    if status not in VALID_GATE_STATUS:
        failures.append(f"quality gates: {gate_id} has invalid status {status!r}")
        return None
    if gate.get("blocks_publication") is not True:
        failures.append(f"quality gates: {gate_id} must block publication")
    reason = gate.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        failures.append(f"quality gates: {gate_id} needs a non-empty reason")
    return str(status)


def _run_git(root: Path, arguments: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=root,
        capture_output=True,
        check=False,
        text=True,
        timeout=15,
    )


def _validate_source_revision(
    root: Path,
    manifest: dict[str, Any],
    gates: dict[str, Any],
    failures: list[str],
) -> None:
    revision = manifest.get("source_revision")
    if not isinstance(revision, str) or REVISION_PATTERN.fullmatch(revision) is None:
        failures.append(
            "upload manifest: source_revision must be a full lowercase 40-hex commit"
        )
        return

    release_gate = gates.get(RELEASE_GATE)
    gate_revision = (
        release_gate.get("source_revision")
        if isinstance(release_gate, dict)
        else None
    )
    if gate_revision != revision:
        failures.append(
            "quality gates: release_artifact_source_sync source_revision "
            f"{gate_revision!r} differs from upload manifest {revision!r}"
        )

    try:
        object_type = _run_git(root, ["cat-file", "-t", revision])
        diff = _run_git(
            root,
            [
                "diff",
                "--quiet",
                "--no-ext-diff",
                revision,
                "--",
                *RELEASE_SOURCE_PATHS,
            ],
        )
        changed = (
            _run_git(
                root,
                [
                    "diff",
                    "--name-only",
                    "--no-ext-diff",
                    revision,
                    "--",
                    *RELEASE_SOURCE_PATHS,
                ],
            )
            if diff.returncode == 1
            else None
        )
        untracked = _run_git(
            root,
            [
                "ls-files",
                "--others",
                "--",
                *RELEASE_SOURCE_PATHS,
                *RELEASE_GENERATED_PATHS,
            ],
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        failures.append(f"upload manifest: cannot verify source_revision: {error}")
        return

    if object_type.returncode != 0:
        detail = object_type.stderr.strip() or "object does not exist"
        failures.append(
            f"upload manifest: source_revision {revision} is not a commit: {detail}"
        )
        return
    resolved_type = object_type.stdout.strip()
    if resolved_type != "commit":
        failures.append(
            f"upload manifest: source_revision {revision} must identify a commit "
            f"object, got {resolved_type or 'unknown'}"
        )
        return

    if diff.returncode == 1:
        assert changed is not None
        if changed.returncode != 0:
            detail = changed.stderr.strip() or f"git diff exited {changed.returncode}"
            failures.append(
                f"upload manifest: cannot inspect stale source_revision: {detail}"
            )
            return
        paths = [line for line in changed.stdout.splitlines() if line]
        detail = ", ".join(paths[:8]) or "release source paths changed"
        if len(paths) > 8:
            detail += f", and {len(paths) - 8} more"
        failures.append(
            f"upload manifest: source_revision {revision} is stale for release source: {detail}"
        )
    elif diff.returncode != 0:
        detail = diff.stderr.strip() or f"git diff exited {diff.returncode}"
        failures.append(
            f"upload manifest: cannot verify source_revision {revision}: {detail}"
        )
        return

    if untracked.returncode != 0:
        detail = untracked.stderr.strip() or f"git ls-files exited {untracked.returncode}"
        failures.append(
            f"upload manifest: cannot inspect untracked release source: {detail}"
        )
        return
    untracked_paths = sorted({line for line in untracked.stdout.splitlines() if line})
    if untracked_paths:
        detail = ", ".join(untracked_paths[:8])
        if len(untracked_paths) > 8:
            detail += f", and {len(untracked_paths) - 8} more"
        failures.append(
            "upload manifest: untracked release source prevents exact-source proof: "
            f"{detail}"
        )


def _existing_repository_file(
    root: Path,
    value: object,
    label: str,
    failures: list[str],
) -> bool:
    if not isinstance(value, str) or not value.strip():
        failures.append(f"{label} must be an existing repository-relative file path")
        return False
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        failures.append(f"{label} must be an existing repository-relative file path")
        return False
    repository = root.resolve()
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(repository)
    except ValueError:
        failures.append(f"{label} resolves outside the repository: {value}")
        return False
    if not candidate.is_file():
        failures.append(f"{label} is missing: {value}")
        return False
    return True


def _historical_identity(
    artifact: dict[str, Any],
    field: str,
    release: object,
) -> str | None:
    historical = artifact.get("historical_candidate")
    if not isinstance(historical, dict):
        return None
    version = historical.get("version", release)
    identity = historical.get(field)
    if not isinstance(version, str) or not version or isinstance(identity, bool):
        return None
    if not isinstance(identity, int):
        return None
    return f"`{version} ({identity})`"


def _current_physical_evidence_boundary(
    root: Path,
    artifact_id: str,
    artifact: dict[str, Any],
    failures: list[str],
) -> str:
    evidence = artifact.get("physical_qa_evidence")
    if evidence is None:
        return "none"
    if _existing_repository_file(
        root,
        evidence,
        f"{artifact_id}: physical_qa_evidence",
        failures,
    ):
        assert isinstance(evidence, str)
        return evidence
    return "invalid"


def _expected_blocks(
    root: Path,
) -> tuple[str | None, str | None, list[str], list[str]]:
    """Return QA table, authority block, failures, and historical identities."""

    failures: list[str] = []
    manifest = _load_json_object(root / UPLOAD_MANIFEST, "upload manifest", failures)
    gate_payload = _load_json_object(root / QUALITY_GATES, "quality gates", failures)
    identities = _build_identities(root, failures)

    release = manifest.get("release")
    revision = manifest.get("source_revision")
    if not isinstance(release, str) or not release:
        failures.append("upload manifest: release must be a non-empty string")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        failures.append("upload manifest: artifacts must be an object")
        artifacts = {}
    gates = gate_payload.get("gates")
    if not isinstance(gates, dict):
        failures.append("quality gates: gates must be an object")
        gates = {}

    _validate_source_revision(root, manifest, gates, failures)
    artifact_verifications = verify_manifest_artifacts(root, manifest, failures)

    release_gate_status = _gate_status(gates, RELEASE_GATE, failures)
    physical_gate_statuses = {
        gate_id: _gate_status(gates, gate_id, failures)
        for gate_id in {surface["physical_gate"] for surface in SURFACES}
    }
    physical_gate_reason_digests: dict[str, str] = {}
    for gate_id in ("android_physical_smoke", "ios_physical_smoke"):
        gate = gates.get(gate_id)
        reason = gate.get("reason") if isinstance(gate, dict) else None
        if isinstance(reason, str) and reason.strip():
            physical_gate_reason_digests[gate_id] = hashlib.sha256(
                reason.encode("utf-8")
            ).hexdigest()

    rows: list[str] = []
    authority_artifact_rows: list[str] = []
    historical_identities: list[str] = []
    for surface in SURFACES:
        artifact_id = surface["artifact"]
        artifact = artifacts.get(artifact_id)
        if not isinstance(artifact, dict):
            failures.append(f"upload manifest: missing artifact object {artifact_id}")
            continue
        identity = identities.get(artifact_id)
        if identity is None:
            continue
        version_name, build_number = identity
        if release != version_name:
            failures.append(
                f"{artifact_id}: build version {version_name} differs from manifest release {release!r}"
            )
        field = surface["identity_field"]
        declared_identity = artifact.get(field)
        if declared_identity != build_number:
            failures.append(
                f"{artifact_id}: manifest {field} {declared_identity!r} differs from build {build_number}"
            )

        source_sync = artifact.get("source_sync")
        if source_sync not in VALID_SOURCE_SYNC:
            failures.append(f"{artifact_id}: invalid source_sync {source_sync!r}")
            continue
        physical_evidence = _current_physical_evidence_boundary(
            root,
            artifact_id,
            artifact,
            failures,
        )
        verification = artifact_verifications.get(
            artifact_id,
            VerificationResult(
                artifact_id=artifact_id,
                source_sync=str(source_sync),
                byte_verified=False,
            ),
        )
        authority_artifact_rows.append(
            f"<!-- artifact:{artifact_id};source_sync={source_sync};"
            f"byte_verified={str(verification.byte_verified).lower()};"
            f"physical_qa_evidence={physical_evidence} -->"
        )
        evidence_contains_digest(
            root,
            artifact.get("source_sync_evidence"),
            revision,
            f"{artifact_id}: source_sync_evidence",
            failures,
            binding="the manifest source_revision",
        )

        historical_identity = _historical_identity(artifact, field, release)
        if source_sync == "blocked":
            if historical_identity is None:
                failures.append(f"{artifact_id}: historical candidate identity is missing")
            else:
                historical_identities.append(historical_identity)
        elif artifact.get("historical_candidate") is not None:
            failures.append(
                f"{artifact_id}: verified-current artifact cannot carry a historical candidate"
            )

        physical_gate = surface["physical_gate"]
        physical_status = physical_gate_statuses.get(physical_gate)
        if release_gate_status is None or physical_status is None:
            continue
        ready_authority = (
            source_sync == "verified-current"
            and verification.byte_verified
            and release_gate_status == "pass"
            and physical_status == "pass"
        )
        evidence_ready = True
        if ready_authority:
            sha256 = artifact.get("sha256")
            if not isinstance(sha256, str) or SHA256_PATTERN.fullmatch(sha256) is None:
                failures.append(
                    f"{artifact_id}: READY requires sha256 to be 64 hexadecimal characters"
                )
                evidence_ready = False
            evidence_ready = (
                evidence_contains_digest(
                    root,
                    artifact.get("signing_evidence"),
                    sha256,
                    f"{artifact_id}: READY signing_evidence",
                    failures,
                )
                and evidence_ready
            )
            evidence_ready = (
                evidence_contains_digest(
                    root,
                    artifact.get("physical_qa_evidence"),
                    sha256,
                    f"{artifact_id}: READY physical_qa_evidence",
                    failures,
                )
                and evidence_ready
            )
        ready = ready_authority and evidence_ready
        status = "READY" if ready else "BLOCKED"
        rows.append(
            f"| {surface['label']} | `{version_name} ({build_number})` | "
            f"`{source_sync}` | `{str(verification.byte_verified).lower()}` | "
            f"`{RELEASE_GATE}: {release_gate_status}` | "
            f"`{physical_gate}: {physical_status}` | **{status}** |"
        )

    if release_gate_status == "pass":
        unverified = [
            artifact_id
            for artifact_id in ("android_phone", "wear_os", "apple")
            if not artifact_verifications.get(
                artifact_id,
                VerificationResult(artifact_id, "missing", False),
            ).byte_verified
        ]
        if unverified:
            failures.append(
                "quality gates: release_artifact_source_sync cannot pass without "
                "byte-verified artifacts: " + ", ".join(unverified)
            )

    if failures or not isinstance(revision, str):
        return None, None, failures, historical_identities
    block = "\n".join(
        (
            CURRENT_BLOCK_START,
            "| Surface | Exact candidate | Manifest source sync | Manifest entry reverified/current | Release/source gate | Required physical QA | Fail-closed status |",
            "| --- | --- | --- | --- | --- | --- | --- |",
            *rows,
            CURRENT_BLOCK_END,
        )
    )
    authority_block = "\n".join(
        (
            AUTHORITY_BLOCK_START,
            f"<!-- source_revision:{revision} -->",
            *authority_artifact_rows,
            *(
                f"<!-- physical_gate:{gate_id}={physical_gate_statuses[gate_id]};"
                f"reason_sha256={physical_gate_reason_digests[gate_id]} -->"
                for gate_id in ("android_physical_smoke", "ios_physical_smoke")
            ),
            AUTHORITY_BLOCK_END,
        )
    )
    return block, authority_block, failures, historical_identities


def expected_current_block(
    root: Path = ROOT,
) -> tuple[str | None, list[str], list[str]]:
    """Return authoritative QA Markdown, failures, and historical identities."""

    block, _, failures, historical_identities = _expected_blocks(root)
    return block, failures, historical_identities


def expected_authority_block(
    root: Path = ROOT,
) -> tuple[str | None, list[str]]:
    """Return the narrative authority block derived from manifest and gates."""

    _, authority_block, failures, _ = _expected_blocks(root)
    return authority_block, failures


def _extract_document_block(
    document: str,
    start_marker: str,
    end_marker: str,
    label: str,
    failures: list[str],
) -> str | None:
    if document.count(start_marker) != 1 or document.count(end_marker) != 1:
        failures.append(f"{label}: block markers must each appear once")
        return None
    start = document.index(start_marker)
    end = document.index(end_marker, start) + len(end_marker)
    return document[start:end]


def validate_contract_only(root: Path = ROOT) -> list[str]:
    """Validate public contract state without inspecting or claiming bytes.

    The byte-verification values already committed by the protected full
    verifier are treated as opaque text.  This path only preserves that block
    while checking its public source, manifest, evidence, and gate bindings.
    It can neither produce a new byte claim nor declare a surface READY.
    """

    failures: list[str] = []
    manifest = _load_json_object(root / UPLOAD_MANIFEST, "upload manifest", failures)
    gate_payload = _load_json_object(root / QUALITY_GATES, "quality gates", failures)
    gates = gate_payload.get("gates")
    if not isinstance(gates, dict):
        failures.append("quality gates: gates must be an object")
        gates = {}

    validate_manifest_artifact_contract(root, manifest, failures)
    _validate_source_revision(root, manifest, gates, failures)
    physical_gate_statuses = {
        gate_id: _gate_status(gates, gate_id, failures)
        for gate_id in ("android_physical_smoke", "ios_physical_smoke")
    }
    _gate_status(gates, RELEASE_GATE, failures)

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        artifacts = {}
    revision = manifest.get("source_revision")

    documents: dict[Path, str] = {}
    authority_blocks: dict[Path, str] = {}
    for relative in AUTHORITY_DOCUMENTS:
        try:
            document = (root / relative).read_text(encoding="utf-8")
        except OSError as error:
            failures.append(f"{relative}: cannot read: {error}")
            continue
        documents[relative] = document
        block = _extract_document_block(
            document,
            AUTHORITY_BLOCK_START,
            AUTHORITY_BLOCK_END,
            f"{relative}: current authority",
            failures,
        )
        if block is not None:
            authority_blocks[relative] = block

    unique_blocks = set(authority_blocks.values())
    if len(unique_blocks) > 1:
        failures.append(
            "release authority: committed authority block differs across documents"
        )
    canonical = next(iter(unique_blocks), None)
    if canonical is not None and isinstance(revision, str):
        lines = canonical.splitlines()
        byte_markers: dict[str, str] = {}
        marker_pattern = re.compile(
            r"<!-- artifact:(android_phone|wear_os|apple);"
            r"source_sync=(blocked|verified-current);"
            r"byte_verified=(true|false);"
            r"physical_qa_evidence=([^;<>]+) -->\Z"
        )
        for line in lines:
            match = marker_pattern.fullmatch(line)
            if match is not None:
                byte_markers[match.group(1)] = match.group(3)
        if set(byte_markers) != {"android_phone", "wear_os", "apple"}:
            failures.append(
                "release authority: committed block must preserve exactly one "
                "opaque byte marker per artifact"
            )
        else:
            expected_lines = [
                AUTHORITY_BLOCK_START,
                f"<!-- source_revision:{revision} -->",
            ]
            for artifact_id in ("android_phone", "wear_os", "apple"):
                artifact = artifacts.get(artifact_id)
                if not isinstance(artifact, dict):
                    continue
                physical = _current_physical_evidence_boundary(
                    root,
                    artifact_id,
                    artifact,
                    failures,
                )
                expected_lines.append(
                    f"<!-- artifact:{artifact_id};"
                    f"source_sync={artifact.get('source_sync')};"
                    f"byte_verified={byte_markers[artifact_id]};"
                    f"physical_qa_evidence={physical} -->"
                )
            for gate_id in ("android_physical_smoke", "ios_physical_smoke"):
                gate = gates.get(gate_id)
                reason = gate.get("reason") if isinstance(gate, dict) else None
                reason_digest = (
                    hashlib.sha256(reason.encode("utf-8")).hexdigest()
                    if isinstance(reason, str) and reason.strip()
                    else ""
                )
                expected_lines.append(
                    f"<!-- physical_gate:{gate_id}="
                    f"{physical_gate_statuses.get(gate_id)};"
                    f"reason_sha256={reason_digest} -->"
                )
            expected_lines.append(AUTHORITY_BLOCK_END)
            if canonical != "\n".join(expected_lines):
                failures.append(
                    "release authority: committed block public fields differ "
                    "from manifest/gates"
                )

    qa_document = documents.get(DOCUMENT)
    if qa_document is not None:
        _extract_document_block(
            qa_document,
            CURRENT_BLOCK_START,
            CURRENT_BLOCK_END,
            f"{DOCUMENT}: exact-current",
            failures,
        )
        if qa_document.count(HISTORICAL_HEADING) != 1:
            failures.append(
                f"{DOCUMENT}: historical non-transferable heading must appear once"
            )
    return failures


def validate(root: Path = ROOT) -> list[str]:
    expected, authority_block, failures, historical_identities = _expected_blocks(root)
    if expected is None or authority_block is None:
        return failures

    documents: dict[Path, str] = {}
    for relative in AUTHORITY_DOCUMENTS:
        try:
            documents[relative] = (root / relative).read_text(encoding="utf-8")
        except OSError as error:
            failures.append(f"{relative}: cannot read: {error}")

    for relative, document in documents.items():
        if (
            document.count(AUTHORITY_BLOCK_START) != 1
            or document.count(AUTHORITY_BLOCK_END) != 1
        ):
            failures.append(
                f"{relative}: current authority block markers must each appear once"
            )
            continue
        start = document.index(AUTHORITY_BLOCK_START)
        end = document.index(AUTHORITY_BLOCK_END, start) + len(AUTHORITY_BLOCK_END)
        if document[start:end] != authority_block:
            failures.append(
                f"{relative}: current authority block differs from upload manifest/gates"
            )

    document = documents.get(DOCUMENT)
    if document is None:
        return failures

    if document.count(CURRENT_BLOCK_START) != 1 or document.count(CURRENT_BLOCK_END) != 1:
        failures.append(f"{DOCUMENT}: exact-current block markers must each appear once")
    else:
        start = document.index(CURRENT_BLOCK_START)
        end = document.index(CURRENT_BLOCK_END, start) + len(CURRENT_BLOCK_END)
        actual = document[start:end]
        if actual != expected:
            failures.append(
                f"{DOCUMENT}: exact-current block differs from build/manifest/gate authority"
            )

    if document.count(HISTORICAL_HEADING) != 1:
        failures.append(f"{DOCUMENT}: historical non-transferable heading must appear once")
    else:
        historical = document.split(HISTORICAL_HEADING, 1)[1]
        for identity in historical_identities:
            if identity not in historical:
                failures.append(
                    f"{DOCUMENT}: historical section is missing manifest identity {identity}"
                )
        if "cannot" not in historical.lower() or "exact-current" not in historical:
            failures.append(
                f"{DOCUMENT}: historical section must state that evidence cannot satisfy exact-current QA"
            )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Nimbo release QA authority matrix."
    )
    parser.add_argument(
        "--contract-only",
        action="store_true",
        help=(
            "Validate only public manifest/evidence bindings and preserve the "
            "existing committed byte authority block"
        ),
    )
    arguments = parser.parse_args()
    failures = validate_contract_only() if arguments.contract_only else validate()
    if failures:
        for failure in failures:
            label = "contract check" if arguments.contract_only else "check"
            print(f"release QA matrix {label} failed: {failure}", file=sys.stderr)
        return 1
    if arguments.contract_only:
        print(
            "Release QA matrix contract check passed: existing byte authority "
            "was preserved but not reverified."
        )
    else:
        print("Release QA matrix check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
