#!/usr/bin/env python3
"""Reject stale or overclaimed organic featuring candidate evidence."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "growth/featuring/manifest.json"
UPLOAD_MANIFEST = ROOT / "store/upload-manifest-1.1.0.json"
GATES = ROOT / "growth/quality/gates.json"
APPLE_DRAFT = ROOT / "growth/featuring/apple-2026-09.md"
GOOGLE_DRAFT = ROOT / "growth/featuring/google-2026-09.md"

EXPECTED_INTERNAL_ACTIONS = [
    "google_play_internal_phone_vc10",
    "google_play_internal_wear_vc1000010",
    "apple_testflight_internal_build8",
    "google_play_internal_phone_vc11",
    "google_play_internal_wear_vc1000011",
    "apple_testflight_internal_build10",
]
CURRENT_EVIDENCE = [
    "store/upload-manifest-1.1.0.json",
    "growth/quality/signed-candidate-run-33852229166.md",
    "growth/quality/release-materialization-2026-09-04-run-33855931653.md",
    "growth/quality/release-artifact-source-sync-2026-09-04-fc4b6de.md",
    "growth/quality/release-artifact-full-verification-2026-09-04-build10-hosted.md",
    "growth/quality/receipts/trusted-release-verification-33859392482.json",
    "growth/quality/testflight-ios-build10-delivery-2026-09-04.md",
    "growth/quality/emulator-runtime-qa-2026-09-03.md",
    "growth/quality/google-play-internal-delivery-2026-09-03-052d12c.md",
    "growth/quality/release-artifact-full-verification-2026-09-02-build9-hosted.md",
    "growth/quality/testflight-ios-build9-background-refresh-crash-2026-09-04.md",
    "growth/quality/testflight-ios-build8-ipad-share-crash-2026-09-02.md",
    "growth/quality/internal-store-delivery-2026-09-01-8fc43b4.md",
    "growth/quality/play-delivered-android-vc10-smoke-2026-09-01.md",
    "growth/quality/testflight-ios-build8-smoke-2026-09-01.md",
]
RUNTIME_AND_RELEASE_BOUNDARIES = (
    "emulator/simulator runtime QA",
    "Google Play Internal delivery",
    "App Store review",
    "post-delivery Vitals",
    "crash close-out",
    "production release",
    "public availability",
    "rank impact",
)


def _mapping(value: Any, label: str, failures: list[str]) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    failures.append(f"{label} must be an object")
    return {}


def validate_featuring_candidate(
    manifest: dict[str, Any],
    upload: dict[str, Any],
    gates: dict[str, Any],
    apple_draft: str,
    google_draft: str,
    *,
    root: Path = ROOT,
) -> list[str]:
    failures: list[str] = []
    if manifest.get("status") != "draft-blocked":
        failures.append("featuring manifest must remain draft-blocked")
    campaign = _mapping(manifest.get("campaign"), "campaign", failures)
    if campaign.get("external_actions_performed") != EXPECTED_INTERNAL_ACTIONS:
        failures.append("internal delivery actions differ from the reviewed candidate set")
    scope = _mapping(manifest.get("scope"), "scope", failures)
    if scope.get("store_console_changes") != (
        "internal-delivery-only-no-production-or-featuring"
    ):
        failures.append("store-console boundary must name internal delivery only")
    if "Status: **DRAFT-BLOCKED — DO NOT SUBMIT**." not in apple_draft:
        failures.append("Apple draft must remain explicitly blocked")
    if "Status: **DRAFT-BLOCKED — DO NOT CREATE OR SUBMIT AN EVENT**." not in google_draft:
        failures.append("Google draft must remain explicitly blocked")

    release = upload.get("release")
    source = upload.get("source_revision")
    artifacts = _mapping(upload.get("artifacts"), "upload artifacts", failures)
    phone = _mapping(artifacts.get("android_phone"), "phone artifact", failures)
    wear = _mapping(artifacts.get("wear_os"), "Wear artifact", failures)
    apple = _mapping(artifacts.get("apple"), "Apple artifact", failures)
    if not isinstance(release, str) or not release:
        failures.append("upload release is missing")
        release = "unknown"
    if not isinstance(source, str) or len(source) != 40:
        failures.append("upload source revision is not a full commit")
        source = "unknown"
    expected_markers = {
        "Apple draft": (apple_draft, f"`{release} ({apple.get('build')})`"),
        "Google phone draft": (
            google_draft,
            f"phone `{release} ({phone.get('version_code')})`",
        ),
        "Google Wear draft": (
            google_draft,
            f"Wear OS `{release} ({wear.get('version_code')})`",
        ),
    }
    for label, (text, marker) in expected_markers.items():
        if marker not in text:
            failures.append(f"{label} does not name current upload identity {marker}")
    for label, text in (("Apple draft", apple_draft), ("Google draft", google_draft)):
        if source not in text:
            failures.append(f"{label} does not name the current source revision")
        for boundary in (
            "Production submission",
            "public availability",
            "rank impact",
        ):
            if boundary.casefold() not in text.casefold():
                failures.append(f"{label} omits boundary: {boundary}")

    verified_claims = manifest.get("verified_claims")
    if not isinstance(verified_claims, list):
        failures.append("verified_claims must be a list")
        verified_claims = []
    candidate_claims = [
        item
        for item in verified_claims
        if isinstance(item, dict) and item.get("id") == "candidate_artifact_boundary"
    ]
    if len(candidate_claims) != 1:
        failures.append("exactly one candidate_artifact_boundary claim is required")
    else:
        candidate = candidate_claims[0]
        claim = candidate.get("claim")
        evidence = candidate.get("evidence")
        if not isinstance(claim, str):
            failures.append("candidate artifact claim must be text")
            claim = ""
        for marker in (
            source,
            f"phone {release} ({phone.get('version_code')})",
            f"Wear OS {release} ({wear.get('version_code')})",
            f"Apple {release} ({apple.get('build')})",
            *RUNTIME_AND_RELEASE_BOUNDARIES,
        ):
            if marker not in claim:
                failures.append(f"candidate artifact claim omits: {marker}")
        if evidence != CURRENT_EVIDENCE:
            failures.append("candidate evidence list differs from current verified records")
        for relative in evidence if isinstance(evidence, list) else []:
            if not isinstance(relative, str) or not (root / relative).is_file():
                failures.append(f"candidate evidence file is missing: {relative}")

    gate_map = _mapping(gates.get("gates"), "quality gates", failures)
    blockers = manifest.get("blockers")
    if not isinstance(blockers, list):
        failures.append("blockers must be a list")
        blockers = []
    blocker_by_id = {
        item.get("id"): item for item in blockers if isinstance(item, dict)
    }
    for identifier in ("ios_crash_gate", "android_physical_smoke", "ios_physical_smoke"):
        gate = _mapping(gate_map.get(identifier), f"gate {identifier}", failures)
        if gate.get("status") == "pass":
            if identifier in blocker_by_id:
                failures.append(f"blocker {identifier} differs from the quality gate")
            continue
        blocker = blocker_by_id.get(identifier)
        if not isinstance(blocker, dict):
            failures.append(f"blocker {identifier} differs from the quality gate")
            continue
        if blocker.get("status") != gate.get("status"):
            failures.append(f"blocker {identifier} differs from the quality gate")
        if blocker.get("evidence") != "growth/quality/gates.json":
            failures.append(f"blocker {identifier} must cite canonical gates")
    public_release = _mapping(
        blocker_by_id.get("deliverable.candidate_public_release"),
        "public release blocker",
        failures,
    )
    if public_release.get("status") != "blocked" or public_release.get("evidence") != (
        "growth/quality/google-play-internal-delivery-2026-09-03-052d12c.md"
    ):
        failures.append("public release blocker must preserve the internal-only boundary")
    if "build 10 App Store approval or public 1.1.0 release" not in manifest.get(
        "prohibited_claims", []
    ):
        failures.append("public-release claim must remain prohibited")
    return failures


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    failures = validate_featuring_candidate(
        _load(MANIFEST),
        _load(UPLOAD_MANIFEST),
        _load(GATES),
        APPLE_DRAFT.read_text(encoding="utf-8"),
        GOOGLE_DRAFT.read_text(encoding="utf-8"),
    )
    if failures:
        for failure in failures:
            print(f"featuring candidate freshness failed: {failure}", file=sys.stderr)
        return 1
    print("Featuring candidate freshness passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
