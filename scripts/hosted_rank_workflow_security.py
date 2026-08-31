#!/usr/bin/env python3
"""Fail-closed static policy for the write-capable hosted rank workflow."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/uz-rank-monitor.yml"
PINNED_ACTIONS = {
    "actions/checkout": "3d3c42e5aac5ba805825da76410c181273ba90b1",
    "actions/setup-python": "ece7cb06caefa5fff74198d8649806c4678c61a1",
    "actions/upload-artifact": "043fb46d1a93c77aae656e7c1c64a875d1fc6a0a",
    "actions/download-artifact": "3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c",
}
EXPECTED_ACTION_COUNTS = {
    "actions/checkout": 2,
    "actions/setup-python": 2,
    "actions/upload-artifact": 1,
    "actions/download-artifact": 1,
}


def _block(lines: list[str], heading: str, next_heading: str) -> list[str]:
    try:
        start = lines.index(heading)
        end = lines.index(next_heading, start + 1)
    except ValueError:
        return []
    return lines[start:end]


def validate_hosted_rank_workflow(text: str) -> list[str]:
    failures: list[str] = []
    if "\r" in text or "\t" in text or not text.endswith("\n"):
        failures.append("workflow must be canonical LF text without tabs")
    lines = text.splitlines()
    trigger = _block(lines, "on:", "permissions:")
    if trigger != [
        "on:",
        "  schedule:",
        '    - cron: "5 19 * * *"',
        "  workflow_dispatch:",
        "",
    ]:
        failures.append("trigger must be daily 19:05 UTC plus manual dispatch only")
    permissions = _block(lines, "permissions:", "concurrency:")
    if permissions != ["permissions:", "  contents: read", ""]:
        failures.append("top-level permissions must be exactly contents: read")
    concurrency = _block(lines, "concurrency:", "jobs:")
    if concurrency != [
        "concurrency:",
        "  group: nimbo-uz-rank-canonical",
        "  cancel-in-progress: false",
        "",
    ]:
        failures.append("workflow concurrency policy differs from the canonical form")

    jobs_block = text.split("\njobs:\n", 1)[1] if "\njobs:\n" in text else ""
    job_names = re.findall(r"(?m)^  ([a-z][a-z0-9-]*):$", jobs_block)
    if job_names != ["capture", "persist"]:
        failures.append("workflow must contain exactly capture and persist jobs")
    if lines.count("    if: github.ref == 'refs/heads/master'") != 1:
        failures.append("capture job must reject non-master execution")
    if lines.count(
        "    if: github.ref == 'refs/heads/master' && "
        "needs.capture.outputs.already_exists != 'true'"
    ) != 1:
        failures.append("persist job must reject non-master and canonical-day no-op")
    if text.count("      contents: write") != 1:
        failures.append("contents: write must appear only on the persist job")
    if "      actions: read\n      contents: write\n" not in text:
        failures.append("persist permissions must be actions: read and contents: write")
    if text.count("persist-credentials: false") != 1:
        failures.append("capture checkout must not retain credentials")
    if text.count("persist-credentials: true") != 1:
        failures.append("only persist checkout may retain the push credential")

    uses = re.findall(r"(?m)^\s*- uses: ([^\s]+)$", text)
    for action, revision in PINNED_ACTIONS.items():
        expected = f"{action}@{revision}"
        if uses.count(expected) != EXPECTED_ACTION_COUNTS[action]:
            failures.append(f"action count or pin differs for {action}")
    for use in uses:
        if re.fullmatch(r"[^@\s]+@[0-9a-f]{40}", use) is None:
            failures.append(f"action is not pinned to a full commit: {use}")
        action = use.rsplit("@", 1)[0]
        if action not in PINNED_ACTIONS:
            failures.append(f"unreviewed action is forbidden: {action}")

    forbidden = (
        "pull_request:",
        "push:\n",
        "secrets.",
        "continue-on-error",
        "write-all",
        "--replace",
        "git push --force",
        "git push -f",
        "pull-requests: write",
        "issues: write",
    )
    for marker in forbidden:
        if marker in text:
            failures.append(f"forbidden workflow construct: {marker}")

    required_counts = {
        "NIMBO_STATE_BRANCH: growth-observations": 4,
        "python3 scripts/growth/monitor_public_rank.py": 1,
        "hosted_rank_state.py prepare-history": 0,
        "hosted_rank_state.py build-bundle": 1,
        "hosted_rank_state.py validate-bundle": 1,
        "hosted_rank_state.py install-bundle": 1,
        "--date \"$NIMBO_LOCAL_DATE\"": 5,
        "diff --cached --diff-filter=A": 1,
        "hash-object --no-filters": 1,
        "Canonical unknown evidence was persisted; failing closed.": 1,
        "--allow-existing-date": 1,
        "already_exists: ${{ steps.history.outputs.already_exists }}": 1,
        "echo \"already_exists=$already_exists\" >> \"$GITHUB_OUTPUT\"": 1,
        "if: steps.history.outputs.already_exists != 'true'": 3,
    }
    for marker, expected_count in required_counts.items():
        if marker == "hosted_rank_state.py prepare-history":
            # prepare-history is passed as an array argument, never shell-expanded.
            continue
        if text.count(marker) != expected_count:
            failures.append(f"workflow contract marker count differs: {marker}")
    if text.count("            prepare-history") != 1:
        failures.append("prepare-history must be invoked exactly once")
    if text.count("set +e") != 1:
        failures.append("only the monitor decision may temporarily disable errexit")
    if text.count("refs/heads/$NIMBO_STATE_BRANCH") < 6:
        failures.append("state reads and push must use the fixed observation branch")
    if "HEAD:refs/heads/$NIMBO_STATE_BRANCH" not in text:
        failures.append("state push destination differs from the fixed branch")
    if "git -C \"$state_root\" push origin" not in text:
        failures.append("state transition must use one explicit non-force push")
    push_index = text.find("git -C \"$state_root\" push origin")
    unknown_index = text.find(
        "Canonical unknown evidence was persisted; failing closed."
    )
    if push_index < 0 or unknown_index < push_index:
        failures.append("unknown evidence must fail only after immutable persistence")
    if re.search(r"state-(?:read|write)[^\n]*scripts/", text):
        failures.append("code from the mutable observation branch must never execute")
    return failures


def main() -> int:
    failures = validate_hosted_rank_workflow(WORKFLOW.read_text(encoding="utf-8"))
    if failures:
        for failure in failures:
            print(f"hosted rank workflow rejected: {failure}", file=sys.stderr)
        return 1
    print("Hosted rank workflow security policy passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
