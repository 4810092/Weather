#!/usr/bin/env python3
"""Fail closed when the hosted byte-verification and Pages chain drifts."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRUSTED_WORKFLOW = ROOT / ".github/workflows/trusted-release-verification.yml"
PAGES_WORKFLOW = ROOT / ".github/workflows/pages.yml"
TRUSTED_SHA256 = "1d7a58771e3b86ce214ff001528e4d513f2548cd4eaeef594bc0e0c7ae55cc62"
PAGES_SHA256 = "6a7f34c5ecf52a0fe23c72e1942d18e7a712d139e6def0663d1bba57c076ca9d"

TRUSTED_REQUIRED = (
    "name: Trusted release verification",
    "  workflow_dispatch:",
    "permissions: {}",
    "github.event_name == 'workflow_dispatch'",
    "github.repository == '4810092/Weather'",
    "github.repository_id == '1329018769'",
    "github.ref == 'refs/heads/master'",
    "NIMBO_WORKFLOW_SHA: ${{ github.sha }}",
    "  stage:",
    "Stage exact unpublished candidate without repository checkout",
    "contents: write",
    "live master changed during candidate staging",
    "staged candidate asset inventory mismatch",
    "retention-days: 1",
    "compression-level: 0",
    "  verify:",
    "needs: stage",
    "needs.stage.result == 'success'",
    "actions: read",
    "contents: read",
    "runs-on: macos-26",
    "ref: ${{ github.sha }}",
    "persist-credentials: false",
    "repos/4810092/Weather/git/ref/heads/master",
    "manual workflow commit is stale relative to live master",
    "live master changed during trusted verification",
    "draft storage tag unexpectedly resolves before verification",
    "repos/4810092/Weather/releases/382592451",
    "repos/4810092/Weather/releases/assets/544061853",
    "repos/4810092/Weather/releases/assets/544061890",
    '"draft": True',
    '"prerelease": True',
    '"published_at": None',
    '"immutable": False',
    "draft release asset ID set mismatch",
    "actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c",
    "name: trusted-candidate-stage-${{ github.sha }}",
    "downloaded staged asset inventory mismatch",
    "post-verification staged asset inventory mismatch",
    "candidate package member inventory mismatch",
    "candidate package regular-file count mismatch",
    "candidate package directory count mismatch",
    "candidate package expanded size mismatch",
    "candidate package links/special entries are forbidden",
    "unsafe candidate package mode",
    "destination.open(\"xb\")",
    "_snapshot_candidate_tree",
    "trusted extracted candidate tree digest mismatch",
    "bundletool-all-1.18.3.jar",
    "a099cfa1543f55593bc2ed16a70a7c67fe54b1747bb7301f37fdfd6d91028e29",
    "Create exact ephemeral verification manifest",
    "python3 scripts/verify_release_artifacts.py --contract-only",
    "committed upload manifest candidate set mismatch",
    "committed_artifacts not in (expected_blocked, expected_verified)",
    'artifact["source_sync"] = "verified-current"',
    'artifact["historical_candidate"] = None',
    'verification-manifest.json',
    '--manifest "$verification_manifest"',
    "full verifier must return exactly three candidate artifacts",
    'artifact.get("source_sync") != "verified-current"',
    'artifact.get("byte_verified") is not True',
    "python3 scripts/check_release_qa_matrix.py",
    "python3 scripts/check_store_metadata.py",
    '"manual_invocation": {',
    '"event": "workflow_dispatch"',
    '"workflow_sha": sys.argv[3]',
    '"candidate_source_revision": "fc4b6de9e28fd8956eb64462294b8bcdf405ce7e"',
    "This receipt contains identities only; no signed candidate bytes are included.",
    "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a",
    "path: ${{ runner.temp }}/nimbo-trusted-receipt/trusted-release-verification.json",
)

PAGES_REQUIRED = (
    "name: GitHub Pages",
    "  workflow_run:",
    "      - Trusted release verification",
    "      - completed",
    "  contents: read",
    "github.repository == '4810092/Weather'",
    "github.repository_id == '1329018769'",
    "github.event.workflow_run.name == 'Trusted release verification'",
    "github.event.workflow_run.path == '.github/workflows/trusted-release-verification.yml'",
    "github.event.workflow_run.conclusion == 'success'",
    "github.event.workflow_run.event == 'workflow_run'",
    "github.event.workflow_run.head_branch == 'master'",
    "github.event.workflow_run.repository.id == 1329018769",
    "github.event.workflow_run.head_repository.id == 1329018769",
    "repos/4810092/Weather/actions/runs/$NIMBO_TRUSTED_RUN_ID",
    "repos/4810092/Weather/git/ref/heads/master",
    "trusted verifier commit is stale relative to live master",
    "live master changed during Pages build",
    "live master changed before Pages deployment",
    "ref: ${{ github.event.workflow_run.head_sha }}",
    "persist-credentials: false",
    "python3 scripts/verify_release_artifacts.py --contract-only",
    "python3 scripts/check_release_qa_matrix.py --contract-only",
    "actions/upload-pages-artifact@fc324d3547104276b827a68afc52ff2a11cc49c9",
    "actions/deploy-pages@cd2ce8fcbc39b97be8ca5fce6e763baed58fa128",
)


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _single_top_level_block(text: str, key: str) -> list[str] | None:
    lines = text.splitlines()
    header = f"{key}:"
    indexes = [index for index, line in enumerate(lines) if line == header]
    if len(indexes) != 1:
        return None
    start = indexes[0] + 1
    end = len(lines)
    for index in range(start, len(lines)):
        if lines[index] and not lines[index].startswith((" ", "#")):
            end = index
            break
    block = lines[start:end]
    while block and block[-1] == "":
        block.pop()
    return block


def _single_job_block(text: str, name: str) -> str | None:
    lines = text.splitlines()
    header = f"  {name}:"
    indexes = [index for index, line in enumerate(lines) if line == header]
    if len(indexes) != 1:
        return None
    start = indexes[0]
    end = len(lines)
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if line.startswith("  ") and not line.startswith("    ") and line.endswith(":"):
            end = index
            break
    return "\n".join(lines[start:end]) + "\n"


def validate_trusted_release_workflow(text: str) -> list[str]:
    failures: list[str] = []
    if _single_top_level_block(text, "on") != ["  workflow_dispatch:"]:
        failures.append("trigger must be exactly manual workflow_dispatch without inputs")
    if text.count("permissions: {}\n") != 1 or _single_top_level_block(text, "permissions") is not None:
        failures.append("trusted workflow must deny all permissions at top level")
    stage = _single_job_block(text, "stage")
    verify = _single_job_block(text, "verify")
    if stage is None or verify is None or "  build:\n" in text or "  deploy:\n" in text:
        failures.append("trusted workflow must contain exactly stage and verify jobs")
    for marker in TRUSTED_REQUIRED:
        if marker not in text:
            failures.append(f"trusted workflow marker missing: {marker}")
    forbidden = (
        "  workflow_run:",
        "  push:",
        "  pull_request:",
        "  schedule:",
        "    inputs:",
        "pull_request_target",
        "self-hosted",
        "secrets.",
        "actions: write",
        "id-token:",
        "actions/cache",
        "gh run download",
        "/artifacts/",
        "environment:",
        "continue-on-error:",
        "tar.extract",
        "extractall(",
        "os.system(",
        "subprocess.",
    )
    for marker in forbidden:
        if marker in text:
            failures.append(f"trusted workflow contains forbidden capability: {marker}")
    if stage is not None:
        if "    permissions:\n      contents: write\n" not in stage:
            failures.append("stage permissions must be exactly contents: write")
        stage_forbidden = (
            "actions: read",
            "actions/checkout@",
            "actions/download-artifact@",
            "actions/setup-",
            "scripts/",
            "git ",
            "gh release",
            "--method",
            "-X POST",
            "-X PUT",
            "-X PATCH",
            "-X DELETE",
        )
        for marker in stage_forbidden:
            if marker in stage:
                failures.append(f"staging job contains forbidden capability: {marker}")
        if stage.count("uses:") != 1 or stage.count("actions/upload-artifact@") != 1:
            failures.append("staging job may only use the pinned upload-artifact action")
    if verify is not None:
        if "    permissions:\n      actions: read\n      contents: read\n" not in verify:
            failures.append("verify permissions must be exactly actions and contents read")
        verify_forbidden = (
            "contents: write",
            "repos/4810092/Weather/releases/",
            "gh release",
            "--method",
            "run-id:",
            "repository:",
            "github-token:",
            "merge-multiple:",
        )
        for marker in verify_forbidden:
            if marker in verify:
                failures.append(f"verification job contains forbidden capability: {marker}")
        if verify.count("actions/download-artifact@") != 1:
            failures.append("verification job must download one same-run staged artifact")
        if verify.count("actions/upload-artifact@") != 1:
            failures.append("verification job must upload one non-secret receipt")
    if text.count("github.event_name == 'workflow_dispatch'") != 2:
        failures.append("stage and verify must each require a manual invocation")
    if text.count("github.ref == 'refs/heads/master'") != 2:
        failures.append("stage and verify must each require the master ref")
    if text.count("NIMBO_WORKFLOW_SHA: ${{ github.sha }}") != 5:
        failures.append("all SHA-sensitive trusted steps must bind the manual workflow SHA")
    if text.count("repos/4810092/Weather/releases/382592451") != 2:
        failures.append("staging job must check draft release exactly before and after")
    if text.count("repos/4810092/Weather/releases/assets/544061853") != 3:
        failures.append("package asset must use only three fixed API calls")
    if text.count("repos/4810092/Weather/releases/assets/544061890") != 3:
        failures.append("receipt asset must use only three fixed API calls")
    if text.count("repos/4810092/Weather/git/ref/heads/master") != 4:
        failures.append("stage and verify must each check live master before and after")
    if text.count(
        "repos/4810092/Weather/git/matching-refs/tags/"
        "nimbo-candidate-v1.1.0-fc4b6de-run-33852229166"
    ) != 3:
        failures.append("draft storage Git tag absence must be checked twice in stage and once in verify")
    if text.count("actions/upload-artifact@") != 2:
        failures.append("only staged bytes and the non-secret receipt may be uploaded")
    if text.count("actions/download-artifact@") != 1:
        failures.append("only one same-run candidate download action is allowed")
    if text.count("actions/checkout@") != 1:
        failures.append("trusted workflow must use one pinned checkout action")
    if text.count("python3 scripts/verify_release_artifacts.py --contract-only") != 1:
        failures.append("committed blocked manifest must pass one contract-only check")
    if text.count('--manifest "$verification_manifest"') != 1:
        failures.append("full verifier must use the exact ephemeral manifest once")
    if text.count('artifact["source_sync"] = "verified-current"') != 2:
        failures.append("exact current state and ephemeral promotion must be pinned")
    if text.count('"physical_qa_evidence": None') != 3:
        failures.append("current candidate must preserve exactly three unknown runtime evidence fields")
    if 'artifact["physical_qa_evidence"]' in text:
        failures.append("ephemeral byte verification must not invent runtime QA evidence")
    if text.count('artifact["historical_candidate"] = None') != 2:
        failures.append("ephemeral manifest must clear historical state before verification")
    if text.count("set +x") != 3:
        failures.append("every token-bearing trusted step must disable shell tracing")
    if _digest(text) != TRUSTED_SHA256:
        failures.append("trusted workflow digest differs from reviewed authority")
    return failures


def validate_pages_workflow(text: str) -> list[str]:
    failures: list[str] = []
    if _single_top_level_block(text, "on") != [
        "  workflow_run:",
        "    workflows:",
        "      - Trusted release verification",
        "    types:",
        "      - completed",
    ]:
        failures.append(
            "Pages trigger must be exactly completed trusted workflow_run"
        )
    if _single_top_level_block(text, "permissions") != ["  contents: read"]:
        failures.append("Pages top-level permissions must be exactly contents: read")
    for marker in PAGES_REQUIRED:
        if marker not in text:
            failures.append(f"Pages workflow marker missing: {marker}")
    forbidden = (
        "workflow_dispatch",
        "pull_request_target",
        "self-hosted",
        "secrets.",
        "actions/cache",
        "actions/download-artifact",
        "actions/upload-artifact@",
        "NIMBO_RELEASE_ARTIFACT_ROOT",
        "NIMBO_BUNDLETOOL_JAR",
        "releases/381212810",
        "releases/assets/",
        "signed-candidate-bytes",
        "signed-candidate-receipt",
        "continue-on-error:",
    )
    for marker in forbidden:
        if marker in text:
            failures.append(f"Pages workflow contains forbidden capability: {marker}")
    if "\n  push:" in text or "\n  workflow_dispatch:" in text:
        failures.append("Pages must not have a direct push or manual trigger")
    if text.count("repos/4810092/Weather/git/ref/heads/master") != 3:
        failures.append("Pages must check live master before and after build and before deploy")
    if text.count("actions/checkout@") != 1:
        failures.append("Pages must use one pinned checkout action")
    if text.count("actions/upload-pages-artifact@") != 1:
        failures.append("Pages must upload one public site artifact")
    if text.count("actions/deploy-pages@") != 1:
        failures.append("Pages must contain one deployment action")
    if _digest(text) != PAGES_SHA256:
        failures.append("Pages workflow digest differs from reviewed authority")
    return failures


def main() -> int:
    failures: list[str] = []
    try:
        trusted = TRUSTED_WORKFLOW.read_text(encoding="utf-8")
    except OSError as error:
        failures.append(f"cannot read trusted workflow: {error}")
    else:
        failures.extend(validate_trusted_release_workflow(trusted))
    try:
        pages = PAGES_WORKFLOW.read_text(encoding="utf-8")
    except OSError as error:
        failures.append(f"cannot read Pages workflow: {error}")
    else:
        failures.extend(validate_pages_workflow(pages))
    if failures:
        for failure in failures:
            print(f"trusted release workflow security failed: {failure}", file=sys.stderr)
        return 1
    print("Trusted release and Pages workflow security checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
