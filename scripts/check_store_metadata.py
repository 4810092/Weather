#!/usr/bin/env python3
"""Validate versioned store listings, locale copy, experiments, and URLs."""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

try:
    from scripts.release_artifact_verifier import verify_manifest_artifacts
except ModuleNotFoundError:
    from release_artifact_verifier import verify_manifest_artifacts  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_LOCALES = {
    "en-US",
    "en-GB",
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
APPLE_UTF8_BYTE_FIELDS = frozenset({"keywords"})
CPP_LOCALIZED_ASSET_ROOTS = {
    "en-GB": "store/creatives/growth-2026-08/app-store/uz-UZ",
    "ru-RU": "store/creatives/growth-2026-08/app-store/ru-RU",
}
APP_STORE_DEFAULT_ASSET_LOCALE_ALIASES = {"en-GB": "en-US"}
APPLE_CPP_ASSIGNMENT_SEQUENCE = [
    "submit-base-version-keywords",
    "wait-for-base-version-approval",
    "assign-custom-product-page-keywords",
]
APPLE_CPP_FIELDS = frozenset(
    {
        "reference_name",
        "status",
        "audience_locale",
        "store_locale_fallback",
        "keyword_assignment_gate",
        "localizations",
    }
)
APPLE_CPP_LOCALIZATION_FIELDS = frozenset(
    {"audience_locale", "promotional_text", "planned_keyword_targets"}
)
GOOGLE_UZ_COUNTRY_LISTING_ID = "google-play-uz-country-listing"
GOOGLE_CUSTOM_LISTING_FIELDS = frozenset(
    {"name", "status", "default_store_locale", "targeting", "localizations"}
)
GOOGLE_CUSTOM_LOCALIZATION_FIELDS = frozenset(
    {
        "audience_locale",
        "store_locale_fallback",
        "title",
        "short_description",
        "full_description",
    }
)
GOOGLE_UZ_LOCALIZED_ASSET_ROOTS = {
    "en-US": "store/creatives/growth-2026-08/google-play/uz-UZ",
    "ru-RU": "store/creatives/growth-2026-08/google-play/ru-RU",
}
GOOGLE_UZ_FEATURE_GRAPHICS = {
    "en-US": "store/assets/google-play/feature-graphic-uz-UZ-1024x500.jpg",
    "ru-RU": "store/assets/google-play/feature-graphic-ru-RU-1024x500.jpg",
}
GOOGLE_UZ_FULL_DESCRIPTION_SOURCES = {
    "en-US": "metadata.localizations.uz-UZ.description",
    "ru-RU": "metadata.localizations.ru-RU.description",
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
UZ_TITLE = "Nimbo Weather: Ob-havo"
UZ_SHORT = "Toshkent va O‘zbekiston ob-havosi: chiqish uchun eng yaxshi vaqtni toping."
RU_TITLE = "Nimbo: Погода и прогноз"
RU_SHORT = "Прогноз погоды: найдите лучшее время, чтобы выйти на улицу."
EN_APP_STORE_SUBTITLE = "Best time to go outside"
APPLE_UZ_DEFAULT_LOCALE = "en-GB"
RU_APP_STORE_SUBTITLE = "Лучшее время для прогулки"
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
    utf8_byte_fields: frozenset[str] = frozenset(),
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
        measured_length = (
            len(value.encode("utf-8")) if field in utf8_byte_fields else len(value)
        )
        if measured_length > limits[field]:
            unit = " UTF-8 bytes" if field in utf8_byte_fields else " characters"
            failures.append(
                f"{owner}:{field}: {measured_length}{unit} > {limits[field]}"
            )


def validate_listing_localization_refs(
    owner: str,
    refs: object,
    known_locales: set[str],
    failures: list[str],
) -> None:
    if (
        not isinstance(refs, list)
        or not refs
        or not all(isinstance(ref, str) and ref for ref in refs)
    ):
        failures.append(f"{owner}: localization_refs contain unknown or empty values")
        return
    if len(refs) != len(set(refs)):
        failures.append(f"{owner}: localization_refs must be unique")
    if not set(refs).issubset(known_locales):
        failures.append(f"{owner}: localization_refs contain unknown or empty values")


def configured_generic_terms(root: Path = ROOT) -> list[str]:
    config = json.loads((root / "growth/config.json").read_text(encoding="utf-8"))
    return [
        query["term"] for query in config["queries"] if query.get("branded") is False
    ]


def apple_keyword_tokens(value: object) -> set[str]:
    if not isinstance(value, str):
        return set()
    return {token.strip().casefold() for token in value.split(",") if token.strip()}


def validate_app_store_default_metadata(
    metadata: object,
    app_default: object,
    failures: list[str],
) -> None:
    if not isinstance(metadata, dict) or not isinstance(app_default, dict):
        failures.append("app-store-default metadata must be an object")
        return
    localizations = metadata.get("localizations", {})
    if not isinstance(localizations, dict):
        failures.append("app-store-default localizations must be an object")
        return
    refs = app_default.get("localization_refs", [])
    if APPLE_UZ_DEFAULT_LOCALE not in refs:
        failures.append(
            "app-store-default must include en-GB for the UZ default language"
        )
    overrides = app_default.get("overrides", {})
    if not isinstance(overrides, dict):
        failures.append("app-store-default overrides must be an object")
        return
    for locale in ("en-US", APPLE_UZ_DEFAULT_LOCALE):
        if overrides.get(locale) != {"title": "Nimbo Weather"}:
            failures.append(
                f"app-store-default must preserve the Nimbo Weather title for {locale}"
            )
        localization = localizations.get(locale, {})
        if (
            not isinstance(localization, dict)
            or localization.get("subtitle") != EN_APP_STORE_SUBTITLE
        ):
            failures.append(
                f"app-store-default must preserve the benefit-led {locale} subtitle"
            )
    if overrides.get("ru-RU") != {
        "title": RU_TITLE,
        "subtitle": RU_APP_STORE_SUBTITLE,
    }:
        failures.append(
            "app-store-default must preserve the query-first Russian title and "
            "Best Time Outside subtitle"
        )


def validate_uz_store_targeting(
    metadata: object,
    generic_terms: list[str],
    failures: list[str],
) -> None:
    if not isinstance(metadata, dict):
        failures.append("UZ store targeting: metadata must be an object")
        return
    listings = metadata.get("listings", [])
    if not isinstance(listings, list):
        failures.append("UZ store targeting: listings must be an array")
        return
    listing_by_id = {
        listing.get("id"): listing
        for listing in listings
        if isinstance(listing, dict) and isinstance(listing.get("id"), str)
    }
    expected_terms = [term for term in generic_terms if isinstance(term, str)]
    expected_folded = {term.casefold() for term in expected_terms}

    google_custom_listing_ids = {
        listing.get("id")
        for listing in listings
        if isinstance(listing, dict)
        and listing.get("platform") == "google-play"
        and listing.get("listing_type") == "custom-listing"
    }
    if google_custom_listing_ids != {GOOGLE_UZ_COUNTRY_LISTING_ID}:
        failures.append(
            "Publishable Google metadata must contain only the UZ country custom listing"
        )
    base_localizations = metadata.get("localizations", {})
    if not isinstance(base_localizations, dict):
        base_localizations = {}
    uz_base = base_localizations.get("uz-UZ", {})
    ru_base = base_localizations.get("ru-RU", {})
    expected_google_locales = {
        "en-US": {
            "audience_locale": "uz-UZ",
            "store_locale_fallback": "en-US",
            "title": UZ_TITLE,
            "short_description": UZ_SHORT,
            "full_description": (
                uz_base.get("description") if isinstance(uz_base, dict) else None
            ),
        },
        "ru-RU": {
            "audience_locale": "ru-RU",
            "store_locale_fallback": "ru-RU",
            "title": RU_TITLE,
            "short_description": RU_SHORT,
            "full_description": (
                ru_base.get("description") if isinstance(ru_base, dict) else None
            ),
        },
    }
    listing_id = GOOGLE_UZ_COUNTRY_LISTING_ID
    listing = listing_by_id.get(listing_id, {})
    if not isinstance(listing, dict):
        listing = {}
    if (
        listing.get("platform") != "google-play"
        or listing.get("listing_type") != "custom-listing"
        or listing.get("storefront") != "UZ"
    ):
        failures.append(f"{listing_id}: platform, type, or storefront differs")
    if listing.get("localization_refs") != ["en-US", "ru-RU"]:
        failures.append(f"{listing_id}: store locales must be en-US plus ru-RU")
    custom_listing = listing.get("custom_listing", {})
    if (
        not isinstance(custom_listing, dict)
        or set(custom_listing) != GOOGLE_CUSTOM_LISTING_FIELDS
    ):
        failures.append(f"{listing_id}: custom listing fields must be exact and explicit")
        custom_listing = {}
    custom_listing_name = custom_listing.get("name")
    if not isinstance(custom_listing_name, str) or not custom_listing_name.strip():
        failures.append(f"{listing_id}: custom listing name must be non-empty")
    if custom_listing.get("status") != "draft":
        failures.append(f"{listing_id}: custom listing must remain a draft")
    if custom_listing.get("default_store_locale") != "en-US":
        failures.append(f"{listing_id}: default_store_locale must be en-US")
    if custom_listing.get("targeting") != {
        "type": "country",
        "country_targets": ["UZ"],
    }:
        failures.append(f"{listing_id}: targeting must be country UZ only")
    custom_localizations = custom_listing.get("localizations", {})
    if custom_localizations != expected_google_locales:
        failures.append(
            f"{listing_id}: localized copy or audience/store-locale mapping differs"
        )
    if isinstance(custom_localizations, dict):
        for store_locale, payload in custom_localizations.items():
            if not isinstance(payload, dict):
                failures.append(f"{listing_id}.{store_locale}: expected an object")
                continue
            if set(payload) != GOOGLE_CUSTOM_LOCALIZATION_FIELDS:
                failures.append(
                    f"{listing_id}.{store_locale}: expected exactly "
                    f"{sorted(GOOGLE_CUSTOM_LOCALIZATION_FIELDS)}"
                )
            validate_text_fields(
                f"{listing_id}.{store_locale}",
                {
                    "title": payload.get("title"),
                    "short_description": payload.get("short_description"),
                    "full_description": payload.get("full_description"),
                },
                {"title": 30, "short_description": 80, "full_description": 4000},
                failures,
            )

    apple_listing = listing_by_id.get("app-store-uz-custom-product-page", {})
    apple_cpp = (
        apple_listing.get("custom_product_page", {})
        if isinstance(apple_listing, dict)
        else {}
    )
    if not isinstance(apple_cpp, dict) or set(apple_cpp) != APPLE_CPP_FIELDS:
        failures.append(
            "App Store UZ custom product page fields must be exact and explicit"
        )
        apple_cpp = {}
    reference_name = apple_cpp.get("reference_name")
    if not isinstance(reference_name, str) or not reference_name.strip():
        failures.append(
            "App Store UZ custom product page reference_name must be non-empty"
        )
    expected_assignment_gate = {
        "status": "blocked-pending-base-version-approval",
        "candidate_source_version": metadata.get("product", {}).get("release"),
        "required_sequence": APPLE_CPP_ASSIGNMENT_SEQUENCE,
    }
    if apple_cpp.get("keyword_assignment_gate") != expected_assignment_gate:
        failures.append(
            "App Store UZ custom product page keyword assignment must remain blocked "
            "until the candidate base version is approved"
        )
    cpp_localizations = apple_cpp.get("localizations", {})
    if not isinstance(cpp_localizations, dict) or set(cpp_localizations) != {
        APPLE_UZ_DEFAULT_LOCALE,
        "ru-RU",
    }:
        failures.append(
            "App Store UZ custom product page requires explicit en-GB and ru-RU "
            "localization payloads"
        )
        return

    expected_audience_locales = {
        APPLE_UZ_DEFAULT_LOCALE: "uz-UZ",
        "ru-RU": "ru-RU",
    }
    targeted_folded: set[str] = set()
    for store_locale, payload in cpp_localizations.items():
        owner = f"app-store-uz-custom-product-page.{store_locale}"
        if not isinstance(payload, dict):
            failures.append(f"{owner}: expected an object")
            continue
        if set(payload) != APPLE_CPP_LOCALIZATION_FIELDS:
            failures.append(
                f"{owner}: expected exactly {sorted(APPLE_CPP_LOCALIZATION_FIELDS)}"
            )
        if payload.get("audience_locale") != expected_audience_locales[store_locale]:
            failures.append(f"{owner}: audience locale mapping differs")
        validate_text_fields(
            owner,
            {"promotional_text": payload.get("promotional_text")},
            {"promotional_text": 170},
            failures,
        )
        targets = payload.get("planned_keyword_targets")
        if (
            not isinstance(targets, list)
            or not targets
            or not all(isinstance(target, str) and target.strip() for target in targets)
        ):
            failures.append(
                f"{owner}: planned_keyword_targets must be a non-empty string list"
            )
            continue
        normalized_targets = {target.casefold() for target in targets}
        if len(normalized_targets) != len(targets):
            failures.append(
                f"{owner}: planned_keyword_targets must be unique ignoring case"
            )
        base_payload = (
            base_localizations.get(store_locale, {})
            if isinstance(base_localizations, dict)
            else {}
        )
        base_keywords = apple_keyword_tokens(
            base_payload.get("keywords") if isinstance(base_payload, dict) else None
        )
        missing_from_candidate_pool = normalized_targets - base_keywords
        if missing_from_candidate_pool:
            failures.append(
                f"{owner}: planned targets missing from the candidate base Apple "
                f"keyword pool: {sorted(missing_from_candidate_pool)}"
            )
        targeted_folded.update(normalized_targets)
    if targeted_folded != expected_folded:
        failures.append(
            "App Store UZ custom product page planned keyword union must exactly match "
            "the configured generic queries"
        )


def validate_cpp_upload_mapping(
    metadata: object,
    upload_manifest: object,
    failures: list[str],
    *,
    root: Path = ROOT,
) -> None:
    if not isinstance(metadata, dict) or not isinstance(upload_manifest, dict):
        failures.append("App Store CPP upload mapping requires object inputs")
        return
    listings = metadata.get("listings", [])
    if not isinstance(listings, list):
        failures.append("App Store CPP upload mapping requires a listings array")
        return
    cpp_listing = next(
        (
            listing
            for listing in listings
            if isinstance(listing, dict)
            and listing.get("id") == "app-store-uz-custom-product-page"
        ),
        {},
    )
    payloads = upload_manifest.get("listing_payloads", [])
    if not isinstance(payloads, list):
        failures.append("App Store CPP upload mapping requires a payload array")
        return
    cpp_uploads = [
        payload
        for payload in payloads
        if isinstance(payload, dict)
        and payload.get("listing_id") == "app-store-uz-custom-product-page"
    ]
    if len(cpp_uploads) != 1:
        failures.append(
            "App Store UZ upload requires exactly one CPP payload; "
            f"found {len(cpp_uploads)}"
        )
    cpp_upload = cpp_uploads[0] if cpp_uploads else {}
    expected_upload_fields = {
        "listing_id",
        "store_locales",
        "audience_locale",
        "store_locale_fallback",
        "keyword_assignment_gate",
        "localized_asset_roots",
    }
    if set(cpp_upload) != expected_upload_fields:
        failures.append(
            "App Store UZ upload requires exactly one explicit localized asset map"
        )
    cpp_metadata = (
        cpp_listing.get("custom_product_page", {})
        if isinstance(cpp_listing, dict)
        else {}
    )
    if not isinstance(cpp_metadata, dict):
        cpp_metadata = {}
    if cpp_upload.get("keyword_assignment_gate") != cpp_metadata.get(
        "keyword_assignment_gate"
    ):
        failures.append(
            "App Store UZ upload keyword assignment gate differs from metadata"
        )
    metadata_locales = set(cpp_metadata.get("localizations", {}))
    upload_locales = set(cpp_upload.get("store_locales", []))
    localized_asset_roots = cpp_upload.get("localized_asset_roots")
    if not isinstance(localized_asset_roots, dict):
        failures.append(
            "App Store UZ upload requires localized_asset_roots for every store locale"
        )
        return
    if (
        metadata_locales != upload_locales
        or set(localized_asset_roots) != upload_locales
    ):
        failures.append(
            "App Store UZ upload locale, copy, and localized asset mappings differ"
        )
    if localized_asset_roots != CPP_LOCALIZED_ASSET_ROOTS:
        failures.append(
            "App Store UZ upload must map en-GB to Uzbek assets and ru-RU to Russian assets"
        )
    for locale, relative in localized_asset_roots.items():
        if not isinstance(relative, str) or not (root / relative).is_dir():
            failures.append(
                f"App Store UZ upload: missing localized asset root {locale}: {relative}"
            )


def validate_google_uz_upload_mapping(
    metadata: object,
    upload_manifest: object,
    failures: list[str],
    *,
    root: Path = ROOT,
) -> None:
    if not isinstance(metadata, dict) or not isinstance(upload_manifest, dict):
        failures.append("Google UZ upload mapping requires object inputs")
        return
    listings = metadata.get("listings", [])
    payloads = upload_manifest.get("listing_payloads", [])
    if not isinstance(listings, list) or not isinstance(payloads, list):
        failures.append("Google UZ upload mapping requires listing and payload arrays")
        return
    listing_by_id = {
        listing.get("id"): listing
        for listing in listings
        if isinstance(listing, dict) and isinstance(listing.get("id"), str)
    }
    expected_fields = {
        "listing_id",
        "store_locales",
        "default_store_locale",
        "targeting",
        "full_description_sources",
        "localized_asset_roots",
        "feature_graphics",
    }
    listing_id = GOOGLE_UZ_COUNTRY_LISTING_ID
    matched_payloads = [
        payload
        for payload in payloads
        if isinstance(payload, dict) and payload.get("listing_id") == listing_id
    ]
    if len(matched_payloads) != 1:
        failures.append(
            f"{listing_id}: upload requires exactly one payload; "
            f"found {len(matched_payloads)}"
        )
    payload = matched_payloads[0] if matched_payloads else {}
    if set(payload) != expected_fields:
        failures.append(
            f"{listing_id}: upload fields must use explicit locale, copy, and targeting maps"
        )
    if payload.get("store_locales") != ["en-US", "ru-RU"]:
        failures.append(f"{listing_id}: upload store locales must be en-US plus ru-RU")
    if payload.get("default_store_locale") != "en-US":
        failures.append(f"{listing_id}: upload default_store_locale must be en-US")
    listing = listing_by_id.get(listing_id, {})
    custom_listing = (
        listing.get("custom_listing", {}) if isinstance(listing, dict) else {}
    )
    expected_targeting = (
        custom_listing.get("targeting", {})
        if isinstance(custom_listing, dict)
        else {}
    )
    if payload.get("targeting") != expected_targeting:
        failures.append(f"{listing_id}: upload targeting differs from metadata")
    if payload.get("full_description_sources") != GOOGLE_UZ_FULL_DESCRIPTION_SOURCES:
        failures.append(
            f"{listing_id}: full description source mapping must resolve UZ and RU base copy"
        )
    metadata_localizations = metadata.get("localizations", {})
    custom_localizations = (
        custom_listing.get("localizations", {})
        if isinstance(custom_listing, dict)
        else {}
    )
    source_locales = {"en-US": "uz-UZ", "ru-RU": "ru-RU"}
    for store_locale, source_locale in source_locales.items():
        source_payload = (
            metadata_localizations.get(source_locale, {})
            if isinstance(metadata_localizations, dict)
            else {}
        )
        store_payload = (
            custom_localizations.get(store_locale, {})
            if isinstance(custom_localizations, dict)
            else {}
        )
        if (
            not isinstance(source_payload, dict)
            or not isinstance(store_payload, dict)
            or store_payload.get("full_description")
            != source_payload.get("description")
        ):
            failures.append(
                f"{listing_id}: {store_locale} full description does not resolve "
                f"{source_locale} base copy"
            )
    if payload.get("localized_asset_roots") != GOOGLE_UZ_LOCALIZED_ASSET_ROOTS:
        failures.append(
            f"{listing_id}: en-US must map to Uzbek assets and ru-RU to Russian assets"
        )
    if payload.get("feature_graphics") != GOOGLE_UZ_FEATURE_GRAPHICS:
        failures.append(f"{listing_id}: localized Google Play feature graphics differ")
    for locale, relative in GOOGLE_UZ_LOCALIZED_ASSET_ROOTS.items():
        if not (root / relative).is_dir():
            failures.append(
                f"{listing_id}: missing localized asset root {locale}: {relative}"
            )
    for locale, relative in GOOGLE_UZ_FEATURE_GRAPHICS.items():
        if not (root / relative).is_file():
            failures.append(
                f"{listing_id}: missing feature graphic {locale}: {relative}"
            )


def validate_listing_payload_ids(
    upload_manifest: object,
    expected_listing_ids: set[str],
    failures: list[str],
) -> None:
    if not isinstance(upload_manifest, dict):
        failures.append("upload manifest must be an object")
        return
    payloads = upload_manifest.get("listing_payloads", [])
    if not isinstance(payloads, list):
        failures.append("upload manifest listing_payloads must be an array")
        return
    payload_ids = [
        payload.get("listing_id")
        for payload in payloads
        if isinstance(payload, dict)
    ]
    duplicates = sorted(
        {
            listing_id
            for listing_id in payload_ids
            if isinstance(listing_id, str) and payload_ids.count(listing_id) > 1
        }
    )
    if duplicates:
        failures.append(f"upload manifest duplicate listing payload ids: {duplicates}")
    if set(payload_ids) != expected_listing_ids:
        failures.append("upload manifest must resolve every listing exactly once")


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
    verify_manifest_artifacts(ROOT, upload_manifest, failures)
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
                or historical_identity > expected_identity
            ):
                failures.append(
                    f"{owner}: historical identity must not exceed current source"
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
            historical_physical_evidence = historical["physical_qa_evidence"]
            if historical_physical_evidence is not None:
                require_evidence_path(
                    historical_physical_evidence,
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
        validate_text_fields(
            locale,
            fields,
            LOCALIZATION_LIMITS,
            failures,
            utf8_byte_fields=APPLE_UTF8_BYTE_FIELDS,
        )
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
        validate_listing_localization_refs(owner, refs, set(localizations), failures)
        for locale, overrides in listing["overrides"].items():
            if locale not in refs:
                failures.append(f"{owner}: override locale {locale} is not referenced")
            validate_text_fields(
                owner + f".overrides.{locale}",
                overrides,
                LOCALIZATION_LIMITS,
                failures,
                exact=False,
                utf8_byte_fields=APPLE_UTF8_BYTE_FIELDS,
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
    validate_app_store_default_metadata(metadata, app_default, failures)

    app_uz = listing_by_id.get("app-store-uz-custom-product-page", {})
    cpp = app_uz.get("custom_product_page", {})
    if not isinstance(cpp, dict) or set(cpp) != APPLE_CPP_FIELDS:
        failures.append(
            "App Store UZ custom product page requires exact localized copy and "
            "keyword fields"
        )
        cpp = {}
    if app_uz.get("storefront") != "UZ" or cpp.get("status") != "draft":
        failures.append("App Store UZ custom product page must remain a UZ draft")
    if (
        cpp.get("audience_locale") != "uz-UZ"
        or cpp.get("store_locale_fallback") != APPLE_UZ_DEFAULT_LOCALE
    ):
        failures.append(
            "App Store UZ custom product page must record the unsupported-locale fallback"
        )
    validate_uz_store_targeting(metadata, configured_generic_terms(), failures)

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
        validate_cpp_upload_mapping(metadata, upload_manifest, failures)
        validate_google_uz_upload_mapping(metadata, upload_manifest, failures)
        payloads = upload_manifest.get("listing_payloads", [])
        validate_listing_payload_ids(upload_manifest, set(listing_by_id), failures)
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
        app_store_default = payload_by_id.get("app-store-default", {})
        if app_store_default.get("asset_locale_aliases") != (
            APP_STORE_DEFAULT_ASSET_LOCALE_ALIASES
        ):
            failures.append(
                "App Store default upload must explicitly reuse en-US assets for en-GB"
            )
        else:
            app_store_locales = set(app_store_default.get("store_locales", []))
            for target_locale, source_locale in (
                APP_STORE_DEFAULT_ASSET_LOCALE_ALIASES.items()
            ):
                if (
                    target_locale not in app_store_locales
                    or source_locale not in app_store_locales
                ):
                    failures.append(
                        "App Store default asset aliases must reference mapped locales"
                    )
        play_default = payload_by_id.get("google-play-default", {})
        if play_default.get("feature_graphic") != (
            "store/assets/google-play/feature-graphic-en-US-1024x500.jpg"
        ):
            failures.append(
                "Google Play default upload must use the en-US feature graphic"
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
