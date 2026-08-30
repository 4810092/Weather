#!/usr/bin/env python3
"""Verify release-candidate bytes before any surface can become READY.

The upload manifest intentionally contains no private or machine-local paths.
When an artifact is marked ``verified-current``, callers must provide the
external artifact directory through ``NIMBO_RELEASE_ARTIFACT_ROOT`` (or the
explicit ``artifact_root`` argument).  The verifier then re-opens the actual
AAB/IPA bytes, recomputes their digest, and checks platform identity and
signing.  A Markdown report or a machine-readable receipt is never accepted as
a substitute for the artifact bytes.
"""

from __future__ import annotations

import hashlib
import json
import os
import plistlib
import re
import shutil
import stat
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Sequence
from xml.etree import ElementTree


ANDROID_NAMESPACE = "http://schemas.android.com/apk/res/android"
ANDROID_PACKAGE_ID = "uz.ganikhodjaev.weather"
ANDROID_UPLOAD_CERTIFICATE_SHA256 = (
    "431548a4871c9c090eee808ac3a34898f5d78602d9e747dfe81e228415aac252"
)
APPLE_TEAM_ID = "5SWEZ7HTYP"
APPLE_DISTRIBUTION_CERTIFICATE_SHA256 = (
    "fd4d8668a7e0f4eb9f64a12b5f0ddec0075ccde31dad50a96e978926e0e743f1"
)
BUNDLETOOL_VERSION = "1.18.3"
BUNDLETOOL_SHA256 = (
    "a099cfa1543f55593bc2ed16a70a7c67fe54b1747bb7301f37fdfd6d91028e29"
)
ARTIFACT_ROOT_ENV = "NIMBO_RELEASE_ARTIFACT_ROOT"
BUNDLETOOL_ENV = "NIMBO_BUNDLETOOL_JAR"
APPLE_CODESIGN = Path("/usr/bin/codesign")
APPLE_SECURITY = Path("/usr/bin/security")
APPLE_XCRUN = Path("/usr/bin/xcrun")
SYSTEM_OPENSSL = Path("/usr/bin/openssl")
SYSTEM_JAVA = Path("/usr/bin/java")
SYSTEM_JARSIGNER = Path("/usr/bin/jarsigner")
SYSTEM_KEYTOOL = Path("/usr/bin/keytool")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
REVISION_PATTERN = re.compile(r"[0-9a-f]{40}\Z")

# Product/build inputs whose checked-out content must match the manifest source
# revision before any artifact bytes can be called current. Evidence and store
# documents intentionally remain outside this list so a later evidence-only
# commit does not invalidate an already built candidate.
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

EXPECTED_POLICY = {
    "artifact_root_env": ARTIFACT_ROOT_ENV,
    "bundletool_jar_env": BUNDLETOOL_ENV,
    "bundletool_version": BUNDLETOOL_VERSION,
    "bundletool_sha256": BUNDLETOOL_SHA256,
    "android_package_id": ANDROID_PACKAGE_ID,
    "android_upload_certificate_sha256": ANDROID_UPLOAD_CERTIFICATE_SHA256,
    "apple_team_id": APPLE_TEAM_ID,
    "apple_distribution_certificate_sha256": (
        APPLE_DISTRIBUTION_CERTIFICATE_SHA256
    ),
    "apple_archive_relative_path": "Nimbo.xcarchive",
    "apple_export_options_relative_path": "ExportOptions.plist",
    "apple_source_revision_info_key": "NimboSourceRevision",
}

APPLE_PRODUCTS = (
    {
        "role": "app",
        "relative_path": Path("."),
        "bundle_id": ANDROID_PACKAGE_ID,
        "executable": "Nimbo",
        "dsym": "Nimbo.app.dSYM",
        "app_group": True,
        "minimum_os": "15.0",
        "platform": "iphoneos",
        "architectures": {"arm64"},
        "supported_platform": "iPhoneOS",
        "device_families": {1, 2},
    },
    {
        "role": "widget",
        "relative_path": Path("PlugIns/NimboWidget.appex"),
        "bundle_id": f"{ANDROID_PACKAGE_ID}.widget",
        "executable": "NimboWidget",
        "dsym": "NimboWidget.appex.dSYM",
        "app_group": True,
        "minimum_os": "15.0",
        "platform": "iphoneos",
        "architectures": {"arm64"},
        "supported_platform": "iPhoneOS",
        "device_families": {1, 2},
    },
    {
        "role": "watch",
        "relative_path": Path("Watch/NimboWatch.app"),
        "bundle_id": f"{ANDROID_PACKAGE_ID}.watchkitapp",
        "executable": "NimboWatch",
        "dsym": "NimboWatch.app.dSYM",
        "app_group": False,
        "minimum_os": "10.0",
        "platform": "watchos",
        "architectures": {"arm64", "arm64_32"},
        "supported_platform": "WatchOS",
        "device_families": {4},
    },
)


@dataclass(frozen=True)
class VerificationResult:
    artifact_id: str
    source_sync: str
    byte_verified: bool
    sha256: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CandidateTreeSnapshot:
    tree_sha256: str
    observation_sha256: str
    top_level_entries: tuple[str, ...]
    file_count: int
    directory_count: int
    total_bytes: int

    def receipt(self) -> dict[str, Any]:
        return {
            "tree_sha256": self.tree_sha256,
            "top_level_entries": list(self.top_level_entries),
            "file_count": self.file_count,
            "directory_count": self.directory_count,
            "total_bytes": self.total_bytes,
        }


@dataclass(frozen=True)
class SignedCandidateVerification:
    artifacts: dict[str, VerificationResult]
    candidate_set: dict[str, Any]
    byte_verified: bool
    source_observation_sha256: str | None = field(default=None, repr=False)


CommandRunner = Callable[..., subprocess.CompletedProcess[Any]]


def _snapshot_candidate_tree(
    root: Path,
    failures: list[str],
    owner: str,
    *,
    expected_top_level: set[str] | None = None,
) -> CandidateTreeSnapshot | None:
    """Hash one closed directory tree without following links or special nodes."""

    resolved_root = root.resolve()
    if not resolved_root.is_dir() or resolved_root.is_symlink():
        failures.append(f"{owner}: candidate root must be a real directory")
        return None
    try:
        top_level = tuple(sorted(entry.name for entry in resolved_root.iterdir()))
    except OSError as error:
        failures.append(f"{owner}: cannot enumerate candidate root: {error}")
        return None
    if expected_top_level is not None and set(top_level) != expected_top_level:
        missing = sorted(expected_top_level - set(top_level))
        unexpected = sorted(set(top_level) - expected_top_level)
        failures.append(
            f"{owner}: candidate root inventory mismatch; missing={missing}, "
            f"unexpected={unexpected}"
        )

    content_entries: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []
    file_count = 0
    directory_count = 0
    total_bytes = 0
    pending_root = True
    for current, directory_names, file_names in os.walk(
        resolved_root,
        topdown=True,
        followlinks=False,
    ):
        directory_names.sort()
        file_names.sort()
        current_path = Path(current)
        candidates = [current_path] if pending_root else []
        pending_root = False
        candidates.extend(current_path / name for name in directory_names)
        candidates.extend(current_path / name for name in file_names)
        for path in candidates:
            relative = path.relative_to(resolved_root)
            relative_text = "." if relative == Path(".") else relative.as_posix()
            try:
                before = path.lstat()
            except OSError as error:
                failures.append(f"{owner}: cannot inspect {relative_text}: {error}")
                continue
            mode = stat.S_IMODE(before.st_mode)
            if stat.S_ISLNK(before.st_mode):
                failures.append(f"{owner}: symlink is forbidden: {relative_text}")
                if path.name in directory_names:
                    directory_names.remove(path.name)
                continue
            if stat.S_ISDIR(before.st_mode):
                kind = "directory"
                digest = None
                size = 0
                directory_count += 1
            elif stat.S_ISREG(before.st_mode):
                kind = "file"
                digest = _sha256_file(path)
                try:
                    after = path.lstat()
                except OSError as error:
                    failures.append(
                        f"{owner}: cannot re-inspect {relative_text}: {error}"
                    )
                    continue
                if (
                    before.st_dev,
                    before.st_ino,
                    before.st_size,
                    before.st_mtime_ns,
                    before.st_ctime_ns,
                ) != (
                    after.st_dev,
                    after.st_ino,
                    after.st_size,
                    after.st_mtime_ns,
                    after.st_ctime_ns,
                ):
                    failures.append(
                        f"{owner}: {relative_text} changed while it was hashed"
                    )
                before = after
                size = before.st_size
                file_count += 1
                total_bytes += size
            else:
                failures.append(
                    f"{owner}: special filesystem entry is forbidden: {relative_text}"
                )
                continue
            content_entries.append(
                {
                    "path": relative_text,
                    "kind": kind,
                    "mode": 0 if relative_text == "." else mode,
                    "size": size,
                    "sha256": digest,
                }
            )
            observations.append(
                {
                    "path": relative_text,
                    "dev": before.st_dev,
                    "ino": before.st_ino,
                    "mode": before.st_mode,
                    "size": before.st_size,
                    "mtime_ns": before.st_mtime_ns,
                    "ctime_ns": before.st_ctime_ns,
                }
            )

    content_entries.sort(key=lambda entry: entry["path"])
    observations.sort(key=lambda entry: entry["path"])
    content_payload = json.dumps(
        content_entries,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    observation_payload = json.dumps(
        observations,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return CandidateTreeSnapshot(
        tree_sha256=hashlib.sha256(content_payload).hexdigest(),
        observation_sha256=hashlib.sha256(observation_payload).hexdigest(),
        top_level_entries=top_level,
        file_count=file_count,
        directory_count=directory_count,
        total_bytes=total_bytes,
    )


def _run_command(
    command: Sequence[str],
    *,
    text: bool = True,
    timeout: int = 120,
) -> subprocess.CompletedProcess[Any]:
    environment = dict(os.environ)
    for variable in (
        "JAVA_HOME",
        "CLASSPATH",
        "JAVA_TOOL_OPTIONS",
        "JDK_JAVA_OPTIONS",
        "_JAVA_OPTIONS",
    ):
        environment.pop(variable, None)
    environment.update({"LC_ALL": "C", "LANG": "C"})
    try:
        return subprocess.run(
            list(command),
            capture_output=True,
            check=False,
            text=text,
            timeout=timeout,
            env=environment,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        empty: str | bytes = "" if text else b""
        detail: str | bytes = str(error) if text else str(error).encode("utf-8")
        return subprocess.CompletedProcess(list(command), 124, empty, detail)


def _command_detail(result: subprocess.CompletedProcess[Any]) -> str:
    chunks: list[str] = []
    for value in (result.stdout, result.stderr):
        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="replace")
        if isinstance(value, str) and value.strip():
            chunks.append(value.strip())
    detail = " | ".join(chunks)
    return detail[-800:] if detail else f"exit {result.returncode}"


def _run_git(
    repository_root: Path,
    arguments: Sequence[str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=repository_root,
        capture_output=True,
        check=False,
        text=True,
        timeout=15,
        env={**os.environ, "LC_ALL": "C", "LANG": "C"},
    )


def _single_source_match(
    text: str,
    pattern: str,
    label: str,
    failures: list[str],
) -> str | None:
    matches = {match.replace("_", "") for match in re.findall(pattern, text)}
    if len(matches) != 1:
        failures.append(
            f"{label}: expected one unambiguous value, found {sorted(matches)}"
        )
        return None
    return next(iter(matches))


def _read_release_identities(
    repository_root: Path,
    failures: list[str],
) -> dict[str, tuple[str, int]]:
    sources: dict[str, str] = {}
    for relative in (
        "app/build.gradle.kts",
        "wearApp/build.gradle.kts",
        "iosApp/project.yml",
        "iosApp/Nimbo.xcodeproj/project.pbxproj",
    ):
        try:
            sources[relative] = (repository_root / relative).read_text(
                encoding="utf-8"
            )
        except OSError as error:
            failures.append(f"{relative}: cannot read build identity: {error}")
    if len(sources) != 4:
        return {}

    phone_name = _single_source_match(
        sources["app/build.gradle.kts"],
        r'versionName\s*=\s*"([^"]+)"',
        "Android phone versionName",
        failures,
    )
    phone_code = _single_source_match(
        sources["app/build.gradle.kts"],
        r"versionCode\s*=\s*([\d_]+)",
        "Android phone versionCode",
        failures,
    )
    wear_name = _single_source_match(
        sources["wearApp/build.gradle.kts"],
        r'versionName\s*=\s*"([^"]+)"',
        "Wear OS versionName",
        failures,
    )
    wear_code = _single_source_match(
        sources["wearApp/build.gradle.kts"],
        r"versionCode\s*=\s*([\d_]+)",
        "Wear OS versionCode",
        failures,
    )
    apple_name = _single_source_match(
        sources["iosApp/project.yml"],
        r"(?m)^\s*MARKETING_VERSION:\s*([^\s]+)\s*$",
        "Apple MARKETING_VERSION",
        failures,
    )
    apple_build = _single_source_match(
        sources["iosApp/project.yml"],
        r"(?m)^\s*CURRENT_PROJECT_VERSION:\s*([\d_]+)\s*$",
        "Apple CURRENT_PROJECT_VERSION",
        failures,
    )
    project_names = set(
        re.findall(
            r"MARKETING_VERSION = ([^;\s]+);",
            sources["iosApp/Nimbo.xcodeproj/project.pbxproj"],
        )
    )
    project_builds = {
        int(match)
        for match in re.findall(
            r"CURRENT_PROJECT_VERSION = (\d+);",
            sources["iosApp/Nimbo.xcodeproj/project.pbxproj"],
        )
    }
    if apple_name is not None and project_names != {apple_name}:
        failures.append(
            "Apple generated project MARKETING_VERSION differs from iosApp/project.yml"
        )
    if apple_build is not None and project_builds != {int(apple_build)}:
        failures.append(
            "Apple generated project build identity differs from iosApp/project.yml"
        )

    values = (phone_name, phone_code, wear_name, wear_code, apple_name, apple_build)
    if any(value is None for value in values):
        return {}
    assert phone_name and phone_code and wear_name and wear_code
    assert apple_name and apple_build
    return {
        "android_phone": (phone_name, int(phone_code)),
        "wear_os": (wear_name, int(wear_code)),
        "apple": (apple_name, int(apple_build)),
    }


def validate_repository_source(
    repository_root: Path,
    source_revision: object,
    failures: list[str],
) -> bool:
    """Prove the checked-out release inputs match one real Git commit."""

    failure_count = len(failures)
    repository = repository_root.resolve()
    if not isinstance(source_revision, str) or REVISION_PATTERN.fullmatch(
        source_revision
    ) is None:
        failures.append(
            "upload manifest: source_revision must be a full lowercase 40-hex commit"
        )
        return False
    try:
        top_level = _run_git(repository, ["rev-parse", "--show-toplevel"])
        object_type = _run_git(repository, ["cat-file", "-t", source_revision])
        diff = _run_git(
            repository,
            [
                "diff",
                "--quiet",
                "--no-ext-diff",
                source_revision,
                "--",
                *RELEASE_SOURCE_PATHS,
            ],
        )
        changed = (
            _run_git(
                repository,
                [
                    "diff",
                    "--name-only",
                    "--no-ext-diff",
                    source_revision,
                    "--",
                    *RELEASE_SOURCE_PATHS,
                ],
            )
            if diff.returncode == 1
            else None
        )
        untracked = _run_git(
            repository,
            [
                "ls-files",
                "--others",
                "--",
                *RELEASE_SOURCE_PATHS,
                *RELEASE_GENERATED_PATHS,
            ],
        )
        index_state = _run_git(
            repository,
            ["ls-files", "-v", "-z", "--", *RELEASE_SOURCE_PATHS],
        )
        committed_tree = _run_git(
            repository,
            [
                "ls-tree",
                "-r",
                "-z",
                "--full-tree",
                source_revision,
                "--",
                *RELEASE_SOURCE_PATHS,
            ],
        )
        current_paths = _run_git(
            repository,
            ["ls-files", "-z", "--", *RELEASE_SOURCE_PATHS],
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        failures.append(f"upload manifest: cannot verify source_revision: {error}")
        return False

    if top_level.returncode != 0:
        detail = top_level.stderr.strip() or "not a Git work tree"
        failures.append(f"upload manifest: cannot resolve repository root: {detail}")
    else:
        reported_root = Path(top_level.stdout.strip()).resolve()
        if reported_root != repository:
            failures.append(
                "upload manifest: repository_root must be the Git top level: "
                f"{reported_root}"
            )

    if object_type.returncode != 0:
        detail = object_type.stderr.strip() or "object does not exist"
        failures.append(
            f"upload manifest: source_revision {source_revision} is not a commit: "
            f"{detail}"
        )
    elif object_type.stdout.strip() != "commit":
        failures.append(
            f"upload manifest: source_revision {source_revision} must identify a "
            f"commit object, got {object_type.stdout.strip() or 'unknown'}"
        )

    if diff.returncode == 1:
        assert changed is not None
        if changed.returncode != 0:
            detail = changed.stderr.strip() or f"git diff exited {changed.returncode}"
            failures.append(
                f"upload manifest: cannot inspect stale source_revision: {detail}"
            )
        else:
            paths = [line for line in changed.stdout.splitlines() if line]
            detail = ", ".join(paths[:8]) or "release source paths changed"
            if len(paths) > 8:
                detail += f", and {len(paths) - 8} more"
            failures.append(
                f"upload manifest: source_revision {source_revision} is stale for "
                f"release source: {detail}"
            )
    elif diff.returncode != 0:
        detail = diff.stderr.strip() or f"git diff exited {diff.returncode}"
        failures.append(
            f"upload manifest: cannot verify source_revision {source_revision}: {detail}"
        )

    if untracked.returncode != 0:
        detail = untracked.stderr.strip() or f"git ls-files exited {untracked.returncode}"
        failures.append(
            f"upload manifest: cannot inspect untracked release source: {detail}"
        )
    else:
        untracked_paths = sorted(
            {line for line in untracked.stdout.splitlines() if line}
        )
        if untracked_paths:
            detail = ", ".join(untracked_paths[:8])
            if len(untracked_paths) > 8:
                detail += f", and {len(untracked_paths) - 8} more"
            failures.append(
                "upload manifest: untracked release source prevents exact-source "
                f"proof: {detail}"
            )
    if index_state.returncode != 0:
        detail = (
            index_state.stderr.strip()
            or f"git ls-files -v exited {index_state.returncode}"
        )
        failures.append(
            f"upload manifest: cannot inspect release-source index flags: {detail}"
        )
    else:
        unsafe_flags: list[str] = []
        for record in index_state.stdout.split("\0"):
            if not record:
                continue
            marker, separator, path = record.partition(" ")
            if separator != " " or marker != "H":
                unsafe_flags.append(f"{marker or '?'}:{path or record}")
        if unsafe_flags:
            detail = ", ".join(unsafe_flags[:8])
            if len(unsafe_flags) > 8:
                detail += f", and {len(unsafe_flags) - 8} more"
            failures.append(
                "upload manifest: unsafe release-source index flags prevent "
                f"exact-source proof: {detail}"
            )
    if committed_tree.returncode != 0 or current_paths.returncode != 0:
        detail = (
            committed_tree.stderr.strip()
            or current_paths.stderr.strip()
            or "cannot enumerate source tree"
        )
        failures.append(
            f"upload manifest: cannot compare release-source bytes: {detail}"
        )
    else:
        tree_entries: list[tuple[str, str, str, str]] = []
        malformed_tree = False
        for record in committed_tree.stdout.split("\0"):
            if not record:
                continue
            metadata, separator, path = record.partition("\t")
            parts = metadata.split(" ")
            if separator != "\t" or len(parts) != 3:
                malformed_tree = True
                break
            mode, object_type_name, object_id = parts
            tree_entries.append((mode, object_type_name, object_id, path))
        tracked_paths = [
            path for path in current_paths.stdout.split("\0") if path
        ]
        committed_paths = [entry[3] for entry in tree_entries]
        if malformed_tree:
            failures.append(
                "upload manifest: cannot parse committed release-source tree"
            )
        elif set(tracked_paths) != set(committed_paths):
            added = sorted(set(tracked_paths) - set(committed_paths))
            removed = sorted(set(committed_paths) - set(tracked_paths))
            failures.append(
                "upload manifest: tracked release-source path set differs from "
                f"the commit: added={added[:8]}, removed={removed[:8]}"
            )
        elif committed_paths:
            hashed = _run_git(
                repository,
                ["hash-object", "--no-filters", "--", *committed_paths],
            )
            actual_ids = [line for line in hashed.stdout.splitlines() if line]
            if hashed.returncode != 0 or len(actual_ids) != len(tree_entries):
                detail = hashed.stderr.strip() or "hash count differs"
                failures.append(
                    f"upload manifest: cannot hash actual release-source bytes: {detail}"
                )
            else:
                byte_drift: list[str] = []
                mode_drift: list[str] = []
                for (mode, object_type_name, object_id, path), actual_id in zip(
                    tree_entries,
                    actual_ids,
                    strict=True,
                ):
                    candidate = repository / path
                    if object_type_name != "blob" or mode not in {
                        "100644",
                        "100755",
                        "120000",
                    }:
                        mode_drift.append(f"{path}:{mode}/{object_type_name}")
                        continue
                    if actual_id != object_id:
                        byte_drift.append(path)
                    if mode == "120000":
                        if not candidate.is_symlink():
                            mode_drift.append(f"{path}:expected-symlink")
                    elif not candidate.is_file() or candidate.is_symlink():
                        mode_drift.append(f"{path}:expected-regular-file")
                    else:
                        executable = bool(candidate.stat().st_mode & 0o111)
                        if executable != (mode == "100755"):
                            mode_drift.append(f"{path}:mode-{mode}")
                if byte_drift:
                    detail = ", ".join(byte_drift[:8])
                    if len(byte_drift) > 8:
                        detail += f", and {len(byte_drift) - 8} more"
                    failures.append(
                        "upload manifest: actual working-tree bytes differ from "
                        f"source_revision: {detail}"
                    )
                if mode_drift:
                    detail = ", ".join(mode_drift[:8])
                    if len(mode_drift) > 8:
                        detail += f", and {len(mode_drift) - 8} more"
                    failures.append(
                        "upload manifest: actual release-source modes differ from "
                        f"source_revision: {detail}"
                    )
    return len(failures) == failure_count


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalise_fingerprint(value: str) -> str:
    return re.sub(r"[^0-9a-fA-F]", "", value).lower()


def _resolve_java_toolchain(
    owner: str,
    failures: list[str],
) -> dict[str, str] | None:
    candidates = {
        "java": SYSTEM_JAVA,
        "jarsigner": SYSTEM_JARSIGNER,
        "keytool": SYSTEM_KEYTOOL,
    }
    resolved: dict[str, str] = {}
    for tool, candidate in candidates.items():
        if not candidate.is_file() or not os.access(candidate, os.X_OK):
            failures.append(
                f"{owner}: executable system Java entry point is missing: {candidate}"
            )
            return None
        resolved[tool] = str(candidate)
    return resolved


def _required_system_tool(
    path: Path,
    owner: str,
    failures: list[str],
) -> str | None:
    if not path.is_file():
        failures.append(f"{owner}: trusted system tool is missing: {path}")
        return None
    return str(path)


def _safe_external_file(
    artifact_root: Path,
    filename: object,
    owner: str,
    failures: list[str],
) -> Path | None:
    if not isinstance(filename, str) or not filename or Path(filename).name != filename:
        failures.append(f"{owner}: filename must be one plain file name")
        return None
    resolved_root = artifact_root.expanduser().resolve()
    candidate = (resolved_root / filename).resolve()
    try:
        candidate.relative_to(resolved_root)
    except ValueError:
        failures.append(f"{owner}: artifact resolves outside artifact root")
        return None
    if not candidate.is_file():
        failures.append(f"{owner}: artifact bytes are missing: {filename}")
        return None
    return candidate


def _safe_external_directory(
    artifact_root: Path,
    relative: object,
    owner: str,
    failures: list[str],
) -> Path | None:
    if not isinstance(relative, str) or not relative or Path(relative).name != relative:
        failures.append(f"{owner}: archive path must be one relative directory name")
        return None
    resolved_root = artifact_root.expanduser().resolve()
    candidate = (resolved_root / relative).resolve()
    try:
        candidate.relative_to(resolved_root)
    except ValueError:
        failures.append(f"{owner}: archive resolves outside artifact root")
        return None
    if not candidate.is_dir():
        failures.append(f"{owner}: archive directory is missing: {relative}")
        return None
    return candidate


def _safe_external_relative_file(
    artifact_root: Path,
    relative: object,
    owner: str,
    failures: list[str],
) -> Path | None:
    if not isinstance(relative, str) or not relative:
        failures.append(f"{owner}: relative file path is missing")
        return None
    relative_path = Path(relative)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        failures.append(f"{owner}: relative file path is unsafe: {relative}")
        return None
    resolved_root = artifact_root.expanduser().resolve()
    candidate = (resolved_root / relative_path).resolve()
    try:
        candidate.relative_to(resolved_root)
    except ValueError:
        failures.append(f"{owner}: relative file resolves outside artifact root")
        return None
    if not candidate.is_file():
        failures.append(f"{owner}: required file is missing: {relative}")
        return None
    return candidate


def _require_contained_entry(
    root: Path,
    candidate: Path,
    owner: str,
    label: str,
    failures: list[str],
    *,
    directory: bool,
) -> bool:
    """Reject missing entries and every symlink hop outside a trusted tree."""

    lexical_root = root.absolute()
    lexical_candidate = candidate.absolute()
    resolved_root = root.resolve()
    try:
        relative = lexical_candidate.relative_to(lexical_root)
    except ValueError:
        try:
            relative = lexical_candidate.relative_to(resolved_root)
        except ValueError:
            failures.append(f"{owner}: {label} is outside its trusted root")
            return False
    current = resolved_root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            failures.append(f"{owner}: {label} must not traverse a symlink")
            return False
    try:
        resolved_candidate = candidate.resolve(strict=True)
        resolved_candidate.relative_to(resolved_root)
    except (OSError, ValueError):
        failures.append(f"{owner}: {label} does not resolve inside its trusted root")
        return False
    correct_type = (
        resolved_candidate.is_dir()
        if directory
        else resolved_candidate.is_file()
    )
    if not correct_type:
        expected = "directory" if directory else "regular file"
        failures.append(f"{owner}: {label} must be a contained {expected}")
        return False
    return True


def _validate_zip(path: Path, owner: str, failures: list[str]) -> zipfile.ZipFile | None:
    try:
        archive = zipfile.ZipFile(path)
        names = archive.namelist()
        if len(names) != len(set(names)):
            failures.append(f"{owner}: ZIP contains duplicate member names")
            archive.close()
            return None
        for name in names:
            member = PurePosixPath(name)
            if member.is_absolute() or ".." in member.parts:
                failures.append(f"{owner}: ZIP contains an unsafe member path: {name}")
                archive.close()
                return None
        corrupt = archive.testzip()
        if corrupt is not None:
            failures.append(f"{owner}: ZIP integrity failed at {corrupt}")
            archive.close()
            return None
        return archive
    except (OSError, zipfile.BadZipFile) as error:
        failures.append(f"{owner}: cannot read ZIP bytes: {error}")
        return None


def _read_text_member(
    archive: zipfile.ZipFile,
    member: str,
    owner: str,
    failures: list[str],
) -> str | None:
    try:
        return archive.read(member).decode("utf-8")
    except KeyError:
        failures.append(f"{owner}: missing {member}")
    except UnicodeDecodeError as error:
        failures.append(f"{owner}: {member} is not UTF-8: {error}")
    return None


def _parse_android_manifest(
    xml: str,
    owner: str,
    failures: list[str],
) -> dict[str, Any] | None:
    try:
        root = ElementTree.fromstring(xml)
    except ElementTree.ParseError as error:
        failures.append(f"{owner}: Bundletool manifest is invalid XML: {error}")
        return None
    android = f"{{{ANDROID_NAMESPACE}}}"
    uses_sdk = root.find("uses-sdk")
    try:
        identity = {
            "package_id": root.attrib["package"],
            "version_code": int(root.attrib[f"{android}versionCode"]),
            "version_name": root.attrib[f"{android}versionName"],
            "min_sdk": int(uses_sdk.attrib[f"{android}minSdkVersion"]),
            "target_sdk": int(uses_sdk.attrib[f"{android}targetSdkVersion"]),
        }
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        failures.append(f"{owner}: Bundletool manifest identity is incomplete: {error}")
        return None
    identity["features"] = {
        feature.attrib.get(f"{android}name", ""): (
            feature.attrib.get(f"{android}required", "true").lower() != "false"
        )
        for feature in root.findall("uses-feature")
        if feature.attrib.get(f"{android}name")
    }
    identity["metadata"] = {
        item.attrib.get(f"{android}name", ""): item.attrib.get(f"{android}value")
        for item in root.findall("./application/meta-data")
        if item.attrib.get(f"{android}name")
    }
    return identity


def _verify_android(
    artifact_id: str,
    path: Path,
    artifact: dict[str, Any],
    manifest: dict[str, Any],
    bundletool_jar: Path | None,
    failures: list[str],
    runner: CommandRunner,
) -> dict[str, Any] | None:
    owner = f"upload manifest artifact {artifact_id}"
    java_tools = _resolve_java_toolchain(owner, failures)
    openssl = _required_system_tool(SYSTEM_OPENSSL, owner, failures)
    if java_tools is None or openssl is None:
        return None
    archive = _validate_zip(path, owner, failures)
    if archive is None:
        return None
    try:
        names = archive.namelist()
        top_level_entries = {PurePosixPath(name).parts[0] for name in names if name}
        required_members = {
            "BundleConfig.pb",
            "base/manifest/AndroidManifest.xml",
        }
        missing_members = required_members - set(names)
        if missing_members:
            failures.append(
                f"{owner}: AAB is missing required members: {sorted(missing_members)}"
            )
        unexpected_top_level = top_level_entries - {
            "base",
            "BUNDLE-METADATA",
            "BundleConfig.pb",
            "META-INF",
        }
        if unexpected_top_level:
            failures.append(
                f"{owner}: AAB contains unexpected feature/module roots: "
                f"{sorted(unexpected_top_level)}"
            )
        signature_files = {
            PurePosixPath(name).suffix.upper()
            for name in names
            if re.fullmatch(r"META-INF/[^/]+\.(?:SF|RSA|DSA|EC)", name, re.I)
        }
        if ".SF" not in signature_files or not signature_files.intersection(
            {".RSA", ".DSA", ".EC"}
        ):
            failures.append(f"{owner}: AAB has no complete JAR signature entries")

        vcs = _read_text_member(
            archive,
            "base/root/META-INF/version-control-info.textproto",
            owner,
            failures,
        )
        revisions = (
            set(re.findall(r'revision:\s*"([0-9a-f]{40})"', vcs))
            if vcs is not None
            else set()
        )
        expected_revision = manifest.get("source_revision")
        if revisions != {expected_revision}:
            failures.append(
                f"{owner}: embedded VCS revisions {sorted(revisions)} differ from "
                f"manifest source_revision {expected_revision!r}"
            )
    finally:
        archive.close()

    jarsigner = runner(
        [java_tools["jarsigner"], "-verify", "-verbose", "-certs", str(path)],
        text=True,
        timeout=120,
    )
    jarsigner_output = f"{jarsigner.stdout or ''}\n{jarsigner.stderr or ''}".lower()
    if (
        jarsigner.returncode != 0
        or "jar verified." not in jarsigner_output
        or "jar is unsigned" in jarsigner_output
        or "unsigned entries" in jarsigner_output
        or re.search(r"(?m)^\s*\?\s*=\s*unsigned entry", jarsigner_output)
    ):
        failures.append(
            f"{owner}: jarsigner did not prove a signed AAB: "
            f"{_command_detail(jarsigner)}"
        )

    strict_jarsigner = runner(
        [
            java_tools["jarsigner"],
            "-verify",
            "-strict",
            "-verbose",
            "-certs",
            str(path),
        ],
        text=True,
        timeout=120,
    )
    strict_output = (
        f"{strict_jarsigner.stdout or ''}\n{strict_jarsigner.stderr or ''}".lower()
    )
    severe_strict_markers = (
        "certificate is expired",
        "certificate is not yet valid",
        "algorithm is disabled",
        "algorithm is considered a security risk",
        "invalid signature",
    )
    if (
        strict_jarsigner.returncode not in {0, 4}
        or "unsigned entries" in strict_output
        or "jar is unsigned" in strict_output
        or re.search(r"(?m)^\s*\?\s*=\s*unsigned entry", strict_output)
        or any(marker in strict_output for marker in severe_strict_markers)
    ):
        failures.append(
            f"{owner}: strict jarsigner reported integrity/signature errors: "
            f"{_command_detail(strict_jarsigner)}"
        )

    certificate = runner(
        [java_tools["keytool"], "-printcert", "-jarfile", str(path)],
        text=True,
        timeout=60,
    )
    certificate_output = f"{certificate.stdout or ''}\n{certificate.stderr or ''}"
    fingerprints = {
        _normalise_fingerprint(value)
        for value in re.findall(
            r"SHA256:\s*([0-9A-Fa-f: ]{64,})",
            certificate_output,
        )
    }
    fingerprints.discard("")
    if certificate.returncode != 0 or fingerprints != {
        ANDROID_UPLOAD_CERTIFICATE_SHA256
    }:
        failures.append(
            f"{owner}: AAB signer SHA-256 {sorted(fingerprints)} differs from "
            "the pinned Google Play upload certificate"
        )
    if "Signature algorithm name: SHA256withRSA" not in certificate_output or (
        "2048-bit RSA key" not in certificate_output
    ):
        failures.append(f"{owner}: AAB signer algorithm/key strength is unexpected")

    certificate_rfc = runner(
        [java_tools["keytool"], "-printcert", "-jarfile", str(path), "-rfc"],
        text=True,
        timeout=60,
    )
    certificate_pem_output = (
        f"{certificate_rfc.stdout or ''}\n{certificate_rfc.stderr or ''}"
    )
    certificate_pem_match = re.search(
        r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----",
        certificate_pem_output,
        re.S,
    )
    if certificate_rfc.returncode != 0 or certificate_pem_match is None:
        failures.append(f"{owner}: cannot extract the AAB signer certificate")
    else:
        with tempfile.TemporaryDirectory(prefix="nimbo-android-cert-") as directory:
            certificate_path = Path(directory) / "upload-certificate.pem"
            certificate_path.write_text(
                certificate_pem_match.group(0) + "\n",
                encoding="ascii",
            )
            certificate_der = runner(
                [
                    openssl,
                    "x509",
                    "-in",
                    str(certificate_path),
                    "-outform",
                    "DER",
                ],
                text=False,
                timeout=60,
            )
            der_bytes = certificate_der.stdout
            if isinstance(der_bytes, str):
                der_bytes = der_bytes.encode("utf-8")
            extracted_fingerprint = (
                hashlib.sha256(der_bytes).hexdigest()
                if certificate_der.returncode == 0 and isinstance(der_bytes, bytes)
                else None
            )
            if extracted_fingerprint != ANDROID_UPLOAD_CERTIFICATE_SHA256:
                failures.append(
                    f"{owner}: extracted signer certificate SHA-256 "
                    f"{extracted_fingerprint!r} differs from the pinned upload "
                    "certificate"
                )
            certificate_validity = runner(
                [
                    openssl,
                    "verify",
                    "-CAfile",
                    str(certificate_path),
                    str(certificate_path),
                ],
                text=True,
                timeout=60,
            )
            if certificate_validity.returncode != 0:
                failures.append(
                    f"{owner}: upload certificate validity check failed: "
                    f"{_command_detail(certificate_validity)}"
                )

    if bundletool_jar is None:
        failures.append(
            f"{owner}: verified-current Android bytes require {BUNDLETOOL_ENV}"
        )
        return None
    resolved_bundletool = bundletool_jar.expanduser().resolve()
    if not resolved_bundletool.is_file():
        failures.append(f"{owner}: Bundletool JAR is missing: {bundletool_jar}")
        return None
    tool_digest = _sha256_file(resolved_bundletool)
    if tool_digest != BUNDLETOOL_SHA256:
        failures.append(
            f"{owner}: Bundletool SHA-256 {tool_digest} differs from pinned "
            f"{BUNDLETOOL_SHA256}"
        )
        return None

    version = runner(
        [java_tools["java"], "-jar", str(resolved_bundletool), "version"],
        text=True,
        timeout=60,
    )
    if version.returncode != 0 or (version.stdout or "").strip() != BUNDLETOOL_VERSION:
        failures.append(
            f"{owner}: Bundletool version check failed: {_command_detail(version)}"
        )

    validation = runner(
        [
            java_tools["java"],
            "-jar",
            str(resolved_bundletool),
            "validate",
            f"--bundle={path}",
        ],
        text=True,
        timeout=180,
    )
    if validation.returncode != 0:
        failures.append(
            f"{owner}: Bundletool validation failed: {_command_detail(validation)}"
        )

    manifest_dump = runner(
        [
            java_tools["java"],
            "-jar",
            str(resolved_bundletool),
            "dump",
            "manifest",
            f"--bundle={path}",
            "--module=base",
        ],
        text=True,
        timeout=120,
    )
    identity = None
    if manifest_dump.returncode != 0:
        failures.append(
            f"{owner}: Bundletool manifest dump failed: "
            f"{_command_detail(manifest_dump)}"
        )
    else:
        identity = _parse_android_manifest(
            manifest_dump.stdout or "",
            owner,
            failures,
        )

    expected_identity = artifact.get("version_code")
    expected_min_sdk = 24 if artifact_id == "android_phone" else 30
    if identity is not None:
        expected = {
            "package_id": ANDROID_PACKAGE_ID,
            "version_code": expected_identity,
            "version_name": manifest.get("release"),
            "min_sdk": expected_min_sdk,
            "target_sdk": 36,
        }
        for field, value in expected.items():
            if identity.get(field) != value:
                failures.append(
                    f"{owner}: Android manifest {field} {identity.get(field)!r} "
                    f"differs from expected {value!r}"
                )
        watch_feature = identity.get("features", {}).get(
            "android.hardware.type.watch"
        )
        if artifact_id == "wear_os":
            if watch_feature is not True:
                failures.append(
                    f"{owner}: Wear AAB must require android.hardware.type.watch"
                )
            if identity.get("metadata", {}).get(
                "com.google.android.wearable.standalone"
            ) != "false":
                failures.append(
                    f"{owner}: Wear AAB must declare wearable.standalone=false"
                )
        elif watch_feature is not None:
            failures.append(f"{owner}: phone AAB unexpectedly declares watch hardware")

    if any(failure.startswith(f"{owner}:") for failure in failures):
        return None
    return {
        "package_id": ANDROID_PACKAGE_ID,
        "version_name": manifest.get("release"),
        "version_code": expected_identity,
        "source_revision": manifest.get("source_revision"),
        "signer_sha256": ANDROID_UPLOAD_CERTIFICATE_SHA256,
        "bundletool_version": BUNDLETOOL_VERSION,
        "bundletool_sha256": BUNDLETOOL_SHA256,
    }


def _plist_from_command(
    result: subprocess.CompletedProcess[Any],
    owner: str,
    label: str,
    failures: list[str],
) -> dict[str, Any] | None:
    if result.returncode != 0:
        failures.append(f"{owner}: {label} failed: {_command_detail(result)}")
        return None
    candidates = (result.stdout, result.stderr)
    for candidate in candidates:
        if isinstance(candidate, str):
            candidate = candidate.encode("utf-8")
        if isinstance(candidate, bytes) and candidate.strip():
            try:
                payload = plistlib.loads(candidate)
            except Exception:
                continue
            if isinstance(payload, dict):
                return payload
    failures.append(f"{owner}: {label} did not return a plist object")
    return None


def _macho_uuids(
    path: Path,
    owner: str,
    label: str,
    failures: list[str],
    runner: CommandRunner,
) -> set[tuple[str, str]]:
    result = runner(
        [str(APPLE_XCRUN), "dwarfdump", "--uuid", str(path)],
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        failures.append(f"{owner}: {label} UUID inspection failed: {_command_detail(result)}")
        return set()
    output = f"{result.stdout or ''}\n{result.stderr or ''}"
    values = {
        (uuid.upper(), architecture)
        for uuid, architecture in re.findall(
            r"UUID:\s*([0-9A-Fa-f-]{36})\s*\(([^)]+)\)", output
        )
    }
    if not values:
        failures.append(f"{owner}: {label} has no Mach-O UUIDs")
    return values


def _verify_apple_product(
    bundle: Path,
    product: dict[str, Any],
    release: object,
    build: object,
    revision: object,
    archive: Path,
    bundle_root: Path,
    owner: str,
    failures: list[str],
    runner: CommandRunner,
    expected_macho_uuids: Sequence[str] | None = None,
    distribution_required: bool = True,
) -> dict[str, Any] | None:
    role = str(product["role"])
    product_owner = f"{owner} {role}"
    if not _require_contained_entry(
        bundle_root,
        bundle,
        product_owner,
        "embedded bundle",
        failures,
        directory=True,
    ):
        return None
    info_path = bundle / "Info.plist"
    if not _require_contained_entry(
        bundle_root,
        info_path,
        product_owner,
        "Info.plist",
        failures,
        directory=False,
    ):
        return None
    try:
        info = plistlib.loads(info_path.read_bytes())
    except (OSError, plistlib.InvalidFileException) as error:
        failures.append(f"{product_owner}: cannot read Info.plist: {error}")
        return None
    if not isinstance(info, dict):
        failures.append(f"{product_owner}: Info.plist root must be a dictionary")
        return None
    expected_info = {
        "CFBundleIdentifier": product["bundle_id"],
        "CFBundleShortVersionString": release,
        "CFBundleVersion": str(build),
        "NimboSourceRevision": revision,
    }
    for key, expected in expected_info.items():
        if info.get(key) != expected:
            failures.append(
                f"{product_owner}: Info.plist {key} {info.get(key)!r} differs "
                f"from expected {expected!r}"
            )
    if info.get("MinimumOSVersion") != product["minimum_os"]:
        failures.append(
            f"{product_owner}: MinimumOSVersion {info.get('MinimumOSVersion')!r} "
            f"differs from expected {product['minimum_os']!r}"
        )
    if info.get("DTPlatformName") != product["platform"]:
        failures.append(
            f"{product_owner}: DTPlatformName {info.get('DTPlatformName')!r} "
            f"differs from expected {product['platform']!r}"
        )
    supported_value = info.get("CFBundleSupportedPlatforms")
    supported_platforms = (
        set(supported_value)
        if isinstance(supported_value, list)
        and all(isinstance(value, str) for value in supported_value)
        else set()
    )
    if not isinstance(supported_value, list) or not all(
        isinstance(value, str) for value in supported_value
    ):
        failures.append(
            f"{product_owner}: CFBundleSupportedPlatforms must be a string array"
        )
    if supported_platforms != {product["supported_platform"]}:
        failures.append(
            f"{product_owner}: supported platforms {sorted(supported_platforms)} "
            f"differ from expected {[product['supported_platform']]}"
        )
    device_family_value = info.get("UIDeviceFamily")
    device_families = (
        set(device_family_value)
        if isinstance(device_family_value, list)
        and all(
            isinstance(value, int) and not isinstance(value, bool)
            for value in device_family_value
        )
        else set()
    )
    if not isinstance(device_family_value, list) or not all(
        isinstance(value, int) and not isinstance(value, bool)
        for value in device_family_value
    ):
        failures.append(f"{product_owner}: UIDeviceFamily must be an integer array")
    if device_families != product["device_families"]:
        failures.append(
            f"{product_owner}: UIDeviceFamily {sorted(device_families)} differs "
            f"from expected {sorted(product['device_families'])}"
        )
    if role == "watch" and info.get("WKCompanionAppBundleIdentifier") != (
        ANDROID_PACKAGE_ID
    ):
        failures.append(f"{product_owner}: companion bundle identifier is invalid")
    if role == "watch" and info.get("WKApplication") is not True:
        failures.append(f"{product_owner}: WKApplication must be true")
    if role == "app" and info.get("ITSAppUsesNonExemptEncryption") is not False:
        failures.append(
            f"{product_owner}: ITSAppUsesNonExemptEncryption must be false"
        )

    executable = bundle / str(product["executable"])
    if not _require_contained_entry(
        bundle_root,
        executable,
        product_owner,
        "executable",
        failures,
        directory=False,
    ):
        return None
    architectures_result = runner(
        [str(APPLE_XCRUN), "lipo", "-archs", str(executable)],
        text=True,
        timeout=60,
    )
    architectures = set((architectures_result.stdout or "").strip().split())
    if architectures_result.returncode != 0 or architectures != product["architectures"]:
        failures.append(
            f"{product_owner}: architectures {sorted(architectures)} differ from "
            f"expected {sorted(product['architectures'])}"
        )

    verification = runner(
        [str(APPLE_CODESIGN), "--verify", "--strict", "--verbose=4", str(bundle)],
        text=True,
        timeout=120,
    )
    if verification.returncode != 0:
        failures.append(
            f"{product_owner}: codesign verification failed: "
            f"{_command_detail(verification)}"
        )

    display = runner(
        [str(APPLE_CODESIGN), "-d", "--verbose=4", str(bundle)],
        text=True,
        timeout=60,
    )
    display_output = f"{display.stdout or ''}\n{display.stderr or ''}"
    authorities = re.findall(r"(?m)^Authority=(.+)$", display_output)
    teams = set(re.findall(r"(?m)^TeamIdentifier=([A-Z0-9]+)$", display_output))
    is_distribution = bool(
        authorities and authorities[0].startswith("Apple Distribution:")
    )
    is_development = bool(
        authorities and authorities[0].startswith("Apple Development:")
    )
    valid_authority = is_distribution or (
        not distribution_required and is_development
    )
    if display.returncode != 0 or not valid_authority:
        expected_authority = (
            "Apple Distribution"
            if distribution_required
            else "Apple Development or Apple Distribution"
        )
        failures.append(
            f"{product_owner}: signer is not {expected_authority}"
        )
    if teams != {APPLE_TEAM_ID}:
        failures.append(
            f"{product_owner}: TeamIdentifier {sorted(teams)} differs from {APPLE_TEAM_ID}"
        )

    entitlements_result = runner(
        [str(APPLE_CODESIGN), "-d", "--entitlements", ":-", str(bundle)],
        text=False,
        timeout=60,
    )
    entitlements = _plist_from_command(
        entitlements_result,
        product_owner,
        "signed-entitlements inspection",
        failures,
    )
    expected_application_identifier = f"{APPLE_TEAM_ID}.{product['bundle_id']}"
    if entitlements is not None:
        if entitlements.get("application-identifier") != expected_application_identifier:
            failures.append(
                f"{product_owner}: application-identifier differs from "
                f"{expected_application_identifier}"
            )
        if entitlements.get("com.apple.developer.team-identifier") != APPLE_TEAM_ID:
            failures.append(f"{product_owner}: signed entitlement team is invalid")
        if distribution_required:
            if entitlements.get("get-task-allow") is not False:
                failures.append(f"{product_owner}: get-task-allow must be false")
            if entitlements.get("beta-reports-active") is not True:
                failures.append(f"{product_owner}: beta-reports-active must be true")
        elif not isinstance(entitlements.get("get-task-allow"), bool):
            failures.append(
                f"{product_owner}: archive get-task-allow must be explicit"
            )
        groups_value = entitlements.get("com.apple.security.application-groups", [])
        groups = (
            groups_value
            if isinstance(groups_value, list)
            and all(isinstance(value, str) for value in groups_value)
            else []
        )
        if not isinstance(groups_value, list) or not all(
            isinstance(value, str) for value in groups_value
        ):
            failures.append(
                f"{product_owner}: signed app-group entitlement must be a string array"
            )
        expected_group = f"group.{ANDROID_PACKAGE_ID}"
        if product["app_group"] and expected_group not in groups:
            failures.append(f"{product_owner}: signed app-group entitlement is missing")
        if not product["app_group"] and groups:
            failures.append(f"{product_owner}: unexpected signed app-group entitlement")

    profile_path = bundle / "embedded.mobileprovision"
    if not _require_contained_entry(
        bundle_root,
        profile_path,
        product_owner,
        "embedded.mobileprovision",
        failures,
        directory=False,
    ):
        return None
    profile_result = runner(
        [str(APPLE_SECURITY), "cms", "-D", "-i", str(profile_path)],
        text=False,
        timeout=60,
    )
    profile = _plist_from_command(
        profile_result,
        product_owner,
        "provisioning-profile inspection",
        failures,
    )
    profile_certificate_hashes: set[str] = set()
    if profile is not None:
        profile_teams = profile.get("TeamIdentifier")
        profile_entitlements = profile.get("Entitlements")
        developer_certificates = profile.get("DeveloperCertificates")
        if profile_teams != [APPLE_TEAM_ID]:
            failures.append(f"{product_owner}: provisioning TeamIdentifier is invalid")
        expiration = profile.get("ExpirationDate")
        if not isinstance(expiration, datetime):
            failures.append(f"{product_owner}: provisioning expiration is missing")
        else:
            if expiration.tzinfo is None:
                expiration = expiration.replace(tzinfo=timezone.utc)
            if expiration <= datetime.now(timezone.utc):
                failures.append(f"{product_owner}: provisioning profile is expired")
        if distribution_required and (
            "ProvisionedDevices" in profile
            or profile.get("ProvisionsAllDevices") is True
        ):
            failures.append(
                f"{product_owner}: provisioning profile is not App Store distribution"
            )
        if not isinstance(developer_certificates, list) or not all(
            isinstance(certificate, bytes) for certificate in developer_certificates
        ):
            failures.append(
                f"{product_owner}: provisioning DeveloperCertificates are missing"
            )
        else:
            profile_certificate_hashes = {
                hashlib.sha256(certificate).hexdigest()
                for certificate in developer_certificates
            }
            if (
                distribution_required
                and APPLE_DISTRIBUTION_CERTIFICATE_SHA256
                not in profile_certificate_hashes
            ):
                failures.append(
                    f"{product_owner}: provisioning profile does not authorize "
                    "the pinned distribution certificate"
                )
        if not isinstance(profile_entitlements, dict):
            failures.append(f"{product_owner}: provisioning entitlements are missing")
        else:
            profile_application_identifier = profile_entitlements.get(
                "application-identifier"
            )
            allowed_profile_identifiers = {expected_application_identifier}
            if not distribution_required:
                allowed_profile_identifiers.add(f"{APPLE_TEAM_ID}.*")
            if profile_application_identifier not in allowed_profile_identifiers:
                failures.append(
                    f"{product_owner}: provisioning application-identifier is invalid"
                )
        if isinstance(profile_entitlements, dict):
            if distribution_required:
                if profile_entitlements.get("get-task-allow") is not False:
                    failures.append(
                        f"{product_owner}: provisioning get-task-allow must be false"
                    )
                if profile_entitlements.get("beta-reports-active") is not True:
                    failures.append(
                        f"{product_owner}: provisioning beta-reports-active must be true"
                    )
            elif not isinstance(
                profile_entitlements.get("get-task-allow"), bool
            ):
                failures.append(
                    f"{product_owner}: archive provisioning get-task-allow "
                    "must be explicit"
                )
            profile_groups = profile_entitlements.get(
                "com.apple.security.application-groups", []
            )
            if not isinstance(profile_groups, list) or not all(
                isinstance(value, str) for value in profile_groups
            ):
                failures.append(
                    f"{product_owner}: provisioning app groups must be a string array"
                )
                profile_groups = []
            expected_group = f"group.{ANDROID_PACKAGE_ID}"
            if product["app_group"] and expected_group not in profile_groups:
                failures.append(
                    f"{product_owner}: provisioning app-group entitlement is missing"
                )
            if not product["app_group"] and profile_groups:
                failures.append(
                    f"{product_owner}: unexpected provisioning app-group entitlement"
                )

    with tempfile.TemporaryDirectory(prefix="nimbo-codesign-cert-") as directory:
        prefix = Path(directory) / "cert"
        extraction = runner(
            [
                str(APPLE_CODESIGN),
                "-d",
                f"--extract-certificates={prefix}",
                str(bundle),
            ],
            text=True,
            timeout=60,
        )
        leaf = Path(f"{prefix}0")
        fingerprints: set[str] = set()
        if extraction.returncode == 0 and leaf.is_file():
            fingerprint = runner(
                [
                    str(SYSTEM_OPENSSL),
                    "x509",
                    "-inform",
                    "DER",
                    "-in",
                    str(leaf),
                    "-noout",
                    "-fingerprint",
                    "-sha256",
                    "-checkend",
                    "0",
                ],
                text=True,
                timeout=60,
            )
            fingerprint_output = f"{fingerprint.stdout or ''}\n{fingerprint.stderr or ''}"
            if fingerprint.returncode == 0:
                fingerprints = {
                    _normalise_fingerprint(value)
                    for value in re.findall(
                        r"Fingerprint=([0-9A-Fa-f:]+)", fingerprint_output
                    )
                }
        if distribution_required:
            if fingerprints != {APPLE_DISTRIBUTION_CERTIFICATE_SHA256}:
                failures.append(
                    f"{product_owner}: distribution certificate SHA-256 "
                    f"{sorted(fingerprints)} differs from pinned identity"
                )
        elif len(fingerprints) != 1 or not fingerprints.issubset(
            profile_certificate_hashes
        ):
            failures.append(
                f"{product_owner}: archive signer certificate {sorted(fingerprints)} "
                "is not authorized by its provisioning profile"
            )

    dsym = archive / "dSYMs" / str(product["dsym"])
    if not _require_contained_entry(
        archive,
        dsym,
        product_owner,
        "dSYM bundle",
        failures,
        directory=True,
    ):
        return None
    dsym_executable = (
        dsym / "Contents/Resources/DWARF" / str(product["executable"])
    )
    if not _require_contained_entry(
        archive,
        dsym_executable,
        product_owner,
        "dSYM executable",
        failures,
        directory=False,
    ):
        return None
    executable_uuids = _macho_uuids(
        executable,
        product_owner,
        "executable",
        failures,
        runner,
    )
    rendered_executable_uuids = sorted(
        f"{uuid} ({arch})" for uuid, arch in executable_uuids
    )
    if (
        expected_macho_uuids is not None
        and rendered_executable_uuids != list(expected_macho_uuids)
    ):
        failures.append(
            f"{product_owner}: executable UUIDs {rendered_executable_uuids} "
            f"differ from exported IPA {list(expected_macho_uuids)}"
        )
    dsym_uuids = _macho_uuids(
        dsym_executable,
        product_owner,
        "dSYM",
        failures,
        runner,
    )
    if executable_uuids and executable_uuids != dsym_uuids:
        failures.append(
            f"{product_owner}: executable UUIDs {sorted(executable_uuids)} differ "
            f"from dSYM UUIDs {sorted(dsym_uuids)}"
        )
    dsym_verification = runner(
        [str(APPLE_XCRUN), "dwarfdump", "--verify", str(dsym)],
        text=True,
        timeout=120,
    )
    if dsym_verification.returncode != 0:
        failures.append(
            f"{product_owner}: dSYM verification failed: "
            f"{_command_detail(dsym_verification)}"
        )

    if any(failure.startswith(f"{product_owner}:") for failure in failures):
        return None
    return {
        "role": role,
        "bundle_id": product["bundle_id"],
        "version": release,
        "build": build,
        "source_revision": revision,
        "team_id": APPLE_TEAM_ID,
        "signer_sha256": next(iter(fingerprints), None),
        "macho_uuids": rendered_executable_uuids,
    }


def _verify_apple_bundle_topology(
    app: Path,
    containment_root: Path,
    owner: str,
    failures: list[str],
    runner: CommandRunner,
) -> bool:
    """Require the one supported app/widget/watch code topology and deep signature."""

    failure_count = len(failures)
    if not _require_contained_entry(
        containment_root,
        app,
        owner,
        "Nimbo.app bundle",
        failures,
        directory=True,
    ):
        return False
    expected_extension = app / "PlugIns/NimboWidget.appex"
    expected_watch_app = app / "Watch/NimboWatch.app"
    _require_contained_entry(
        containment_root,
        expected_extension,
        owner,
        "NimboWidget.appex bundle",
        failures,
        directory=True,
    )
    _require_contained_entry(
        containment_root,
        expected_watch_app,
        owner,
        "NimboWatch.app bundle",
        failures,
        directory=True,
    )
    extensions = {
        candidate.relative_to(app).as_posix()
        for candidate in (app / "PlugIns").glob("*.appex")
    }
    watch_apps = {
        candidate.relative_to(app).as_posix()
        for candidate in (app / "Watch").glob("*.app")
    }
    if extensions != {"PlugIns/NimboWidget.appex"}:
        failures.append(
            f"{owner}: embedded app-extension topology is unexpected: "
            f"{sorted(extensions)}"
        )
    if watch_apps != {"Watch/NimboWatch.app"}:
        failures.append(
            f"{owner}: embedded watch-app topology is unexpected: "
            f"{sorted(watch_apps)}"
        )
    allowed_code_bundles = {
        (app / "PlugIns/NimboWidget.appex").resolve(),
        (app / "Watch/NimboWatch.app").resolve(),
    }
    discovered_code_bundles = {
        candidate.resolve()
        for suffix in ("*.app", "*.appex", "*.framework", "*.xpc")
        for candidate in app.rglob(suffix)
    }
    unexpected_code_bundles = discovered_code_bundles - allowed_code_bundles
    unexpected_dynamic_libraries = sorted(
        candidate.relative_to(app).as_posix()
        for candidate in app.rglob("*.dylib")
    )
    if unexpected_code_bundles or unexpected_dynamic_libraries:
        rendered_bundles: list[str] = []
        for candidate in unexpected_code_bundles:
            try:
                rendered = candidate.relative_to(app.resolve()).as_posix()
            except ValueError:
                rendered = f"outside:{candidate}"
            rendered_bundles.append(rendered)
        rendered_bundles.sort()
        failures.append(
            f"{owner}: unexpected embedded executable code: "
            f"bundles={rendered_bundles}, dylibs={unexpected_dynamic_libraries}"
        )
    deep = runner(
        [
            str(APPLE_CODESIGN),
            "--verify",
            "--deep",
            "--strict",
            "--verbose=4",
            str(app),
        ],
        text=True,
        timeout=180,
    )
    if deep.returncode != 0:
        failures.append(
            f"{owner}: deep codesign verification failed: {_command_detail(deep)}"
        )
    return len(failures) == failure_count


def _verify_apple(
    path: Path,
    artifact: dict[str, Any],
    manifest: dict[str, Any],
    artifact_root: Path,
    failures: list[str],
    runner: CommandRunner,
) -> dict[str, Any] | None:
    owner = "upload manifest artifact apple"
    required_tools = (
        APPLE_CODESIGN,
        APPLE_SECURITY,
        APPLE_XCRUN,
        SYSTEM_OPENSSL,
    )
    if any(
        _required_system_tool(tool, owner, failures) is None
        for tool in required_tools
    ):
        return None
    archive_zip = _validate_zip(path, owner, failures)
    if archive_zip is None:
        return None
    apple_archive = _safe_external_directory(
        artifact_root,
        EXPECTED_POLICY["apple_archive_relative_path"],
        owner,
        failures,
    )
    if apple_archive is None:
        archive_zip.close()
        return None
    export_options_path = _safe_external_relative_file(
        artifact_root,
        EXPECTED_POLICY["apple_export_options_relative_path"],
        owner,
        failures,
    )
    if export_options_path is None:
        archive_zip.close()
        return None
    try:
        export_options = plistlib.loads(export_options_path.read_bytes())
    except (OSError, plistlib.InvalidFileException) as error:
        failures.append(f"{owner}: cannot read ExportOptions.plist: {error}")
        archive_zip.close()
        return None
    if not isinstance(export_options, dict):
        failures.append(f"{owner}: ExportOptions.plist root must be a dictionary")
        archive_zip.close()
        return None
    expected_export_options = {
        "method": "app-store-connect",
        "teamID": APPLE_TEAM_ID,
        "uploadSymbols": True,
        "manageAppVersionAndBuildNumber": False,
    }
    for key, expected in expected_export_options.items():
        if export_options.get(key) != expected:
            failures.append(
                f"{owner}: ExportOptions.plist {key} "
                f"{export_options.get(key)!r} differs from expected {expected!r}"
            )

    try:
        archive_info = plistlib.loads((apple_archive / "Info.plist").read_bytes())
    except (OSError, plistlib.InvalidFileException) as error:
        failures.append(f"{owner}: cannot read archive Info.plist: {error}")
        archive_zip.close()
        return None
    if not isinstance(archive_info, dict):
        failures.append(f"{owner}: archive Info.plist root must be a dictionary")
        archive_zip.close()
        return None
    application_properties = archive_info.get("ApplicationProperties")
    expected_archive_properties = {
        "CFBundleIdentifier": ANDROID_PACKAGE_ID,
        "CFBundleShortVersionString": manifest.get("release"),
        "CFBundleVersion": str(artifact.get("build")),
        "Team": APPLE_TEAM_ID,
    }
    if not isinstance(application_properties, dict):
        failures.append(f"{owner}: archive ApplicationProperties are missing")
    else:
        for key, expected in expected_archive_properties.items():
            if application_properties.get(key) != expected:
                failures.append(
                    f"{owner}: archive {key} {application_properties.get(key)!r} "
                    f"differs from expected {expected!r}"
                )

    archive_applications = apple_archive / "Products/Applications"
    expected_archive_app = archive_applications / "Nimbo.app"
    archive_apps = (
        sorted(archive_applications.glob("*.app"))
        if archive_applications.is_dir() and not archive_applications.is_symlink()
        else []
    )
    archive_app: Path | None = None
    if archive_apps != [expected_archive_app]:
        failures.append(
            f"{owner}: xcarchive must contain exactly "
            "Products/Applications/Nimbo.app"
        )
    elif _require_contained_entry(
        apple_archive,
        expected_archive_app,
        owner,
        "archived Nimbo.app bundle",
        failures,
        directory=True,
    ):
        archive_app = expected_archive_app

    products: list[dict[str, Any]] = []
    archive_products: list[dict[str, Any]] = []
    try:
        with tempfile.TemporaryDirectory(prefix="nimbo-ipa-") as directory:
            destination = Path(directory)
            archive_zip.extractall(destination)
            apps = sorted((destination / "Payload").glob("*.app"))
            if len(apps) != 1:
                failures.append(
                    f"{owner}: IPA must contain exactly one top-level Payload app"
                )
                return None
            app = apps[0]
            _verify_apple_bundle_topology(
                app,
                destination,
                f"{owner} exported IPA",
                failures,
                runner,
            )
            if archive_app is not None:
                _verify_apple_bundle_topology(
                    archive_app,
                    apple_archive,
                    f"{owner} xcarchive",
                    failures,
                    runner,
                )
            for product in APPLE_PRODUCTS:
                bundle = app / product["relative_path"]
                verified = _verify_apple_product(
                    bundle,
                    product,
                    manifest.get("release"),
                    artifact.get("build"),
                    manifest.get("source_revision"),
                    apple_archive,
                    destination,
                    f"{owner} exported IPA",
                    failures,
                    runner,
                )
                if verified is not None:
                    products.append(verified)
                if archive_app is None:
                    continue
                archive_bundle = archive_app / product["relative_path"]
                archive_verified = _verify_apple_product(
                    archive_bundle,
                    product,
                    manifest.get("release"),
                    artifact.get("build"),
                    manifest.get("source_revision"),
                    apple_archive,
                    apple_archive,
                    f"{owner} xcarchive",
                    failures,
                    runner,
                    expected_macho_uuids=(
                        verified.get("macho_uuids")
                        if verified is not None
                        else None
                    ),
                    distribution_required=False,
                )
                if archive_verified is not None:
                    archive_products.append(archive_verified)

            exported_by_role = {item["role"]: item for item in products}
            archive_by_role = {item["role"]: item for item in archive_products}
            for role in ("app", "widget", "watch"):
                exported = exported_by_role.get(role)
                archived = archive_by_role.get(role)
                if exported is None or archived is None:
                    failures.append(
                        f"{owner}: cannot bind {role} across IPA, xcarchive, and dSYM"
                    )
                    continue
                if archived["macho_uuids"] != exported["macho_uuids"]:
                    failures.append(
                        f"{owner}: xcarchive {role} executable UUIDs "
                        f"{archived['macho_uuids']} differ from exported IPA "
                        f"{exported['macho_uuids']}"
                    )
    finally:
        archive_zip.close()

    if any(failure.startswith(owner) for failure in failures):
        return None
    return {
        "release": manifest.get("release"),
        "build": artifact.get("build"),
        "source_revision": manifest.get("source_revision"),
        "team_id": APPLE_TEAM_ID,
        "signer_sha256": APPLE_DISTRIBUTION_CERTIFICATE_SHA256,
        "products": products,
        "archive_products": archive_products,
    }


def validate_verification_policy(
    manifest: dict[str, Any],
    failures: list[str],
) -> bool:
    valid = True
    if manifest.get("schema_version") != 2:
        failures.append("upload manifest: schema_version must be 2")
        valid = False
    release = manifest.get("release")
    if not isinstance(release, str) or not release.strip():
        failures.append("upload manifest: release must be a non-empty string")
        valid = False
    source_revision = manifest.get("source_revision")
    if not isinstance(source_revision, str) or REVISION_PATTERN.fullmatch(
        source_revision
    ) is None:
        failures.append(
            "upload manifest: source_revision must be a full lowercase 40-hex commit"
        )
        valid = False
    policy = manifest.get("verification_policy")
    if policy != EXPECTED_POLICY:
        failures.append(
            "upload manifest: verification_policy differs from the pinned "
            "release-artifact contract"
        )
        valid = False
    return valid


def _validate_artifact_contract(
    repository_root: Path,
    manifest: dict[str, Any],
    artifacts: dict[str, Any],
    failures: list[str],
) -> bool:
    """Validate the complete current/historical artifact contract."""

    failure_count = len(failures)
    release = manifest.get("release")
    revision = manifest.get("source_revision")
    identities = _read_release_identities(repository_root, failures)
    identity_fields = {
        "android_phone": "version_code",
        "wear_os": "version_code",
        "apple": "build",
    }
    common_fields = {
        "filename",
        "source_sync",
        "sha256",
        "signing_evidence",
        "physical_qa_evidence",
        "source_sync_evidence",
        "historical_candidate",
    }

    for artifact_id in ("android_phone", "wear_os", "apple"):
        artifact = artifacts.get(artifact_id)
        owner = f"upload manifest artifact {artifact_id}"
        identity_field = identity_fields[artifact_id]
        expected_fields = common_fields | {identity_field}
        if not isinstance(artifact, dict) or set(artifact) != expected_fields:
            actual_fields = sorted(artifact) if isinstance(artifact, dict) else []
            failures.append(
                f"{owner}: expected exactly {sorted(expected_fields)}, got "
                f"{actual_fields}"
            )
            continue

        identity = identities.get(artifact_id)
        if identity is None:
            continue
        version_name, build_number = identity
        if release != version_name:
            failures.append(
                f"{owner}: source release {version_name!r} differs from manifest "
                f"{release!r}"
            )
        declared_identity = artifact.get(identity_field)
        if (
            isinstance(declared_identity, bool)
            or not isinstance(declared_identity, int)
            or declared_identity != build_number
        ):
            failures.append(
                f"{owner}: declared {identity_field} {declared_identity!r} differs "
                f"from source {build_number}"
            )
        expected_filename = {
            "android_phone": f"nimbo-phone-{release}-vc{build_number}.aab",
            "wear_os": f"nimbo-wear-{release}-vc{build_number}.aab",
            "apple": "Nimbo.ipa",
        }[artifact_id]
        if artifact.get("filename") != expected_filename:
            failures.append(
                f"{owner}: filename does not match the current source identity"
            )
        evidence_contains_digest(
            repository_root,
            artifact.get("source_sync_evidence"),
            revision,
            f"{owner}.source_sync_evidence",
            failures,
            binding="the manifest source_revision",
        )

        source_sync = artifact.get("source_sync")
        if source_sync == "blocked":
            for field_name in (
                "sha256",
                "signing_evidence",
                "physical_qa_evidence",
            ):
                if artifact.get(field_name) is not None:
                    failures.append(
                        f"{owner}: blocked artifact must keep {field_name} null"
                    )
            historical = artifact.get("historical_candidate")
            historical_fields = {
                "status",
                "filename",
                identity_field,
                "sha256",
                "signing_evidence",
                "physical_qa_evidence",
            }
            if not isinstance(historical, dict) or set(historical) != historical_fields:
                failures.append(
                    f"{owner}: blocked artifact requires one exact historical candidate"
                )
                continue
            if historical.get("status") != "historical-superseded":
                failures.append(
                    f"{owner}: historical candidate must be marked superseded"
                )
            historical_filename = historical.get("filename")
            if (
                not isinstance(historical_filename, str)
                or not historical_filename
                or Path(historical_filename).name != historical_filename
            ):
                failures.append(
                    f"{owner}: historical filename must be one plain file name"
                )
            historical_identity = historical.get(identity_field)
            if (
                isinstance(historical_identity, bool)
                or not isinstance(historical_identity, int)
                or historical_identity > build_number
            ):
                failures.append(
                    f"{owner}: historical identity must not exceed current source"
                )
            historical_sha = historical.get("sha256")
            if (
                not isinstance(historical_sha, str)
                or SHA256_PATTERN.fullmatch(historical_sha) is None
            ):
                failures.append(f"{owner}: historical SHA-256 is invalid")
            else:
                evidence_contains_digest(
                    repository_root,
                    historical.get("signing_evidence"),
                    historical_sha,
                    f"{owner}.historical.signing_evidence",
                    failures,
                )
            historical_physical = historical.get("physical_qa_evidence")
            if historical_physical is not None:
                evidence_contains_digest(
                    repository_root,
                    historical_physical,
                    historical_sha,
                    f"{owner}.historical.physical_qa_evidence",
                    failures,
                    binding="the historical artifact SHA-256",
                )
        elif source_sync == "verified-current":
            if artifact.get("historical_candidate") is not None:
                failures.append(
                    f"{owner}: verified-current artifact cannot carry a historical candidate"
                )
            repository = repository_root.resolve()
            evidence_identities: list[str] = []
            for value in (
                artifact.get("source_sync_evidence"),
                artifact.get("signing_evidence"),
                artifact.get("physical_qa_evidence"),
            ):
                if not isinstance(value, str):
                    continue
                relative = Path(value)
                if relative.is_absolute() or ".." in relative.parts:
                    continue
                resolved = (repository / relative).resolve()
                try:
                    evidence_identities.append(
                        resolved.relative_to(repository).as_posix()
                    )
                except ValueError:
                    continue
            if len(evidence_identities) != len(set(evidence_identities)):
                failures.append(
                    f"{owner}: source, signing, and physical evidence must be "
                    "separate committed records"
                )
            declared_sha = artifact.get("sha256")
            if (
                not isinstance(declared_sha, str)
                or SHA256_PATTERN.fullmatch(declared_sha) is None
            ):
                failures.append(f"{owner}: verified-current SHA-256 is invalid")
            else:
                evidence_contains_digest(
                    repository_root,
                    artifact.get("signing_evidence"),
                    declared_sha,
                    f"{owner}.signing_evidence",
                    failures,
                )
                physical_evidence = artifact.get("physical_qa_evidence")
                if physical_evidence is not None:
                    evidence_contains_digest(
                        repository_root,
                        physical_evidence,
                        declared_sha,
                        f"{owner}.physical_qa_evidence",
                        failures,
                    )
        else:
            failures.append(f"{owner}: invalid source_sync {source_sync!r}")
    return len(failures) == failure_count


def verify_manifest_artifacts(
    repository_root: Path,
    manifest: dict[str, Any],
    failures: list[str],
    *,
    artifact_root: Path | None = None,
    bundletool_jar: Path | None = None,
    runner: CommandRunner = _run_command,
) -> dict[str, VerificationResult]:
    """Validate artifact state and verify bytes for every current claim."""

    policy_valid = validate_verification_policy(manifest, failures)
    artifacts = manifest.get("artifacts")
    expected_artifacts = {"android_phone", "wear_os", "apple"}
    if not isinstance(artifacts, dict) or set(artifacts) != expected_artifacts:
        failures.append(
            "upload manifest: artifacts must contain exactly android_phone, "
            "wear_os, and apple"
        )
        return {}

    source_valid = validate_repository_source(
        repository_root,
        manifest.get("source_revision"),
        failures,
    )
    contract_valid = _validate_artifact_contract(
        repository_root,
        manifest,
        artifacts,
        failures,
    )

    resolved_artifact_root = artifact_root
    if resolved_artifact_root is None:
        configured = os.environ.get(ARTIFACT_ROOT_ENV)
        if configured:
            resolved_artifact_root = Path(configured)
    resolved_bundletool = bundletool_jar
    if resolved_bundletool is None:
        configured = os.environ.get(BUNDLETOOL_ENV)
        if configured:
            resolved_bundletool = Path(configured)

    results: dict[str, VerificationResult] = {}
    for artifact_id in ("android_phone", "wear_os", "apple"):
        artifact = artifacts.get(artifact_id)
        owner = f"upload manifest artifact {artifact_id}"
        if not isinstance(artifact, dict):
            failures.append(f"{owner}: artifact definition is missing")
            continue
        source_sync = artifact.get("source_sync")
        if source_sync == "blocked":
            results[artifact_id] = VerificationResult(
                artifact_id=artifact_id,
                source_sync="blocked",
                byte_verified=False,
            )
            continue
        if source_sync != "verified-current":
            failures.append(f"{owner}: invalid source_sync {source_sync!r}")
            results[artifact_id] = VerificationResult(
                artifact_id=artifact_id,
                source_sync=str(source_sync),
                byte_verified=False,
            )
            continue
        if not (policy_valid and source_valid and contract_valid):
            results[artifact_id] = VerificationResult(
                artifact_id=artifact_id,
                source_sync="verified-current",
                byte_verified=False,
            )
            continue
        if resolved_artifact_root is None:
            failures.append(
                f"{owner}: verified-current requires real artifact bytes through "
                f"{ARTIFACT_ROOT_ENV}"
            )
            results[artifact_id] = VerificationResult(
                artifact_id=artifact_id,
                source_sync="verified-current",
                byte_verified=False,
            )
            continue
        path = _safe_external_file(
            resolved_artifact_root,
            artifact.get("filename"),
            owner,
            failures,
        )
        if path is None:
            results[artifact_id] = VerificationResult(
                artifact_id=artifact_id,
                source_sync="verified-current",
                byte_verified=False,
            )
            continue
        digest = _sha256_file(path)
        declared_digest = artifact.get("sha256")
        if not isinstance(declared_digest, str) or not SHA256_PATTERN.fullmatch(
            declared_digest
        ):
            failures.append(f"{owner}: verified-current SHA-256 is invalid")
        elif digest != declared_digest:
            failures.append(
                f"{owner}: artifact SHA-256 {digest} differs from manifest "
                f"{declared_digest}"
            )

        failure_count = len(failures)
        with tempfile.TemporaryDirectory(prefix="nimbo-artifact-stage-") as directory:
            staging_directory = Path(directory)
            staged_path = staging_directory / path.name
            shutil.copyfile(path, staged_path)
            staged_path.chmod(0o400)
            staged_digest = _sha256_file(staged_path)
            if staged_digest != digest:
                failures.append(
                    f"{owner}: staged artifact SHA-256 {staged_digest} differs "
                    f"from source bytes {digest}"
                )
            if artifact_id in {"android_phone", "wear_os"}:
                details = _verify_android(
                    artifact_id,
                    staged_path,
                    artifact,
                    manifest,
                    resolved_bundletool,
                    failures,
                    runner,
                )
            else:
                details = _verify_apple(
                    staged_path,
                    artifact,
                    manifest,
                    resolved_artifact_root,
                    failures,
                    runner,
                )
            final_staged_digest = _sha256_file(staged_path)
            if final_staged_digest != staged_digest:
                failures.append(
                    f"{owner}: staged artifact changed during verification: "
                    f"{staged_digest} -> {final_staged_digest}"
                )
        final_digest = _sha256_file(path)
        if final_digest != digest:
            failures.append(
                f"{owner}: artifact changed during verification: "
                f"{digest} -> {final_digest}"
            )
        byte_verified = (
            digest == declared_digest
            and staged_digest == digest
            and final_staged_digest == staged_digest
            and final_digest == digest
            and details is not None
            and len(failures) == failure_count
        )
        results[artifact_id] = VerificationResult(
            artifact_id=artifact_id,
            source_sync="verified-current",
            byte_verified=byte_verified,
            sha256=digest,
            details=details or {},
        )
    return results


def _candidate_mapping_filename(phone_filename: object) -> str | None:
    if not isinstance(phone_filename, str) or Path(phone_filename).name != phone_filename:
        return None
    return f"{Path(phone_filename).stem}-mapping.txt"


def _verify_candidate_mapping(
    path: Path,
    phone_bundle: Path,
    failures: list[str],
) -> dict[str, Any] | None:
    owner = "upload manifest artifact android_phone mapping"
    try:
        size = path.stat().st_size
        with path.open("r", encoding="utf-8") as source:
            header = [source.readline().rstrip("\n") for _ in range(7)]
    except (OSError, UnicodeError) as error:
        failures.append(f"{owner}: cannot read mapping: {error}")
        return None
    required_exact = {
        "# compiler: R8",
        "# min_api: 24",
        '# {"id":"com.android.tools.r8.mapping","version":"2.2"}',
    }
    if size <= 0 or not required_exact.issubset(set(header)):
        failures.append(f"{owner}: R8 identity header is incomplete")
        return None
    for prefix in ("# compiler_version: ", "# pg_map_id: ", "# pg_map_hash: "):
        if not any(line.startswith(prefix) and len(line) > len(prefix) for line in header):
            failures.append(f"{owner}: missing {prefix.strip()}")
            return None
    digest = _sha256_file(path)
    embedded_path = "BUNDLE-METADATA/com.android.tools.build.obfuscation/proguard.map"
    try:
        with zipfile.ZipFile(phone_bundle) as bundle:
            embedded_names = [name for name in bundle.namelist() if name == embedded_path]
            if embedded_names != [embedded_path]:
                failures.append(
                    f"{owner}: phone AAB must contain exactly one embedded mapping"
                )
                return None
            embedded = bundle.read(embedded_path)
    except (OSError, zipfile.BadZipFile, KeyError) as error:
        failures.append(f"{owner}: cannot inspect embedded phone mapping: {error}")
        return None
    embedded_digest = hashlib.sha256(embedded).hexdigest()
    if embedded_digest != digest or embedded != path.read_bytes():
        failures.append(f"{owner}: external mapping differs from phone AAB mapping")
        return None
    return {
        "filename": path.name,
        "size": size,
        "sha256": digest,
        "embedded_path": embedded_path,
    }


def _unverified_candidate_results() -> dict[str, VerificationResult]:
    return {
        artifact_id: VerificationResult(
            artifact_id=artifact_id,
            source_sync="candidate-unverified",
            byte_verified=False,
        )
        for artifact_id in ("android_phone", "wear_os", "apple")
    }


def verify_signed_candidate_artifacts(
    repository_root: Path,
    manifest: dict[str, Any],
    failures: list[str],
    *,
    artifact_root: Path,
    bundletool_jar: Path,
    source_repository_root: Path | None = None,
    runner: CommandRunner = _run_command,
) -> SignedCandidateVerification:
    """Verify newly signed bytes before promoting the committed manifest.

    A release workflow cannot know deterministic artifact hashes until after it
    has built and signed the candidate.  The committed manifest therefore stays
    fail-closed as ``blocked`` while this function validates the real staged
    bytes, embedded source identity, store signing identities, Android bundle
    manifests, Apple archive/export topology, and dSYM UUID binding.  Its JSON
    receipt is evidence for a later committed manifest promotion; it is not a
    substitute for that promotion or for physical QA.
    """

    policy_valid = validate_verification_policy(manifest, failures)
    artifacts = manifest.get("artifacts")
    expected_artifacts = {"android_phone", "wear_os", "apple"}
    if not isinstance(artifacts, dict) or set(artifacts) != expected_artifacts:
        failures.append(
            "upload manifest: artifacts must contain exactly android_phone, "
            "wear_os, and apple"
        )
        return SignedCandidateVerification(
            artifacts={},
            candidate_set={},
            byte_verified=False,
        )

    release_source_root = source_repository_root or repository_root
    build_source_valid = validate_repository_source(
        release_source_root,
        manifest.get("source_revision"),
        failures,
    )
    current_source_valid = True
    if release_source_root.resolve() != repository_root.resolve():
        current_source_valid = validate_repository_source(
            repository_root,
            manifest.get("source_revision"),
            failures,
        )
    source_valid = build_source_valid and current_source_valid
    contract_valid = _validate_artifact_contract(
        repository_root,
        manifest,
        artifacts,
        failures,
    )
    for artifact_id in ("android_phone", "wear_os", "apple"):
        artifact = artifacts.get(artifact_id)
        if isinstance(artifact, dict) and artifact.get("source_sync") != "blocked":
            failures.append(
                f"upload manifest artifact {artifact_id}: signed-candidate "
                "preflight requires the committed manifest to remain blocked"
            )
            contract_valid = False

    results: dict[str, VerificationResult] = {}
    if not (policy_valid and source_valid and contract_valid):
        return SignedCandidateVerification(
            artifacts=_unverified_candidate_results(),
            candidate_set={},
            byte_verified=False,
        )

    phone_mapping_name = _candidate_mapping_filename(
        artifacts["android_phone"].get("filename")
    )
    filenames = {
        artifact.get("filename")
        for artifact in artifacts.values()
        if isinstance(artifact, dict) and isinstance(artifact.get("filename"), str)
    }
    if phone_mapping_name is None or len(filenames) != 3:
        failures.append("signed candidate: cannot derive the closed artifact layout")
        return SignedCandidateVerification(
            artifacts=_unverified_candidate_results(),
            candidate_set={},
            byte_verified=False,
        )
    expected_top_level = filenames | {
        phone_mapping_name,
        EXPECTED_POLICY["apple_archive_relative_path"],
        EXPECTED_POLICY["apple_export_options_relative_path"],
    }
    candidate_failure_count = len(failures)
    source_before = _snapshot_candidate_tree(
        artifact_root,
        failures,
        "signed candidate",
        expected_top_level=expected_top_level,
    )
    if source_before is None or len(failures) != candidate_failure_count:
        return SignedCandidateVerification(
            artifacts=_unverified_candidate_results(),
            candidate_set={},
            byte_verified=False,
        )

    candidate_set: dict[str, Any] = source_before.receipt()
    with tempfile.TemporaryDirectory(
        prefix="nimbo-signed-candidate-stage-"
    ) as directory:
        staged_root = Path(directory) / "bytes"
        shutil.copytree(artifact_root.resolve(), staged_root, copy_function=shutil.copy2)
        staged_before = _snapshot_candidate_tree(
            staged_root,
            failures,
            "staged signed candidate",
            expected_top_level=expected_top_level,
        )
        if (
            staged_before is None
            or staged_before.tree_sha256 != source_before.tree_sha256
        ):
            failures.append(
                "signed candidate: staged tree differs from source candidate tree"
            )

        mapping_path = _safe_external_file(
            staged_root,
            phone_mapping_name,
            "upload manifest artifact android_phone mapping",
            failures,
        )
        staged_phone_path = _safe_external_file(
            staged_root,
            artifacts["android_phone"].get("filename"),
            "upload manifest artifact android_phone",
            failures,
        )
        mapping_details = (
            _verify_candidate_mapping(mapping_path, staged_phone_path, failures)
            if mapping_path is not None and staged_phone_path is not None
            else None
        )
        if mapping_details is not None:
            candidate_set["phone_mapping"] = mapping_details

        for artifact_id in ("android_phone", "wear_os", "apple"):
            artifact = artifacts[artifact_id]
            owner = f"upload manifest artifact {artifact_id}"
            failure_count = len(failures)
            path = _safe_external_file(
                staged_root,
                artifact.get("filename"),
                owner,
                failures,
            )
            details: dict[str, Any] | None = None
            digest: str | None = None
            if path is not None:
                digest = _sha256_file(path)
                if artifact_id in {"android_phone", "wear_os"}:
                    details = _verify_android(
                        artifact_id,
                        path,
                        artifact,
                        manifest,
                        bundletool_jar,
                        failures,
                        runner,
                    )
                    if artifact_id == "android_phone" and details is not None:
                        if mapping_details is None:
                            failures.append(f"{owner}: verified R8 mapping is missing")
                        else:
                            details["mapping"] = mapping_details
                else:
                    details = _verify_apple(
                        path,
                        artifact,
                        manifest,
                        staged_root,
                        failures,
                        runner,
                    )
            byte_verified = (
                path is not None
                and details is not None
                and len(failures) == failure_count
            )
            results[artifact_id] = VerificationResult(
                artifact_id=artifact_id,
                source_sync=(
                    "candidate-verified"
                    if byte_verified
                    else "candidate-unverified"
                ),
                byte_verified=byte_verified,
                sha256=digest,
                details=details or {},
            )

        staged_after = _snapshot_candidate_tree(
            staged_root,
            failures,
            "staged signed candidate",
            expected_top_level=expected_top_level,
        )
        if (
            staged_before is None
            or staged_after is None
            or staged_before.tree_sha256 != staged_after.tree_sha256
            or staged_before.observation_sha256 != staged_after.observation_sha256
        ):
            failures.append("signed candidate: staged tree changed during verification")

        archive_path = staged_root / EXPECTED_POLICY["apple_archive_relative_path"]
        archive_snapshot = _snapshot_candidate_tree(
            archive_path,
            failures,
            "signed candidate Apple archive",
        )
        export_options_path = (
            staged_root / EXPECTED_POLICY["apple_export_options_relative_path"]
        )
        if archive_snapshot is not None:
            candidate_set["apple_archive"] = archive_snapshot.receipt()
        if export_options_path.is_file() and not export_options_path.is_symlink():
            candidate_set["export_options_sha256"] = _sha256_file(export_options_path)
        dsyms: dict[str, dict[str, Any]] = {}
        for product in APPLE_PRODUCTS:
            dsym_path = archive_path / "dSYMs" / product["dsym"]
            snapshot = _snapshot_candidate_tree(
                dsym_path,
                failures,
                f"signed candidate {product['role']} dSYM",
            )
            if snapshot is not None:
                dsyms[product["role"]] = snapshot.receipt()
        if dsyms:
            candidate_set["apple_dsyms"] = dsyms

    source_after = _snapshot_candidate_tree(
        artifact_root,
        failures,
        "signed candidate",
        expected_top_level=expected_top_level,
    )
    source_stable = (
        source_after is not None
        and source_after.tree_sha256 == source_before.tree_sha256
        and source_after.observation_sha256 == source_before.observation_sha256
    )
    if not source_stable:
        failures.append("signed candidate: source tree changed during verification")

    globally_verified = (
        len(failures) == candidate_failure_count
        and source_stable
        and len(results) == 3
        and all(result.byte_verified for result in results.values())
    )
    if not globally_verified:
        results = {
            artifact_id: VerificationResult(
                artifact_id=result.artifact_id,
                source_sync="candidate-unverified",
                byte_verified=False,
                sha256=result.sha256,
                details=result.details,
            )
            for artifact_id, result in results.items()
        }
        for artifact_id, fallback in _unverified_candidate_results().items():
            results.setdefault(artifact_id, fallback)
    return SignedCandidateVerification(
        artifacts=results,
        candidate_set=candidate_set,
        byte_verified=globally_verified,
        source_observation_sha256=source_after.observation_sha256 if source_after else None,
    )


def evidence_contains_digest(
    repository_root: Path,
    evidence: object,
    digest: object,
    label: str,
    failures: list[str],
    *,
    binding: str = "the verified artifact SHA-256",
) -> bool:
    if not isinstance(evidence, str) or not evidence.strip():
        failures.append(f"{label} must be an existing repository-relative file path")
        return False
    relative = Path(evidence)
    if relative.is_absolute() or ".." in relative.parts:
        failures.append(f"{label} must be an existing repository-relative file path")
        return False
    if relative.suffix != ".md" or relative.parts[:2] != ("growth", "quality"):
        failures.append(f"{label} must be a Markdown record under growth/quality")
        return False
    repository = repository_root.resolve()
    path = (repository / relative).resolve()
    try:
        path.relative_to(repository)
    except ValueError:
        failures.append(f"{label} resolves outside the repository: {evidence}")
        return False
    if not path.is_file():
        failures.append(f"{label} is missing: {evidence}")
        return False
    content = path.read_text(encoding="utf-8", errors="replace")
    try:
        tracked = _run_git(
            repository,
            ["ls-files", "--error-unmatch", "--", relative.as_posix()],
        )
        committed = _run_git(
            repository,
            ["show", f"HEAD:{relative.as_posix()}"],
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        failures.append(f"{label} cannot verify committed evidence: {error}")
        return False
    if tracked.returncode != 0 or committed.returncode != 0:
        failures.append(f"{label} must be tracked and committed: {evidence}")
        return False
    if committed.stdout != content:
        failures.append(f"{label} differs from committed HEAD bytes: {evidence}")
        return False
    if not isinstance(digest, str) or digest not in content:
        failures.append(f"{label} does not bind {binding}")
        return False
    return True


def verification_summary(
    results: dict[str, VerificationResult],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "artifacts": {
            artifact_id: {
                "source_sync": result.source_sync,
                "byte_verified": result.byte_verified,
                "sha256": result.sha256,
                "details": result.details,
            }
            for artifact_id, result in sorted(results.items())
        },
    }


def load_manifest(path: Path, failures: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        failures.append(f"upload manifest: cannot read JSON: {error}")
        return {}
    if not isinstance(payload, dict):
        failures.append("upload manifest: root must be a JSON object")
        return {}
    return payload
