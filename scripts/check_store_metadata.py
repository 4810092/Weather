#!/usr/bin/env python3
"""Validate versioned store listings, locale copy, experiments, and URLs."""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_LOCALES = {
    "en-US",
    "ru-RU",
    "ar",
    "es-ES",
    "fr-FR",
    "de-DE",
    "pt-PT",
    "zh-CN",
    "ja-JP",
    "ko-KR",
    "hi-IN",
    "tr-TR",
    "uz-UZ",
}
TOP_LEVEL_FIELDS = {
    "$schema",
    "schema_version",
    "metadata_revision",
    "product",
    "localizations",
    "creative_sets",
    "experiments",
    "listings",
}
LOCALIZATION_LIMITS = {
    "title": 30,
    "subtitle": 30,
    "short_description": 80,
    "keywords": 100,
    "description": 4000,
    "release_notes": 500,
}
LISTING_FIELDS = {
    "id",
    "platform",
    "storefront",
    "listing_type",
    "localization_refs",
    "overrides",
    "custom_listing",
    "custom_product_page",
    "creative_set",
    "experiment",
    "marketing_url",
    "support_url",
    "privacy_url",
}
PLATFORMS = {"app-store", "google-play"}
LISTING_TYPES = {"default", "custom-listing", "custom-product-page"}
UZ_TITLE = "Nimbo: Ob-havo va prognoz"
UZ_SHORT = "Tashqariga chiqish uchun eng yaxshi vaqtni toping."
EXPECTED_PUBLIC_URLS = {
    "marketing": "https://nimbo.uz/",
    "support": "https://nimbo.uz/support/",
    "privacy": "https://nimbo.uz/privacy/",
}
EXPECTED_SCHEMA_ID = "https://nimbo.uz/schemas/store-metadata-v2.json"
SEMANTIC_VERSION = re.compile(r"^\d+\.\d+\.\d+$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
ARTIFACT_NAMES = {"android_phone", "wear_os", "apple"}


def is_https_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def validate_text_fields(
    owner: str,
    fields: object,
    limits: dict[str, int],
    failures: list[str],
    *,
    exact: bool = True,
) -> None:
    if not isinstance(fields, dict):
        failures.append(f"{owner}: expected an object")
        return
    if exact and set(fields) != set(limits):
        failures.append(f"{owner}: expected exactly {sorted(limits)}")
        return
    for field, value in fields.items():
        if field not in limits:
            failures.append(f"{owner}:{field}: unsupported field")
            continue
        if not isinstance(value, str) or not value.strip():
            failures.append(f"{owner}:{field}: empty or not a string")
            continue
        if len(value) > limits[field]:
            failures.append(f"{owner}:{field}: {len(value)} > {limits[field]}")


def read_source_integer(
    relative_path: str,
    pattern: str,
    owner: str,
    failures: list[str],
) -> int | None:
    content = (ROOT / relative_path).read_text(encoding="utf-8")
    match = re.search(pattern, content)
    if match is None:
        failures.append(f"{owner}: source identity could not be read")
        return None
    return int(match.group(1).replace("_", ""))


def require_evidence_path(value: object, owner: str, failures: list[str]) -> None:
    if not isinstance(value, str) or not (ROOT / value).is_file():
        failures.append(f"{owner}: evidence file is missing")


def validate_upload_artifacts(
    upload_manifest: object,
    product_release: str,
    failures: list[str],
) -> None:
    if not isinstance(upload_manifest, dict):
        failures.append("upload manifest must be an object")
        return
    artifacts = upload_manifest.get("artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != ARTIFACT_NAMES:
        failures.append(
            "upload manifest artifacts must contain exactly android_phone, "
            "wear_os, and apple"
        )
        return

    source_identities = {
        "android_phone": read_source_integer(
            "app/build.gradle.kts",
            r"versionCode\s*=\s*([\d_]+)",
            "android_phone",
            failures,
        ),
        "wear_os": read_source_integer(
            "wearApp/build.gradle.kts",
            r"versionCode\s*=\s*([\d_]+)",
            "wear_os",
            failures,
        ),
        "apple": read_source_integer(
            "iosApp/project.yml",
            r"CURRENT_PROJECT_VERSION:\s*([\d_]+)",
            "apple",
            failures,
        ),
    }
    apple_build = source_identities["apple"]
    project_versions = {
        int(value)
        for value in re.findall(
            r"CURRENT_PROJECT_VERSION = (\d+);",
            (ROOT / "iosApp/Nimbo.xcodeproj/project.pbxproj").read_text(
                encoding="utf-8"
            ),
        )
    }
    if apple_build is not None and project_versions != {apple_build}:
        failures.append(
            "Apple generated project build identity differs from iosApp/project.yml"
        )

    identity_fields = {
        "android_phone": "version_code",
        "wear_os": "version_code",
        "apple": "build",
    }
    expected_filenames = {
        "android_phone": (
            f"nimbo-phone-{product_release}-vc{source_identities['android_phone']}.aab"
        ),
        "wear_os": (
            f"nimbo-wear-{product_release}-vc{source_identities['wear_os']}.aab"
        ),
        "apple": "Nimbo.ipa",
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

    for artifact_name in sorted(ARTIFACT_NAMES):
        artifact = artifacts[artifact_name]
        identity_field = identity_fields[artifact_name]
        owner = f"upload manifest artifact {artifact_name}"
        expected_fields = common_fields | {identity_field}
        if not isinstance(artifact, dict) or set(artifact) != expected_fields:
            failures.append(f"{owner}: expected exactly {sorted(expected_fields)}")
            continue
        expected_identity = source_identities[artifact_name]
        if artifact[identity_field] != expected_identity:
            failures.append(
                f"{owner}: declared {identity_field} {artifact[identity_field]!r} "
                f"differs from source {expected_identity!r}"
            )
        if artifact["filename"] != expected_filenames[artifact_name]:
            failures.append(
                f"{owner}: filename does not match the declared source identity"
            )
        require_evidence_path(
            artifact["source_sync_evidence"],
            f"{owner}.source_sync_evidence",
            failures,
        )

        source_sync = artifact["source_sync"]
        if source_sync == "blocked":
            for field in ("sha256", "signing_evidence", "physical_qa_evidence"):
                if artifact[field] is not None:
                    failures.append(f"{owner}: blocked artifact must keep {field} null")
            historical = artifact["historical_candidate"]
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
            if historical["status"] != "historical-superseded":
                failures.append(
                    f"{owner}: historical candidate must be marked superseded"
                )
            historical_identity = historical[identity_field]
            if (
                not isinstance(historical_identity, int)
                or expected_identity is None
                or historical_identity >= expected_identity
            ):
                failures.append(
                    f"{owner}: historical identity must precede current source"
                )
            historical_sha = historical["sha256"]
            if not isinstance(historical_sha, str) or not SHA256.fullmatch(
                historical_sha
            ):
                failures.append(f"{owner}: historical SHA-256 is invalid")
            require_evidence_path(
                historical["signing_evidence"],
                f"{owner}.historical.signing_evidence",
                failures,
            )
            signing_evidence = historical["signing_evidence"]
            if (
                isinstance(signing_evidence, str)
                and isinstance(historical_sha, str)
                and (ROOT / signing_evidence).is_file()
                and historical_sha
                not in (ROOT / signing_evidence).read_text(encoding="utf-8")
            ):
                failures.append(
                    f"{owner}: historical SHA-256 is absent from signing evidence"
                )
            require_evidence_path(
                historical["physical_qa_evidence"],
                f"{owner}.historical.physical_qa_evidence",
                failures,
            )
        elif source_sync == "verified-current":
            artifact_sha = artifact["sha256"]
            if not isinstance(artifact_sha, str) or not SHA256.fullmatch(artifact_sha):
                failures.append(f"{owner}: verified-current SHA-256 is invalid")
            require_evidence_path(
                artifact["signing_evidence"],
                f"{owner}.signing_evidence",
                failures,
            )
            signing_evidence = artifact["signing_evidence"]
            if (
                isinstance(signing_evidence, str)
                and isinstance(artifact_sha, str)
                and (ROOT / signing_evidence).is_file()
                and artifact_sha
                not in (ROOT / signing_evidence).read_text(encoding="utf-8")
            ):
                failures.append(f"{owner}: SHA-256 is absent from signing evidence")
            physical_evidence = artifact["physical_qa_evidence"]
            if physical_evidence is not None:
                require_evidence_path(
                    physical_evidence,
                    f"{owner}.physical_qa_evidence",
                    failures,
                )
            if artifact["historical_candidate"] is not None:
                failures.append(
                    f"{owner}: verified-current artifact cannot carry a replacement"
                )
        else:
            failures.append(f"{owner}: invalid source_sync {source_sync!r}")


def main() -> int:
    metadata_path = ROOT / "store/metadata.json"
    schema_path = ROOT / "store/metadata.schema.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    failures: list[str] = []

    if set(metadata) != TOP_LEVEL_FIELDS:
        failures.append(
            f"top-level fields differ: missing={sorted(TOP_LEVEL_FIELDS - set(metadata))}, "
            f"extra={sorted(set(metadata) - TOP_LEVEL_FIELDS)}"
        )
    if metadata.get("$schema") != "./metadata.schema.json":
        failures.append("$schema must reference ./metadata.schema.json")
    if metadata.get("schema_version") != 2:
        failures.append("schema_version must be 2")
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        failures.append("metadata.schema.json must use JSON Schema draft 2020-12")
    if schema.get("$id") != EXPECTED_SCHEMA_ID:
        failures.append(
            f"metadata.schema.json $id must use canonical {EXPECTED_SCHEMA_ID!r}"
        )
    try:
        date.fromisoformat(metadata.get("metadata_revision", ""))
    except (TypeError, ValueError):
        failures.append("metadata_revision must be an ISO date")

    product = metadata.get("product", {})
    if set(product) != {"id", "release", "urls"}:
        failures.append("product must contain exactly id, release, and urls")
    product_urls = product.get("urls", {}) if isinstance(product, dict) else {}
    product_release = product.get("release") if isinstance(product, dict) else None
    if not isinstance(product_release, str) or not SEMANTIC_VERSION.fullmatch(
        product_release
    ):
        failures.append("product.release must be a three-part semantic version")
    else:
        version_sources = {
            "Android phone": (
                ROOT / "app/build.gradle.kts",
                r'versionName\s*=\s*"([^"]+)"',
            ),
            "Wear OS": (
                ROOT / "wearApp/build.gradle.kts",
                r'versionName\s*=\s*"([^"]+)"',
            ),
            "Apple": (
                ROOT / "iosApp/project.yml",
                r"MARKETING_VERSION:\s*([^\s]+)",
            ),
        }
        for platform, (path, pattern) in version_sources.items():
            match = re.search(pattern, path.read_text(encoding="utf-8"))
            if match is None:
                failures.append(f"{platform}: release version could not be read")
            elif match.group(1) != product_release:
                failures.append(
                    f"{platform}: {match.group(1)!r} differs from "
                    f"product.release {product_release!r}"
                )
    if set(product_urls) != {"marketing", "support", "privacy"}:
        failures.append(
            "product.urls must contain exactly marketing, support, and privacy"
        )
    for name, value in product_urls.items():
        if not is_https_url(value):
            failures.append(f"product.urls.{name}: expected an HTTPS URL")
        elif value != EXPECTED_PUBLIC_URLS.get(name):
            failures.append(
                f"product.urls.{name}: expected canonical "
                f"{EXPECTED_PUBLIC_URLS.get(name)!r}"
            )

    localizations = metadata.get("localizations", {})
    if not isinstance(localizations, dict):
        failures.append("localizations must be an object")
        localizations = {}
    if set(localizations) != EXPECTED_LOCALES:
        failures.append(
            f"locale set differs: missing={sorted(EXPECTED_LOCALES - set(localizations))}, "
            f"extra={sorted(set(localizations) - EXPECTED_LOCALES)}"
        )
    for locale, fields in localizations.items():
        validate_text_fields(locale, fields, LOCALIZATION_LIMITS, failures)
        if isinstance(fields, dict):
            lowered = " ".join(str(value) for value in fields.values()).lower()
            for forbidden in ("ai weather", "most accurate", "самый точный"):
                if forbidden in lowered:
                    failures.append(
                        f"{locale}: forbidden unsupported claim {forbidden!r}"
                    )

    creative_sets = metadata.get("creative_sets", {})
    if not isinstance(creative_sets, dict) or not creative_sets:
        failures.append("creative_sets must be a non-empty object")
        creative_sets = {}
    for creative_id, creative in creative_sets.items():
        expected_fields = {
            "revision",
            "manifest",
            "platforms",
            "audience_locales",
            "support_url",
        }
        if not isinstance(creative, dict) or set(creative) != expected_fields:
            failures.append(
                f"creative_sets.{creative_id}: expected exactly {sorted(expected_fields)}"
            )
            continue
        if not isinstance(creative["revision"], int) or creative["revision"] < 1:
            failures.append(
                f"creative_sets.{creative_id}.revision must be a positive integer"
            )
        if set(creative["platforms"]) != PLATFORMS:
            failures.append(
                f"creative_sets.{creative_id}.platforms must cover both stores"
            )
        if not set(creative["audience_locales"]).issubset(localizations):
            failures.append(f"creative_sets.{creative_id}: unknown audience locale")
        if not is_https_url(creative["support_url"]):
            failures.append(f"creative_sets.{creative_id}.support_url must be HTTPS")
        elif creative["support_url"] != EXPECTED_PUBLIC_URLS["support"]:
            failures.append(
                f"creative_sets.{creative_id}.support_url must use canonical "
                f"{EXPECTED_PUBLIC_URLS['support']!r}"
            )
        manifest_path = ROOT / creative["manifest"]
        if not manifest_path.is_file():
            failures.append(
                f"creative_sets.{creative_id}: missing manifest {creative['manifest']}"
            )
        else:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("id") != creative_id:
                failures.append(f"creative_sets.{creative_id}: manifest id mismatch")
            if manifest.get("revision") != creative["revision"]:
                failures.append(
                    f"creative_sets.{creative_id}: manifest revision mismatch"
                )

    experiments = metadata.get("experiments", {})
    if not isinstance(experiments, dict):
        failures.append("experiments must be an object")
        experiments = {}
    experiment_fields = {
        "status",
        "platforms",
        "baseline_creative_set",
        "variant_creative_set",
        "single_variable",
        "minimum_weekly_store_visitors",
        "decision_rule",
    }
    for experiment_id, experiment in experiments.items():
        if not isinstance(experiment, dict) or set(experiment) != experiment_fields:
            failures.append(
                f"experiments.{experiment_id}: expected exactly {sorted(experiment_fields)}"
            )
            continue
        if experiment["status"] not in {
            "not-started",
            "running",
            "completed",
            "cancelled",
        }:
            failures.append(f"experiments.{experiment_id}: invalid status")
        if not set(experiment["platforms"]).issubset(PLATFORMS):
            failures.append(f"experiments.{experiment_id}: invalid platform")
        if experiment["baseline_creative_set"] not in creative_sets:
            failures.append(
                f"experiments.{experiment_id}: unknown baseline creative set"
            )
        variant = experiment["variant_creative_set"]
        if variant is not None and variant not in creative_sets:
            failures.append(
                f"experiments.{experiment_id}: unknown variant creative set"
            )
        if experiment["minimum_weekly_store_visitors"] < 500:
            failures.append(
                f"experiments.{experiment_id}: traffic gate must be at least 500"
            )
        if experiment["status"] == "running" and variant is None:
            failures.append(
                f"experiments.{experiment_id}: running experiment requires a variant"
            )

    listings = metadata.get("listings", [])
    if not isinstance(listings, list):
        failures.append("listings must be an array")
        listings = []
    listing_by_id: dict[str, dict] = {}
    for index, listing in enumerate(listings):
        owner = f"listings[{index}]"
        if not isinstance(listing, dict) or set(listing) != LISTING_FIELDS:
            failures.append(f"{owner}: expected exactly {sorted(LISTING_FIELDS)}")
            continue
        listing_id = listing["id"]
        if listing_id in listing_by_id:
            failures.append(f"{owner}: duplicate id {listing_id!r}")
        listing_by_id[listing_id] = listing
        if listing["platform"] not in PLATFORMS:
            failures.append(f"{owner}: invalid platform")
        if listing["listing_type"] not in LISTING_TYPES:
            failures.append(f"{owner}: invalid listing_type")
        refs = listing["localization_refs"]
        if (
            not isinstance(refs, list)
            or not refs
            or not set(refs).issubset(localizations)
        ):
            failures.append(
                f"{owner}: localization_refs contain unknown or empty values"
            )
        for locale, overrides in listing["overrides"].items():
            if locale not in refs:
                failures.append(f"{owner}: override locale {locale} is not referenced")
            validate_text_fields(
                owner + f".overrides.{locale}",
                overrides,
                LOCALIZATION_LIMITS,
                failures,
                exact=False,
            )
        if listing["creative_set"] not in creative_sets:
            failures.append(f"{owner}: unknown creative_set")
        experiment_id = listing["experiment"]
        if experiment_id is not None and experiment_id not in experiments:
            failures.append(f"{owner}: unknown experiment")
        for url_field in ("marketing_url", "support_url", "privacy_url"):
            if not is_https_url(listing[url_field]):
                failures.append(f"{owner}.{url_field}: expected an HTTPS URL")
                continue
            canonical_key = url_field.removesuffix("_url")
            if listing[url_field] != EXPECTED_PUBLIC_URLS[canonical_key]:
                failures.append(
                    f"{owner}.{url_field}: expected canonical "
                    f"{EXPECTED_PUBLIC_URLS[canonical_key]!r}"
                )
        listing_type = listing["listing_type"]
        if listing_type == "default":
            if (
                listing["custom_listing"] is not None
                or listing["custom_product_page"] is not None
            ):
                failures.append(
                    f"{owner}: default listing cannot have a custom payload"
                )
        elif listing_type == "custom-listing":
            if listing["platform"] != "google-play" or not isinstance(
                listing["custom_listing"], dict
            ):
                failures.append(f"{owner}: custom-listing is Google Play only")
            if listing["custom_product_page"] is not None:
                failures.append(
                    f"{owner}: custom-listing cannot have a custom product page"
                )
        elif listing_type == "custom-product-page":
            if listing["platform"] != "app-store" or not isinstance(
                listing["custom_product_page"], dict
            ):
                failures.append(f"{owner}: custom-product-page is App Store only")
            if listing["custom_listing"] is not None:
                failures.append(
                    f"{owner}: custom-product-page cannot have a custom listing"
                )

    app_default = listing_by_id.get("app-store-default", {})
    if (
        app_default.get("overrides", {}).get("en-US", {}).get("title")
        != "Nimbo Weather"
    ):
        failures.append(
            "app-store-default must preserve the global title Nimbo Weather"
        )

    google_uz = listing_by_id.get("google-play-uz-custom-listing", {})
    custom_listing = google_uz.get("custom_listing", {})
    if google_uz.get("storefront") != "UZ" or custom_listing.get("country_targets") != [
        "UZ"
    ]:
        failures.append("google-play-uz-custom-listing must target only UZ")
    custom_locales = custom_listing.get("localizations", {})
    if set(custom_locales) != {"uz-UZ", "ru-RU"}:
        failures.append(
            "Google UZ custom listing must contain separate Uzbek and Russian copy"
        )
    else:
        uz_copy = custom_locales["uz-UZ"]
        ru_copy = custom_locales["ru-RU"]
        if (
            uz_copy.get("title") != UZ_TITLE
            or uz_copy.get("short_description") != UZ_SHORT
        ):
            failures.append(
                "Google UZ title or short description differs from the approved copy"
            )
        for locale, copy in (("uz-UZ", uz_copy), ("ru-RU", ru_copy)):
            validate_text_fields(
                f"google-play-uz-custom-listing.{locale}",
                {
                    "title": copy.get("title"),
                    "short_description": copy.get("short_description"),
                },
                {"title": 30, "short_description": 80},
                failures,
            )

    app_uz = listing_by_id.get("app-store-uz-custom-product-page", {})
    cpp = app_uz.get("custom_product_page", {})
    if app_uz.get("storefront") != "UZ" or cpp.get("status") != "draft":
        failures.append("App Store UZ custom product page must remain a UZ draft")
    if (
        cpp.get("audience_locale") != "uz-UZ"
        or cpp.get("store_locale_fallback") != "en-US"
    ):
        failures.append(
            "App Store UZ custom product page must record the unsupported-locale fallback"
        )
    if len(cpp.get("promotional_text", "")) > 170:
        failures.append(
            "App Store custom product page promotional text exceeds 170 characters"
        )
    if not cpp.get("keyword_targets"):
        failures.append("App Store UZ custom product page requires keyword targets")

    upload_manifest_path = ROOT / f"store/upload-manifest-{product_release}.json"
    if not isinstance(product_release, str) or not upload_manifest_path.is_file():
        failures.append(
            f"missing resolved upload manifest {upload_manifest_path.relative_to(ROOT)}"
        )
    else:
        upload_manifest = json.loads(upload_manifest_path.read_text(encoding="utf-8"))
        if upload_manifest.get("release") != product_release:
            failures.append("upload manifest release differs from product.release")
        if upload_manifest.get("status") != "draft-blocked":
            failures.append("upload manifest must remain draft-blocked before upload")
        if upload_manifest.get("metadata") != "store/metadata.json":
            failures.append("upload manifest must reference store/metadata.json")
        validate_upload_artifacts(upload_manifest, product_release, failures)
        payloads = upload_manifest.get("listing_payloads", [])
        payload_ids = {
            payload.get("listing_id")
            for payload in payloads
            if isinstance(payload, dict)
        }
        if payload_ids != set(listing_by_id):
            failures.append("upload manifest must resolve every listing exactly once")
        for payload in payloads:
            if not isinstance(payload, dict):
                failures.append("upload manifest listing payload must be an object")
                continue
            listing = listing_by_id.get(payload.get("listing_id"), {})
            if set(payload.get("store_locales", [])) != set(
                listing.get("localization_refs", [])
            ):
                failures.append(
                    f"upload manifest {payload.get('listing_id')}: locale mapping differs"
                )
            for key in ("asset_root", "growth_creatives", "feature_graphic"):
                path = payload.get(key)
                if path is not None and not (ROOT / path).exists():
                    failures.append(
                        f"upload manifest {payload.get('listing_id')}: missing {key} {path}"
                    )
            feature_graphics = payload.get("feature_graphics", {})
            if not isinstance(feature_graphics, dict):
                failures.append(
                    f"upload manifest {payload.get('listing_id')}: invalid feature map"
                )
            else:
                for locale, path in feature_graphics.items():
                    if locale not in payload.get("store_locales", []):
                        failures.append(
                            f"upload manifest {payload.get('listing_id')}: "
                            f"feature locale {locale} is not mapped"
                        )
                    if not isinstance(path, str) or not (ROOT / path).is_file():
                        failures.append(
                            f"upload manifest {payload.get('listing_id')}: "
                            f"missing feature graphic {path}"
                        )
        payload_by_id = {
            payload["listing_id"]: payload
            for payload in payloads
            if isinstance(payload, dict) and payload.get("listing_id") in listing_by_id
        }
        play_default = payload_by_id.get("google-play-default", {})
        if play_default.get("feature_graphic") != (
            "store/assets/google-play/feature-graphic-en-US-1024x500.jpg"
        ):
            failures.append(
                "Google Play default upload must use the en-US feature graphic"
            )
        play_uz = payload_by_id.get("google-play-uz-custom-listing", {})
        if play_uz.get("feature_graphics") != {
            "uz-UZ": "store/assets/google-play/feature-graphic-uz-UZ-1024x500.jpg",
            "ru-RU": "store/assets/google-play/feature-graphic-ru-RU-1024x500.jpg",
        }:
            failures.append(
                "Google Play UZ upload must map the UZ and RU feature graphics"
            )
    if failures:
        print("Store metadata check failed:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print(
        f"Store metadata passed: schema v2, {len(localizations)} locales, "
        f"{len(listings)} listings, {len(creative_sets)} creative set, "
        f"release {product_release} upload manifest."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
