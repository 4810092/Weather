#!/usr/bin/env python3
"""Fail-closed static policy for the Google Play vitals read-only workflow."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/google-play-vitals-readonly.yml"
PINNED_ACTIONS = {
    "actions/checkout": "3d3c42e5aac5ba805825da76410c181273ba90b1",
    "google-github-actions/auth": "7c6bc770dae815cd3e89ee6cdf493a5fab2cc093",  # gitleaks:allow -- pinned action commit
    "actions/upload-artifact": "043fb46d1a93c77aae656e7c1c64a875d1fc6a0a",
}


def validate_google_play_vitals_workflow(text: str) -> list[str]:
    failures: list[str] = []
    if "\r" in text or "\t" in text or not text.endswith("\n"):
        failures.append("workflow must be canonical LF text without tabs")
    if not text.startswith("name: Google Play vitals read-only evidence\n\non:\n  workflow_dispatch:\n"):
        failures.append("trigger must be manual workflow_dispatch only")
    if "\npermissions:\n  contents: read\n\nconcurrency:\n" not in text:
        failures.append("top-level permissions must be exactly contents: read")
    if text.count("  workflow_dispatch:") != 1 or any(
        marker in text for marker in ("pull_request:", "push:\n", "schedule:")
    ):
        failures.append("automatic or repository-event triggers are forbidden")
    required_input = (
        "      week_end:\n"
        "        description: Inclusive complete Google Play day (YYYY-MM-DD, America/Los_Angeles)\n"
        "        required: true\n"
        "        type: string\n"
    )
    if text.count(required_input) != 1:
        failures.append("one required week_end input is mandatory")

    jobs_block = text.split("\njobs:\n", 1)[1] if "\njobs:\n" in text else ""
    if re.findall(r"(?m)^  ([a-z][a-z0-9-]*):$", jobs_block) != ["export"]:
        failures.append("workflow must contain exactly one export job")
    exact_if = (
        "    if: github.repository == '4810092/Weather' && "
        "github.ref == 'refs/heads/master' && "
        "vars.NIMBO_GOOGLE_WIF_PROVIDER != '' && "
        "vars.NIMBO_GOOGLE_WIF_SERVICE_ACCOUNT != ''\n"
    )
    if text.count(exact_if) != 1:
        failures.append("job must be fixed to the canonical repository and master")
    if text.count("      contents: read\n      id-token: write\n") != 1:
        failures.append("job permissions must be contents read plus OIDC only")
    if "    environment: store-readonly\n" not in text:
        failures.append("store-readonly environment protection is mandatory")
    if text.count("persist-credentials: false") != 1:
        failures.append("checkout must not retain Git credentials")

    uses = re.findall(r"(?m)^\s+(?:- )?uses: ([^\s]+)$", text)
    expected_uses = [f"{action}@{revision}" for action, revision in PINNED_ACTIONS.items()]
    if uses != expected_uses:
        failures.append("actions must exactly match reviewed full-commit pins")
    for use in uses:
        if re.fullmatch(r"[^@\s]+@[0-9a-f]{40}", use) is None:
            failures.append(f"action is not pinned to a full commit: {use}")

    required_counts = {
        "token_format: access_token": 1,
        "access_token_lifetime: 600s": 1,
        "access_token_scopes: https://www.googleapis.com/auth/playdeveloperreporting": 1,
        "create_credentials_file: false": 1,
        "NIMBO_GOOGLE_PLAY_REPORTING_ACCESS_TOKEN: ${{ steps.google-auth.outputs.access_token }}": 1,
        "python3 -I scripts/google-play-vitals-readonly-probe.py": 1,
        "python3 -I scripts/growth/import_weekly.py": 1,
        'evidence="$RUNNER_TEMP/google-play-vitals-$NIMBO_WEEK_END.csv"': 1,
        'normalized="$RUNNER_TEMP/google-play-vitals-$NIMBO_WEEK_END.json"': 1,
        "if-no-files-found: error": 1,
    }
    for marker, expected in required_counts.items():
        if text.count(marker) != expected:
            failures.append(f"workflow contract marker count differs: {marker}")

    forbidden = (
        "contents: write",
        "actions: write",
        "packages: write",
        "pull-requests: write",
        "issues: write",
        "write-all",
        "continue-on-error",
        "androidpublisher",
        "APP_TESTERS",
        "SERVICE_ACCOUNT_JSON",
        "create_credentials_file: true",
        "curl ",
        "wget ",
        "gh ",
        "git ",
        "--replace",
    )
    for marker in forbidden:
        if marker in text:
            failures.append(f"forbidden workflow construct: {marker}")
    return failures


def main() -> int:
    failures = validate_google_play_vitals_workflow(
        WORKFLOW.read_text(encoding="utf-8")
    )
    if failures:
        for failure in failures:
            print(f"Google Play vitals workflow rejected: {failure}", file=sys.stderr)
        return 1
    print("Google Play vitals read-only workflow security policy passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
