#!/usr/bin/env python3
"""Validate the blocked, single-variable UZ ASO experiment draft."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_PATH = ROOT / "growth/experiments/growth-2026-09-uz-query-headline.json"
METADATA_PATH = ROOT / "store/metadata.json"
GATES_PATH = ROOT / "growth/quality/gates.json"

TOP_FIELDS = {
    "schema_version",
    "id",
    "status",
    "objective",
    "storefront",
    "single_variable",
    "product_source_revision",
    "metadata_source",
    "evidence_refs",
    "approved_intent_terms",
    "activation",
    "current_blockers",
    "surfaces",
    "analysis_plan",
    "forbidden_actions",
    "negative_claims",
    "external_mutation_performed",
}
ACTIVATION_FIELDS = {
    "required_gate_statuses",
    "required_scale_status",
    "minimum_weekly_store_visitors",
    "observed_weekly_store_visitors",
    "public_release_verified",
    "current_storefront_recheck_verified",
    "explicit_action_authorization_at_activation_required",
    "activation_ready",
}
SURFACE_FIELDS = {
    "id",
    "platform",
    "listing_id",
    "locale",
    "field",
    "control",
    "variant",
    "control_characters",
    "variant_characters",
    "maximum_characters",
    "required_intent_terms",
    "unchanged_fields_sha256",
    "scope_limit",
    "claim_source_refs",
}
ANALYSIS_FIELDS = {
    "unit_of_analysis",
    "primary_metric",
    "secondary_metric",
    "minimum_complete_days",
    "decision_rule",
    "pool_platforms",
    "pool_locales",
    "paid_traffic",
    "incentivized_activity",
}
EXPECTED_SURFACES = {
    ("app-store", "app-store-default", "en-GB"),
    ("app-store", "app-store-default", "ru-RU"),
    ("google-play", "google-play-uz-country-listing", "en-US"),
    ("google-play", "google-play-uz-country-listing", "ru-RU"),
}
ALLOWED_VARIANT_TOKENS = {"nimbo", "toshkent", "ob-havo", "погода", "ташкент"}
REQUIRED_FORBIDDEN_ACTIONS = {
    "publish_metadata",
    "submit_review",
    "start_store_experiment",
    "send_outreach",
    "paid_acquisition",
    "incentivized_installs_or_reviews",
}


def _sha256_json(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _listing(metadata: dict[str, Any], listing_id: str) -> dict[str, Any] | None:
    for listing in metadata.get("listings", []):
        if isinstance(listing, dict) and listing.get("id") == listing_id:
            return listing
    return None


def _resolved_copy(
    metadata: dict[str, Any], platform: str, listing_id: str, locale: str
) -> dict[str, Any] | None:
    listing = _listing(metadata, listing_id)
    if listing is None or listing.get("platform") != platform:
        return None
    if platform == "app-store":
        base = metadata.get("localizations", {}).get(locale)
        if not isinstance(base, dict):
            return None
        resolved = dict(base)
        override = listing.get("overrides", {}).get(locale, {})
        if not isinstance(override, dict):
            return None
        resolved.update(override)
        return resolved
    custom = listing.get("custom_listing")
    if not isinstance(custom, dict):
        return None
    copy = custom.get("localizations", {}).get(locale)
    return dict(copy) if isinstance(copy, dict) else None


def _path_exists(root: Path, value: Any) -> bool:
    return isinstance(value, str) and bool(value) and (root / value).is_file()


def validate_aso_experiment(
    experiment: dict[str, Any],
    metadata: dict[str, Any],
    gates_payload: dict[str, Any],
    root: Path = ROOT,
) -> list[str]:
    failures: list[str] = []
    if set(experiment) != TOP_FIELDS:
        failures.append("experiment must contain the exact top-level contract")
        return failures
    if experiment.get("schema_version") != 1:
        failures.append("schema_version must be 1")
    if experiment.get("id") != "growth-2026-09-uz-query-headline":
        failures.append("unexpected experiment id")
    if experiment.get("status") != "draft-blocked":
        failures.append("repository experiment must remain draft-blocked")
    if experiment.get("storefront") != "UZ":
        failures.append("experiment storefront must be UZ")
    if experiment.get("single_variable") != "title":
        failures.append("the only experiment variable must be title")
    if experiment.get("external_mutation_performed") is not False:
        failures.append("external_mutation_performed must remain false")
    if experiment.get("metadata_source") != "store/metadata.json":
        failures.append("metadata_source must use canonical store metadata")

    refs = experiment.get("evidence_refs")
    if not isinstance(refs, list) or not refs or any(
        not _path_exists(root, value) for value in refs
    ):
        failures.append("every evidence_ref must resolve to a repository file")

    approved_terms = experiment.get("approved_intent_terms")
    if not isinstance(approved_terms, list) or len(set(approved_terms)) != len(
        approved_terms
    ):
        failures.append("approved_intent_terms must be a unique array")
        approved_terms = []
    approved_casefold = {str(value).casefold() for value in approved_terms}

    gates = gates_payload.get("gates")
    if not isinstance(gates, dict):
        failures.append("quality gates must be an object")
        gates = {}
    activation = experiment.get("activation")
    if not isinstance(activation, dict) or set(activation) != ACTIVATION_FIELDS:
        failures.append("activation must contain the exact fail-closed contract")
        activation = {}
    blocking_gate_ids = {
        gate_id
        for gate_id, gate in gates.items()
        if isinstance(gate, dict) and gate.get("blocks_publication") is True
    }
    required_statuses = activation.get("required_gate_statuses")
    if not isinstance(required_statuses, dict) or set(required_statuses) != blocking_gate_ids:
        failures.append("activation must require every publication-blocking gate")
        required_statuses = {}
    if any(value != "pass" for value in required_statuses.values()):
        failures.append("every required gate status must be pass")
    if activation.get("required_scale_status") != "scale":
        failures.append("activation must require scale status")
    minimum_visitors = activation.get("minimum_weekly_store_visitors")
    if not isinstance(minimum_visitors, int) or minimum_visitors < 500:
        failures.append("weekly visitor threshold must be at least 500")
    if activation.get("observed_weekly_store_visitors") is not None:
        failures.append("unobserved weekly traffic must remain null")
    for field in ("public_release_verified", "current_storefront_recheck_verified"):
        if activation.get(field) is not False:
            failures.append(f"{field} must remain false until separately verified")
    if activation.get("explicit_action_authorization_at_activation_required") is not True:
        failures.append("activation must require explicit action-time authorization")
    if activation.get("activation_ready") is not False:
        failures.append("a repository draft cannot infer activation readiness")

    expected_blockers = sorted(
        [
            gate_id
            for gate_id, gate in gates.items()
            if isinstance(gate, dict)
            and gate.get("blocks_publication") is True
            and gate.get("status") != "pass"
        ]
        + ([f"scale_status:{gates_payload.get('scale_status')}"] if gates_payload.get("scale_status") != "scale" else [])
        + [
            "public_release_unverified",
            "weekly_traffic_unknown",
            "storefront_recheck_unverified",
        ]
    )
    blockers = experiment.get("current_blockers")
    if not isinstance(blockers, list) or sorted(blockers) != expected_blockers:
        failures.append("current_blockers must match canonical fail-closed state")

    surfaces = experiment.get("surfaces")
    if not isinstance(surfaces, list):
        failures.append("surfaces must be an array")
        surfaces = []
    identities: set[tuple[str, str, str]] = set()
    ids: set[str] = set()
    for index, surface in enumerate(surfaces):
        owner = f"surfaces[{index}]"
        if not isinstance(surface, dict) or set(surface) != SURFACE_FIELDS:
            failures.append(f"{owner} must contain the exact surface contract")
            continue
        surface_id = surface.get("id")
        if not isinstance(surface_id, str) or surface_id in ids:
            failures.append(f"{owner} id must be unique")
        ids.add(str(surface_id))
        identity = (
            str(surface.get("platform")),
            str(surface.get("listing_id")),
            str(surface.get("locale")),
        )
        if identity in identities:
            failures.append(f"{owner} duplicates a platform/listing/locale")
        identities.add(identity)
        if surface.get("field") != experiment.get("single_variable"):
            failures.append(f"{owner} changes a field outside the single variable")
        copy = _resolved_copy(metadata, *identity)
        if copy is None:
            failures.append(f"{owner} cannot resolve canonical listing copy")
            continue
        control = surface.get("control")
        variant = surface.get("variant")
        if copy.get("title") != control:
            failures.append(f"{owner} control differs from canonical metadata")
        if not isinstance(variant, str) or variant == control:
            failures.append(f"{owner} variant must differ from control")
            variant = ""
        if surface.get("control_characters") != len(str(control)):
            failures.append(f"{owner} control character count mismatch")
        if surface.get("variant_characters") != len(variant):
            failures.append(f"{owner} variant character count mismatch")
        if surface.get("maximum_characters") != 30 or len(variant) > 30:
            failures.append(f"{owner} title exceeds the 30-character contract")
        tokens = {
            token.casefold()
            for token in re.findall(r"[^\W_]+(?:-[^\W_]+)*", variant, re.UNICODE)
        }
        if not tokens or not tokens.issubset(ALLOWED_VARIANT_TOKENS):
            failures.append(f"{owner} variant uses an unapproved title token")
        required_terms = surface.get("required_intent_terms")
        if not isinstance(required_terms, list) or not required_terms:
            failures.append(f"{owner} requires explicit intent terms")
            required_terms = []
        if any(str(term).casefold() not in approved_casefold for term in required_terms):
            failures.append(f"{owner} references an unapproved intent term")
        if any(str(term).casefold() not in variant.casefold() for term in required_terms):
            failures.append(f"{owner} variant omits a required intent term")
        unchanged = dict(copy)
        unchanged.pop("title", None)
        if surface.get("unchanged_fields_sha256") != _sha256_json(unchanged):
            failures.append(f"{owner} non-title control fields drifted")
        limit = surface.get("scope_limit")
        if not isinstance(limit, str) or not limit.strip():
            failures.append(f"{owner} requires a scope limitation")
        elif identity[0] == "app-store" and "not a UZ-only" not in limit:
            failures.append(f"{owner} must disclose Apple global-localization scope")
        claim_refs = surface.get("claim_source_refs")
        if not isinstance(claim_refs, list) or not claim_refs or any(
            not _path_exists(root, value) for value in claim_refs
        ):
            failures.append(f"{owner} claim sources must resolve")
    if identities != EXPECTED_SURFACES:
        failures.append("surfaces must cover the exact Apple and Google UZ locale set")

    analysis = experiment.get("analysis_plan")
    if not isinstance(analysis, dict) or set(analysis) != ANALYSIS_FIELDS:
        failures.append("analysis_plan must contain the exact contract")
    else:
        if analysis.get("unit_of_analysis") != "platform-locale":
            failures.append("analysis cannot pool platform or locale units")
        if analysis.get("minimum_complete_days", 0) < 14:
            failures.append("analysis requires at least 14 complete days")
        for field in ("pool_platforms", "pool_locales", "paid_traffic", "incentivized_activity"):
            if analysis.get(field) is not False:
                failures.append(f"analysis_plan.{field} must be false")
    forbidden = experiment.get("forbidden_actions")
    if not isinstance(forbidden, list) or set(forbidden) != REQUIRED_FORBIDDEN_ACTIONS:
        failures.append("forbidden_actions must preserve every external-action boundary")
    negative_claims = experiment.get("negative_claims")
    if not isinstance(negative_claims, list) or len(negative_claims) < 4:
        failures.append("negative_claims must preserve all non-claims")
    return failures


def main() -> int:
    experiment = json.loads(EXPERIMENT_PATH.read_text(encoding="utf-8"))
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    gates = json.loads(GATES_PATH.read_text(encoding="utf-8"))
    failures = validate_aso_experiment(experiment, metadata, gates)
    if failures:
        for failure in failures:
            print(f"ASO experiment check failed: {failure}")
        return 1
    print("ASO experiment check passed: draft-blocked, title-only, organic-only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
