#!/usr/bin/env python3
"""Fail-closed policy for the one-shot signed-candidate materializer."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path


WORKFLOW_SHA256 = "278d9d72ad6c995858a63f64d79279e7ebbe3d6ab86e06f937636382a0daca9e"
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
ACTION_STEP_SHA256 = "5e297e4a9c8562f204300624fd3afffbbaaabb5d9630d40332adbd3fe0e754f6"
RUN_SHA256 = {
    "Validate immutable source provenance": (
        "34160d7df1b7b33ac7174683bb252bf016963235faa26380ab2f04e99a785112"
    ),
    "Verify and stage exact candidate assets": (
        "cb7d88b7c7ee90ba74c5085630bc2565262440ed857e4e81de0d16456659e99d"
    ),
    "Create or reuse exact unpublished draft": (
        "6cad09296ef8291edc625a6e180d2bb8f2b8e491acc4e5d84e337316b3f3aa3c"
    ),
    "Upload only missing exact assets": (
        "42bba34fc071f778788aae03f5715ce7ce8066b58bde15496363a04b137f597a"
    ),
    "Verify exact unpublished materialization": (
        "fae4633da90265d10fe185eb2c367b7f8f932d6bbad416b788bd296b32158906"
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
    "36361077488",
    "10946307432",
    "345674745",
    "1329018769",
    "0faf1105cc5da072e4e9ee043c46e2e9de4f4ada",
    "9d96056de4a3f62f6a33e3528bdd965590a39ad8",
    "877ffa2656f160b4699de88020bb4952e0ffaa3ae00febdf4c1d6e85acf116d7",
    "a170d6a31aad57360ffea1f0b7263b4228bc639b87e8708c9bc0e37912707eb3",
    "b42ab34cb0a332268d45a16dbb7ebc253c782995dd1ffc0bba27ce128d755fed",
    "3f1ff98e565e46d65c7f47b01dbbded8b499e78515acc01e7dc80a0ebb7c133e",
    "5316328a69699e03acb9d149b7b9e77a0480630f0e26c10259de9f3501fa0564",
    "5fdc866094226d7cde09696e6fd2de27683af0ee6955674b3a1d29a7c203a2cd",
    "51a1d4f0a8e5b8cfa6cb6d752e1a3aad56de36749eaa6fb551039a1f429b23e4",
    "b42d0bf6a218ba1b5ed3d607a18611fbf700fadef856b02861f618411585474d",
    "nimbo-candidate-v1.1.0-0faf110-run-36361077488",
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
        "  group: release-materialization-36361077488",
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
    if text.count("matching-refs/tags/nimbo-candidate-v1.1.0-0faf110-run-36361077488") != 2:
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
