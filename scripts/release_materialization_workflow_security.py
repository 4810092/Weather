#!/usr/bin/env python3
"""Fail-closed policy for the one-shot signed-candidate materializer."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path


WORKFLOW_SHA256 = "1b7106c582dbfd21b0a60336bb44a151dad240b0a2a3a0b06ddc619d54f0628d"
REPOSITORY_GUARD = (
    "github.repository == '4810092/Weather' && "
    "github.repository_id == '1329018769' && "
    "github.ref == 'refs/heads/master'"
)
DOWNLOAD_ACTION = (
    "actions/download-artifact@"
    "3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c"
)
STEP_INVENTORY = [
    ("name", "Validate immutable source provenance"),
    ("uses", DOWNLOAD_ACTION),
    ("name", "Verify and stage exact candidate assets"),
    ("name", "Create or reuse exact unpublished draft"),
    ("name", "Upload only missing exact assets"),
    ("name", "Verify exact unpublished materialization"),
]
ACTION_STEP_SHA256 = (
    "03ed1d5f833b8feeffefe0908d31e4e64612fee0d4c2d6418e5d516178a5f19a"
)
RUN_SHA256 = {
    "Validate immutable source provenance": (
        "25c6db43e37f12ff65775fccf8532a43f8b635026f82de8b5bccaeb0f184b676"
    ),
    "Verify and stage exact candidate assets": (
        "c0cae5b2efac65bb6a7bae5b03672d2f20da2208ed4c8a6c389f8e8082a3bde9"
    ),
    "Create or reuse exact unpublished draft": (
        "2c75f23973a5312e856a7be4e0c4f0b408edd18426c578a01ba58efe35cb6198"
    ),
    "Upload only missing exact assets": (
        "48d4d895554c9186b6217f01f9f20f301826b3bce5f2cf927091a17c2caa7950"
    ),
    "Verify exact unpublished materialization": (
        "0d605a6c6ec09935aae431f53db51f03cf89f23788a2450f82f06fc79d42667a"
    ),
}
TOKEN_STEP_ENVS = {
    "Validate immutable source provenance": [
        "        env:",
        "          GH_TOKEN: ${{ github.token }}",
    ],
    "Create or reuse exact unpublished draft": [
        "        env:",
        "          GH_TOKEN: ${{ github.token }}",
    ],
    "Upload only missing exact assets": [
        "        env:",
        "          GH_TOKEN: ${{ github.token }}",
        "          NIMBO_RELEASE_ID: ${{ steps.release.outputs.release_id }}",
    ],
    "Verify exact unpublished materialization": [
        "        env:",
        "          GH_TOKEN: ${{ github.token }}",
        "          NIMBO_RELEASE_ID: ${{ steps.release.outputs.release_id }}",
    ],
}
REQUIRED_MARKERS = (
    "33381050098",
    "9754332100",
    "345674745",
    "1329018769",
    "2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652",
    "dd6e275e840947ec6b22b9485ebeb63d5eaa320c",
    "fd96eb999047cc033beb211eb09761dbbe68ec341dc9f3cf5902adfadfdebc55",
    "f1754ff767d908cd6be5ce5652e05e6f3dc8721ffa1b0db303d72a5d27cf5478",
    "60c827ef9f5d2cdc51add5344bd33ab780ab1be3154a3f3da8c22074ddb518d9",
    "c852c61e07289d2a7a8f211efc91d7f30fab2c3475465ba000625780a21de19c",
    "c91ea40ae12fd59aacfee77f03ba75240951b5797c16b23487ce334eb85502fa",
    "d4a90676f32745ea314b50ced2c9955e86923589534a1a7654ac6f1207e88a62",
    "e76d685b20e86f8878be7c9a1a59ac6edb5781ec8e61d5ecd36feb52ddc1cccf",
    "7466afb1a06f3000ad5d095734082d57cf58e992bdd7a8bed326e90d26ba39d0",
    "nimbo-candidate-v1.1.0-2cdd438-run-33381050098",
    "Internal artifact storage only. Do not publish.",
    '"draft": True',
    '"prerelease": True',
    'payload["generate_release_notes"] = False',
    'payload["make_latest"] = "false"',
    '"target_commitish": os.environ["GITHUB_SHA"]',
    "len(package_members) != 192",
    "candidate package regular-file count mismatch",
    "candidate package directory count mismatch",
    "unsafe candidate package member",
    "candidate draft asset name set mismatch",
    'release.get("published_at") is not None',
    "candidate storage tag already exists",
    "draft materialization unexpectedly created a Git tag",
    "existing candidate asset mismatch",
    "candidate draft asset count mismatch",
    "sha256sum --check --strict",
)


def _top_level_block(lines: list[str], key: str) -> list[str] | None:
    header = f"{key}:"
    matches = [index for index, line in enumerate(lines) if line == header]
    if len(matches) != 1:
        return None
    start = matches[0] + 1
    end = len(lines)
    for index in range(start, len(lines)):
        line = lines[index]
        if line and not line.startswith((" ", "#")):
            end = index
            break
    return lines[start:end]


def _job_blocks(lines: list[str]) -> tuple[list[str], dict[str, list[str]]]:
    jobs = _top_level_block(lines, "jobs")
    if jobs is None:
        return [], {}
    headers: list[tuple[int, str]] = []
    for index, line in enumerate(jobs):
        match = re.fullmatch(r"  ([a-z][a-z0-9-]*):", line)
        if match:
            headers.append((index, match.group(1)))
    names: list[str] = []
    result: dict[str, list[str]] = {}
    for position, (index, name) in enumerate(headers):
        end = headers[position + 1][0] if position + 1 < len(headers) else len(jobs)
        names.append(name)
        result[name] = jobs[index + 1 : end]
    return names, result


def _step_block(job: list[str], name: str) -> list[str] | None:
    header = f"      - name: {name}"
    matches = [index for index, line in enumerate(job) if line == header]
    if len(matches) != 1:
        return None
    start = matches[0]
    end = len(job)
    for index in range(start + 1, len(job)):
        if job[index].startswith("      - "):
            end = index
            break
    return job[start:end]


def _literal_run(step: list[str]) -> list[str] | None:
    matches = [index for index, line in enumerate(step) if line == "        run: |"]
    if len(matches) != 1:
        return None
    return [line[10:] for line in step[matches[0] + 1 :] if line.strip()]


def _step_env_block(step: list[str]) -> list[str] | None:
    matches = [index for index, line in enumerate(step) if line == "        env:"]
    if len(matches) != 1:
        return None
    start = matches[0]
    end = start + 1
    while end < len(step) and step[end].startswith("          "):
        end += 1
    return step[start:end]


def _step_inventory(job: list[str]) -> list[tuple[str, str]]:
    inventory: list[tuple[str, str]] = []
    for line in job:
        uses = re.fullmatch(r"      - uses: ([^\s#]+)", line)
        name = re.fullmatch(r"      - name: (.+)", line)
        if uses:
            inventory.append(("uses", uses.group(1)))
        elif name:
            inventory.append(("name", name.group(1)))
        elif line.startswith("      - "):
            inventory.append(("invalid", line.strip()))
    return inventory


def validate_release_materialization_workflow(text: str) -> list[str]:
    failures: list[str] = []
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != WORKFLOW_SHA256:
        failures.append("workflow bytes differ from the reviewed materialization policy")
    if text.startswith("\ufeff") or "\x00" in text or "\r" in text or "\t" in text:
        failures.append("workflow must use canonical UTF-8 LF text without tabs")
    lines = text.splitlines()
    yaml_policy_lines = "\n".join(
        line for line in lines if len(line) - len(line.lstrip(" ")) <= 8
    )
    if re.search(r"(?m)^\s*(?:<<:|[^#\n]*:\s*[\[{])", yaml_policy_lines):
        failures.append("flow mappings/lists and YAML merge keys are forbidden")
    if re.search(
        r"(?m)(?:^|\s)[&*][A-Za-z_][A-Za-z0-9_-]*", yaml_policy_lines
    ):
        failures.append("YAML anchors and aliases are forbidden")

    top_level_keys = [
        match.group(1)
        for line in lines
        if (match := re.fullmatch(r"([a-z][a-z0-9_-]*):(?:.*)?", line))
    ]
    if top_level_keys != ["name", "on", "permissions", "concurrency", "jobs"]:
        failures.append("top-level workflow keys or order differ from policy")
    if _top_level_block(lines, "on") != ["  workflow_dispatch:", ""]:
        failures.append("trigger must be exactly manual workflow_dispatch")
    if _top_level_block(lines, "permissions") != [
        "  actions: read",
        "  contents: write",
        "",
    ]:
        failures.append("permissions must be exactly actions read and contents write")
    if _top_level_block(lines, "concurrency") != [
        "  group: release-materialization-33381050098",
        "  cancel-in-progress: false",
        "",
    ]:
        failures.append("concurrency policy differs from the exact candidate lock")

    job_names, jobs = _job_blocks(lines)
    if job_names != ["materialize"]:
        failures.append("workflow must contain exactly one materialize job")
        return failures
    job = jobs["materialize"]
    if _step_inventory(job) != STEP_INVENTORY:
        failures.append("materialization step inventory differs from policy")
    if f"    if: {REPOSITORY_GUARD}" not in job:
        failures.append("materialization job lacks the exact repository/id/master guard")
    if job.count("    runs-on: ubuntu-24.04") != 1 or "self-hosted" in text:
        failures.append("materialization must use only standard ubuntu-24.04")
    if job.count("    timeout-minutes: 15") != 1:
        failures.append("materialization timeout differs from policy")
    if any(line.startswith("    permissions:") for line in job):
        failures.append("materialization job must not override token permissions")
    if any(line.startswith("    environment:") for line in job):
        failures.append("materialization job must not gain environment secrets")

    action_starts = [
        index for index, line in enumerate(job) if line.startswith("      - uses:")
    ]
    if len(action_starts) != 1:
        failures.append("materialization must use exactly one pinned action")
    else:
        start = action_starts[0]
        end = next(
            (index for index in range(start + 1, len(job)) if job[index].startswith("      - ")),
            len(job),
        )
        action_step = job[start:end]
        action_digest = hashlib.sha256(
            ("\n".join(action_step) + "\n").encode("utf-8")
        ).hexdigest()
        if action_digest != ACTION_STEP_SHA256:
            failures.append("download action block differs from exact ID/run policy")
        if action_step[0] != f"      - uses: {DOWNLOAD_ACTION}":
            failures.append("download action is not pinned to its approved commit")
    if text.count("uses:") != 1 or "actions/checkout" in text:
        failures.append("only the exact download action is permitted")

    for step_name, expected_digest in RUN_SHA256.items():
        step = _step_block(job, step_name)
        if step is None:
            failures.append(f"required materialization step missing: {step_name}")
            continue
        if step.count("        shell: bash") != 1 or any(
            line.startswith("        shell:") and line != "        shell: bash"
            for line in step
        ):
            failures.append(f"materialization shell differs from policy: {step_name}")
        run = _literal_run(step)
        digest = (
            hashlib.sha256(("\n".join(run) + "\n").encode("utf-8")).hexdigest()
            if run is not None
            else None
        )
        if digest != expected_digest:
            failures.append(f"materialization run block differs from policy: {step_name}")
        expected_env = TOKEN_STEP_ENVS.get(step_name)
        actual_env = _step_env_block(step)
        if expected_env is None and actual_env is not None:
            failures.append(f"non-token step has an environment block: {step_name}")
        if expected_env is not None and actual_env != expected_env:
            failures.append(f"token step env differs from policy: {step_name}")
        if expected_env is not None and (run is None or run[:2] != [
            "set +x",
            "set -euo pipefail",
        ]):
            failures.append(f"token step must disable xtrace first: {step_name}")

    if text.count("${{ github.token }}") != 5:
        failures.append("GITHUB_TOKEN binding inventory differs from policy")
    if "secrets." in text or "secrets[" in text or "toJSON(secrets" in text:
        failures.append("repository or environment secrets are forbidden")
    if "NIMBO_ANDROID_" in text or "NIMBO_APPLE_" in text:
        failures.append("signing material must never enter the materialization workflow")
    if "continue-on-error:" in text or "if: always()" in text:
        failures.append("error suppression is forbidden")
    if re.search(r"(?mi)^\s*set\s+-[^\n]*x", text) or re.search(
        r"(?mi)\bxtrace\b", text
    ):
        failures.append("shell tracing is forbidden")

    forbidden_mutations = (
        "gh release create",
        "gh release upload",
        "--clobber",
        "--method PATCH",
        "--method DELETE",
        "--request PATCH",
        "--request DELETE",
        '"draft": False',
        '"prerelease": False',
        'payload["make_latest"] = "true"',
        "actions: write",
        "id-token: write",
        "packages: write",
    )
    for forbidden in forbidden_mutations:
        if forbidden in text:
            failures.append(f"forbidden publication or privilege construct: {forbidden}")
    if "extractall" in text or re.search(r"(?m)^\s*(?:eval|source)\s", text):
        failures.append("downloaded candidate content must never be executed or bulk-extracted")
    if text.count("https://uploads.github.com/repos/4810092/Weather/releases/") != 1:
        failures.append("release upload endpoint inventory differs from policy")
    if text.count("matching-refs/tags/nimbo-candidate-v1.1.0-2cdd438-run-33381050098") != 2:
        failures.append("candidate Git-tag absence must be checked before and after")
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"materialization contract marker is missing: {marker}")
    return failures


def main() -> int:
    path = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else Path(__file__).resolve().parents[1]
        / ".github/workflows/release-materialization.yml"
    )
    failures = validate_release_materialization_workflow(path.read_text(encoding="utf-8"))
    for failure in failures:
        print(f"release materialization workflow check failed: {failure}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
