from __future__ import annotations

import base64
import copy
import gzip
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from xml.etree import ElementTree

from PIL import Image

from scripts.build_store_creatives import (
    generated_output_paths,
    generated_source_paths,
    validate_output_sha256_contract,
    validate_source_sha256_contract,
)
from scripts.check_dashboard_report import (
    BACKING_JSON_PATHS,
    EXPECTED_SOURCE_PATHS,
    DashboardConsistencyError,
    verify_dashboard_report,
    verify_dashboard_sources,
)
from scripts.growth.sync_dashboard_report_payload import render_static_fallback
from scripts.check_store_assets import (
    inspect_image,
    load_creative_manifest,
    load_promotional_asset_specs,
    validate_store_image,
)
from scripts.check_store_metadata import (
    APPLE_CPP_FIELDS,
    APPLE_CPP_LOCALIZATION_FIELDS,
    APP_STORE_DEFAULT_ASSET_LOCALE_ALIASES,
    APPLE_UTF8_BYTE_FIELDS,
    APPLE_UZ_DEFAULT_LOCALE,
    EN_APP_STORE_SUBTITLE,
    GOOGLE_CUSTOM_LISTING_FIELDS,
    GOOGLE_CUSTOM_LOCALIZATION_FIELDS,
    GOOGLE_UZ_COUNTRY_LISTING_ID,
    RU_APP_STORE_SUBTITLE,
    RU_TITLE,
    configured_generic_terms,
    validate_cpp_upload_mapping,
    validate_app_store_default_metadata,
    validate_google_uz_upload_mapping,
    validate_listing_localization_refs,
    validate_listing_payload_ids,
    validate_text_fields,
    validate_upload_artifacts,
    validate_uz_store_targeting,
)
from scripts.release_artifact_verifier import verify_manifest_artifacts


ROOT = Path(__file__).resolve().parents[3]


def portable_report(payload: dict) -> str:
    encoded = base64.b64encode(
        gzip.compress(
            json.dumps(payload, separators=(",", ":")).encode("utf-8"),
            mtime=0,
        )
    ).decode("ascii")
    return (
        "<html><body>"
        f"{render_static_fallback(payload)}"
        "<template "
        'id="data-analytics-portable-artifact-payload-source" '
        'data-compression="gzip-base64">'
        f"{encoded}</template></body></html>"
    )


class ValidationScriptsTest(unittest.TestCase):
    def metadata(self) -> dict:
        return json.loads((ROOT / "store/metadata.json").read_text(encoding="utf-8"))

    def upload_manifest(self) -> dict:
        return json.loads(
            (ROOT / "store/upload-manifest-1.1.0.json").read_text(encoding="utf-8")
        )

    def blocked_upload_manifest(self) -> dict:
        manifest = copy.deepcopy(self.upload_manifest())
        historical = {
            "android_phone": {
                "status": "historical-superseded",
                "filename": "nimbo-phone-1.1.0-vc7.aab",
                "version_code": 7,
                "sha256": "e476a124c33854873add9061140f68f1720ff098202b52e7758038bb50f5a77c",
                "signing_evidence": "growth/quality/android-release-artifacts-2026-08-28.md",
                "physical_qa_evidence": "growth/quality/android-physical-smoke-2026-08-28.md",
            },
            "wear_os": {
                "status": "historical-superseded",
                "filename": "nimbo-wear-1.1.0-vc1000008.aab",
                "version_code": 1000008,
                "sha256": "ac19a0eab1a60554db309166f135e754c97205b79c4f5182164a8b21594e7dc6",
                "signing_evidence": "growth/quality/android-release-artifacts-2026-08-28.md",
                "physical_qa_evidence": None,
            },
            "apple": {
                "status": "historical-superseded",
                "filename": "Nimbo.ipa",
                "build": 5,
                "sha256": "b36f8fddb225cd616e3833de6037b6434486ec3cbb9ed06f5cc8deb0627ed4dc",
                "signing_evidence": "growth/quality/apple-release-artifacts-2026-08-28.md",
                "physical_qa_evidence": "growth/quality/apple-runtime-smoke-2026-08-28.md",
            },
        }
        for artifact_id, artifact in manifest["artifacts"].items():
            artifact["source_sync"] = "blocked"
            artifact["sha256"] = None
            artifact["signing_evidence"] = None
            artifact["physical_qa_evidence"] = None
            artifact["historical_candidate"] = historical[artifact_id]
        return manifest

    def test_app_store_default_has_query_first_russian_override(self) -> None:
        listing = next(
            listing
            for listing in self.metadata()["listings"]
            if listing["id"] == "app-store-default"
        )
        self.assertEqual(
            listing["overrides"]["ru-RU"],
            {
                "title": RU_TITLE,
                "subtitle": RU_APP_STORE_SUBTITLE,
            },
        )

    def test_app_store_default_has_benefit_led_english_subtitle(self) -> None:
        metadata = self.metadata()
        listing = next(
            listing
            for listing in metadata["listings"]
            if listing["id"] == "app-store-default"
        )
        for locale in ("en-US", APPLE_UZ_DEFAULT_LOCALE):
            with self.subTest(locale=locale):
                self.assertEqual(
                    listing["overrides"][locale]["title"], "Nimbo Weather"
                )
                self.assertEqual(
                    metadata["localizations"][locale]["subtitle"],
                    EN_APP_STORE_SUBTITLE,
                )
        self.assertLessEqual(len(EN_APP_STORE_SUBTITLE), 30)

    def test_app_store_default_subtitle_drift_fails_contract(self) -> None:
        metadata = self.metadata()
        listing = next(
            listing
            for listing in metadata["listings"]
            if listing["id"] == "app-store-default"
        )
        metadata["localizations"][APPLE_UZ_DEFAULT_LOCALE]["subtitle"] = (
            "Generic weather"
        )
        failures: list[str] = []
        validate_app_store_default_metadata(metadata, listing, failures)
        self.assertIn(
            "app-store-default must preserve the benefit-led en-GB subtitle",
            failures,
        )

    def test_app_store_uz_cpp_uses_documented_default_locale(self) -> None:
        metadata = self.metadata()
        listing = next(
            listing
            for listing in metadata["listings"]
            if listing["id"] == "app-store-uz-custom-product-page"
        )
        cpp = listing["custom_product_page"]
        self.assertEqual(cpp["store_locale_fallback"], APPLE_UZ_DEFAULT_LOCALE)
        self.assertEqual(
            set(cpp["localizations"]),
            {APPLE_UZ_DEFAULT_LOCALE, "ru-RU"},
        )
        payload = next(
            payload
            for payload in self.upload_manifest()["listing_payloads"]
            if payload["listing_id"] == "app-store-uz-custom-product-page"
        )
        self.assertEqual(payload["store_locale_fallback"], APPLE_UZ_DEFAULT_LOCALE)
        self.assertEqual(
            set(payload["localized_asset_roots"]),
            {APPLE_UZ_DEFAULT_LOCALE, "ru-RU"},
        )
        default_payload = next(
            payload
            for payload in self.upload_manifest()["listing_payloads"]
            if payload["listing_id"] == "app-store-default"
        )
        self.assertEqual(
            default_payload["asset_locale_aliases"],
            APP_STORE_DEFAULT_ASSET_LOCALE_ALIASES,
        )

    def test_ios_widget_matches_app_floor_with_guarded_newer_surfaces(self) -> None:
        project = (ROOT / "iosApp/project.yml").read_text(encoding="utf-8")
        generated = (
            ROOT / "iosApp/Nimbo.xcodeproj/project.pbxproj"
        ).read_text(encoding="utf-8")
        widget = (
            ROOT / "iosApp/NimboWidget/NimboWidget.swift"
        ).read_text(encoding="utf-8")

        self.assertRegex(
            project,
            r'(?ms)^  NimboWidget:\n.*?^    deploymentTarget: "15\.0"',
        )
        self.assertEqual(generated.count("IPHONEOS_DEPLOYMENT_TARGET = 15.0;"), 6)
        self.assertNotIn("IPHONEOS_DEPLOYMENT_TARGET = 17.0;", generated)
        for compatibility_contract in (
            "if #available(iOS 16.0, *)",
            "if #available(iOS 17.0, *)",
            "containerBackground(for: .widget)",
            "background(color)",
            ".supportedFamilies(supportedWidgetFamilies)",
        ):
            self.assertIn(compatibility_contract, widget)

    def test_android_widget_rechecks_freshness_without_provider_work(self) -> None:
        widget_info = ElementTree.parse(
            ROOT / "app/src/main/res/xml/weather_widget_info.xml"
        ).getroot()
        update_period = (
            "{http://schemas.android.com/apk/res/android}updatePeriodMillis"
        )
        self.assertEqual(widget_info.get(update_period), "1800000")

        provider = (
            ROOT / "app/src/main/java/uz/ganikhodjaev/weather/WeatherWidgetProvider.kt"
        ).read_text(encoding="utf-8")
        self.assertNotIn("Wearable.", provider)
        self.assertNotIn("OpenMeteo", provider)

    def test_store_inspection_decodes_pixels_and_rejects_truncation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            valid = Path(directory) / "valid.png"
            corrupt = Path(directory) / "corrupt.png"
            Image.new("RGB", (8, 6), "blue").save(valid, format="PNG")
            self.assertEqual(inspect_image(valid), ((8, 6), "PNG", "RGB", False))
            corrupt.write_bytes(valid.read_bytes()[:-20])
            with self.assertRaisesRegex(ValueError, "decode/verification failed"):
                inspect_image(corrupt)

    def test_opaque_rgba_store_screenshot_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            screenshot = Path(directory) / "opaque-rgba.png"
            Image.new("RGBA", (8, 6), (12, 34, 56, 255)).save(screenshot, format="PNG")
            relative = "store/screenshots/google-play/phone-en/opaque-rgba.png"
            self.assertEqual(
                validate_store_image(relative, screenshot, (8, 6), "PNG"),
                [f"{relative}: alpha channel is not allowed"],
            )

    def test_google_play_icon_requires_32_bit_alpha_and_size_limit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rgb = root / "rgb.png"
            rgba = root / "rgba.png"
            Image.new("RGB", (512, 512), "blue").save(rgb, format="PNG")
            Image.new("RGBA", (512, 512), (12, 34, 56, 255)).save(rgba, format="PNG")
            relative = "store/assets/google-play/icon-512.png"
            self.assertIn(
                f"{relative}: must be a 32-bit RGBA image with alpha",
                validate_store_image(
                    relative,
                    rgb,
                    (512, 512),
                    "PNG",
                    require_alpha=True,
                    max_bytes=1024 * 1024,
                ),
            )
            self.assertEqual(
                validate_store_image(
                    relative,
                    rgba,
                    (512, 512),
                    "PNG",
                    require_alpha=True,
                    max_bytes=1024 * 1024,
                ),
                [],
            )
            self.assertTrue(
                any(
                    "exceeds 1-byte store limit" in failure
                    for failure in validate_store_image(
                        relative,
                        rgba,
                        (512, 512),
                        "PNG",
                        require_alpha=True,
                        max_bytes=1,
                    )
                )
            )

    def test_google_promotional_assets_are_hash_locked_and_unsubmitted(self) -> None:
        specs, failures = load_promotional_asset_specs()
        self.assertEqual(failures, [])
        self.assertEqual(
            set(specs),
            {
                "growth/featuring/assets/google-play/nimbo-1.1.0-quick-city-primary-1920x1080.jpg",
                "growth/featuring/assets/google-play/nimbo-1.1.0-quick-city-square-1080x1080.jpg",
            },
        )
        self.assertEqual(
            specs[
                "growth/featuring/assets/google-play/nimbo-1.1.0-quick-city-primary-1920x1080.jpg"
            ]["size"],
            (1920, 1080),
        )
        self.assertEqual(
            specs[
                "growth/featuring/assets/google-play/nimbo-1.1.0-quick-city-square-1080x1080.jpg"
            ]["size"],
            (1080, 1080),
        )

    def test_creative_manifest_uses_locale_matched_watch_sources(self) -> None:
        manifest, failures = load_creative_manifest()
        self.assertEqual(failures, [])
        self.assertEqual(
            manifest["platforms"]["google-play"]["legacy_feature_graphic_locale"],
            "en-US",
        )
        self.assertEqual(
            manifest["source_capture_evidence"],
            "growth/quality/apple-localized-current-product-capture-2026-08-30.md",
        )
        self.assertTrue((ROOT / manifest["source_capture_evidence"]).is_file())
        self.assertEqual(
            [story["app_store_source_name"] for story in manifest["stories"]],
            [
                "01-current.png",
                "02-recent-comparison.png",
                "03-timeline-selected.png",
                "04-details.png",
                "01-current.png",
                "01-current.png",
            ],
        )
        for locale, payload in manifest["locales"].items():
            expected_segment = "en" if locale == "en-US" else locale
            self.assertTrue(
                all(
                    expected_segment in source
                    for source in payload["watch_sources"].values()
                )
            )

        output_paths = generated_output_paths(manifest)
        self.assertEqual(len(output_paths), 40)
        self.assertEqual(len(set(output_paths)), 40)
        self.assertEqual(set(manifest["output_sha256"]), set(output_paths))
        self.assertEqual(validate_output_sha256_contract(manifest, root=ROOT), [])
        source_paths = generated_source_paths(manifest)
        self.assertEqual(len(source_paths), 31)
        self.assertEqual(set(manifest["source_sha256"]), set(source_paths))
        self.assertEqual(validate_source_sha256_contract(manifest, root=ROOT), [])

    def test_creative_manifest_rejects_duplicate_apple_story_compositions(self) -> None:
        manifest, failures = load_creative_manifest()
        self.assertEqual(failures, [])
        duplicated = copy.deepcopy(manifest)
        duplicated["stories"][1]["app_store_source_name"] = duplicated["stories"][0].get(
            "app_store_source_name", "01-current.png"
        )
        duplicated["stories"][1]["app_store_focus"] = duplicated["stories"][0][
            "app_store_focus"
        ]

        with mock.patch("scripts.check_store_assets.CREATIVE_MANIFEST") as manifest_path:
            manifest_path.read_text.return_value = json.dumps(duplicated)
            _, duplicate_failures = load_creative_manifest()

        self.assertIn(
            "the first five App Store stories must use distinct source/focus "
            "compositions",
            duplicate_failures,
        )

    def test_creative_manifest_rejects_out_of_range_story_focus(self) -> None:
        manifest, failures = load_creative_manifest()
        self.assertEqual(failures, [])
        invalid_cases = (
            ("app_store_focus", [-1, 0.5, 1], "invalid App Store source/focus"),
            ("app_store_focus", [0.5, 2, 1], "invalid App Store source/focus"),
            ("app_store_focus", [0.5, 0.5, 0], "invalid App Store source/focus"),
            ("app_store_focus", [True, 0.5, 1], "invalid App Store source/focus"),
            ("google_focus", [0.5, 0.5, 0], "invalid Google Play focus"),
        )
        with mock.patch("scripts.check_store_assets.CREATIVE_MANIFEST") as manifest_path:
            for focus_key, focus, expected in invalid_cases:
                with self.subTest(focus_key=focus_key, focus=focus):
                    mutated = copy.deepcopy(manifest)
                    mutated["stories"][0][focus_key] = focus
                    manifest_path.read_text.return_value = json.dumps(mutated)
                    _, invalid_failures = load_creative_manifest()
                    self.assertTrue(
                        any(expected in failure for failure in invalid_failures),
                        invalid_failures,
                    )

    def test_creative_manifest_rejects_escaping_capture_evidence(self) -> None:
        manifest, failures = load_creative_manifest()
        self.assertEqual(failures, [])
        manifest["source_capture_evidence"] = "growth/quality/../../README.md"
        with mock.patch("scripts.check_store_assets.CREATIVE_MANIFEST") as manifest_path:
            manifest_path.read_text.return_value = json.dumps(manifest)
            _, invalid_failures = load_creative_manifest()
        self.assertIn(
            "creative manifest must reference checked-in source capture evidence",
            invalid_failures,
        )

    def test_creative_output_contract_rejects_path_set_mutations(self) -> None:
        manifest, failures = load_creative_manifest()
        self.assertEqual(failures, [])
        relative = next(iter(manifest["output_sha256"]))

        missing = copy.deepcopy(manifest)
        missing["output_sha256"].pop(relative)
        self.assertIn(
            f"creative output SHA-256 contract is missing: {relative}",
            validate_output_sha256_contract(missing, root=ROOT, verify_files=False),
        )

        unexpected = copy.deepcopy(manifest)
        unexpected["output_sha256"]["store/creatives/unexpected.png"] = "0" * 64
        self.assertIn(
            "creative output SHA-256 contract has unexpected paths: "
            "store/creatives/unexpected.png",
            validate_output_sha256_contract(unexpected, root=ROOT, verify_files=False),
        )

    def test_creative_output_contract_rejects_byte_mutation(self) -> None:
        manifest = {
            "platforms": {
                "app-store": {"output_dir": "generated/app-store"},
                "google-play": {
                    "output_dir": "generated/google-play",
                    "feature_graphics": {
                        "en-US": {"output": "generated/feature-en.jpg"}
                    },
                    "legacy_feature_graphic": "generated/feature-legacy.jpg",
                },
            },
            "locales": {"en-US": {}},
            "stories": [{"filename": "01.png"}],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in generated_output_paths(manifest):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(f"asset:{relative}".encode())
            manifest["output_sha256"] = {
                relative: hashlib.sha256((root / relative).read_bytes()).hexdigest()
                for relative in generated_output_paths(manifest)
            }
            self.assertEqual(validate_output_sha256_contract(manifest, root=root), [])

            mutated = generated_output_paths(manifest)[0]
            (root / mutated).write_bytes(b"replacement-with-different-bytes")
            self.assertTrue(
                any(
                    failure.startswith(f"{mutated}: SHA-256 drift")
                    for failure in validate_output_sha256_contract(manifest, root=root)
                )
            )

    def test_creative_source_contract_rejects_byte_mutation(self) -> None:
        manifest = {
            "platforms": {
                "app-store": {"phone_source": "sources/apple-{source_locale}.png"},
                "google-play": {
                    "phone_source": "sources/google-{source_locale}-{source_name}",
                    "feature_graphic_source": "sources/icon.png",
                },
            },
            "locales": {
                "en-US": {
                    "source_locale": "en",
                    "watch_sources": {
                        "app-store": "sources/apple-watch.png",
                        "google-play": "sources/google-watch.png",
                    },
                }
            },
            "stories": [{"google_source_name": "screen.png"}],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in generated_source_paths(manifest):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(f"source:{relative}".encode())
            manifest["source_sha256"] = {
                relative: hashlib.sha256((root / relative).read_bytes()).hexdigest()
                for relative in generated_source_paths(manifest)
            }
            self.assertEqual(validate_source_sha256_contract(manifest, root=root), [])

            mutated = generated_source_paths(manifest)[0]
            (root / mutated).write_bytes(b"replacement-source")
            self.assertTrue(
                any(
                    failure.startswith(f"{mutated}: source SHA-256 drift")
                    for failure in validate_source_sha256_contract(manifest, root=root)
                )
            )

    def test_upload_artifacts_match_source_and_preserve_fail_closed_state(self) -> None:
        failures: list[str] = []
        validate_upload_artifacts(self.upload_manifest(), "1.1.0", failures)
        self.assertEqual(failures, [])

    def test_blocked_upload_artifact_cannot_claim_current_evidence(self) -> None:
        invalid_values = {
            "sha256": "0" * 64,
            "signing_evidence": (
                "growth/quality/android-release-artifacts-2026-08-28.md"
            ),
            "physical_qa_evidence": (
                "growth/quality/android-physical-smoke-2026-08-28.md"
            ),
        }
        for field, value in invalid_values.items():
            with self.subTest(field=field):
                manifest = self.blocked_upload_manifest()
                manifest["artifacts"]["android_phone"][field] = value
                failures: list[str] = []
                validate_upload_artifacts(manifest, "1.1.0", failures)
                self.assertIn(
                    "upload manifest artifact android_phone: blocked artifact "
                    f"must keep {field} null",
                    failures,
                )

    def test_upload_artifact_identity_must_match_source(self) -> None:
        manifest = copy.deepcopy(self.upload_manifest())
        source_build = manifest["artifacts"]["apple"]["build"]
        invalid_build = source_build - 1
        manifest["artifacts"]["apple"]["build"] = invalid_build
        failures: list[str] = []
        validate_upload_artifacts(manifest, "1.1.0", failures)
        self.assertTrue(
            any(
                f"declared build {invalid_build} differs from source {source_build}" in item
                for item in failures
            )
        )

    def test_historical_hashes_cannot_be_relabelled_as_current_bytes(self) -> None:
        manifest = self.blocked_upload_manifest()
        canonical = self.upload_manifest()["artifacts"]
        for artifact_id, artifact in manifest["artifacts"].items():
            historical = artifact["historical_candidate"]
            artifact["source_sync"] = "verified-current"
            artifact["sha256"] = historical["sha256"]
            artifact["signing_evidence"] = historical["signing_evidence"]
            artifact["physical_qa_evidence"] = None
            artifact["source_sync_evidence"] = canonical[artifact_id][
                "source_sync_evidence"
            ]
            artifact["historical_candidate"] = None
        failures: list[str] = []

        with mock.patch.dict(
            "os.environ",
            {"NIMBO_RELEASE_ARTIFACT_ROOT": ""},
            clear=False,
        ):
            verify_manifest_artifacts(ROOT, manifest, failures)

        for artifact_id in ("android_phone", "wear_os", "apple"):
            self.assertIn(
                f"upload manifest artifact {artifact_id}: verified-current "
                "requires real artifact bytes through NIMBO_RELEASE_ARTIFACT_ROOT",
                failures,
            )

    def test_blocked_artifact_can_preserve_same_version_historical_bytes(self) -> None:
        manifest = self.blocked_upload_manifest()
        wear = manifest["artifacts"]["wear_os"]
        self.assertEqual(wear["source_sync"], "blocked")
        wear["historical_candidate"]["version_code"] = wear["version_code"]
        self.assertEqual(
            wear["historical_candidate"]["version_code"], wear["version_code"]
        )
        self.assertIsNone(wear["historical_candidate"]["physical_qa_evidence"])

        failures: list[str] = []
        validate_upload_artifacts(manifest, "1.1.0", failures)
        self.assertEqual(failures, [])

        wear["historical_candidate"]["version_code"] = wear["version_code"] + 1
        failures = []
        validate_upload_artifacts(manifest, "1.1.0", failures)
        self.assertIn(
            "upload manifest artifact wear_os: historical identity must not "
            "exceed current source",
            failures,
        )

    def test_apple_keyword_limit_uses_utf8_bytes(self) -> None:
        failures: list[str] = []
        validate_text_fields(
            "synthetic",
            {"keywords": "я" * 51},
            {"keywords": 100},
            failures,
            utf8_byte_fields=APPLE_UTF8_BYTE_FIELDS,
        )
        self.assertEqual(
            failures,
            ["synthetic:keywords: 102 UTF-8 bytes > 100"],
        )

        failures = []
        validate_text_fields(
            "synthetic",
            {"keywords": "a" * 100},
            {"keywords": 100},
            failures,
            utf8_byte_fields=APPLE_UTF8_BYTE_FIELDS,
        )
        self.assertEqual(failures, [])

    def test_uz_store_targeting_copy_and_apple_candidates_match_contract(self) -> None:
        metadata = self.metadata()
        generic_terms = configured_generic_terms()
        failures: list[str] = []
        validate_uz_store_targeting(metadata, generic_terms, failures)
        self.assertEqual(failures, [])

        google_custom_ids = {
            listing["id"]
            for listing in metadata["listings"]
            if listing["platform"] == "google-play"
            and listing["listing_type"] == "custom-listing"
        }
        self.assertEqual(google_custom_ids, {GOOGLE_UZ_COUNTRY_LISTING_ID})

        country_listing = next(
            listing
            for listing in metadata["listings"]
            if listing["id"] == GOOGLE_UZ_COUNTRY_LISTING_ID
        )
        uz_title = country_listing["custom_listing"]["localizations"]["en-US"][
            "title"
        ]
        self.assertEqual(uz_title, "Nimbo Weather: Ob-havo")
        self.assertLessEqual(len(uz_title), 30)
        for title_term in ("weather", "ob-havo"):
            self.assertIn(title_term, uz_title.casefold())

        uz_short = country_listing["custom_listing"]["localizations"]["en-US"][
            "short_description"
        ]
        self.assertEqual(
            uz_short,
            "Toshkent va O‘zbekiston ob-havosi: chiqish uchun eng yaxshi vaqtni toping.",
        )
        self.assertLessEqual(len(uz_short), 80)
        for local_term in ("Toshkent", "O‘zbekiston", "ob-havo"):
            self.assertIn(local_term, uz_short)

        schema = json.loads(
            (ROOT / "store/metadata.schema.json").read_text(encoding="utf-8")
        )
        custom_listing_schema = schema["$defs"]["customListing"]
        self.assertEqual(
            set(custom_listing_schema["properties"]["targeting"]["properties"]),
            {"type", "country_targets"},
        )
        self.assertEqual(
            schema["$defs"]["customProductPage"]["properties"]
            ["keyword_assignment_gate"]["properties"]["status"],
            {"const": "blocked-pending-base-version-approval"},
        )

        impossible_combination = copy.deepcopy(metadata)
        country_listing = next(
            listing
            for listing in impossible_combination["listings"]
            if listing["id"] == GOOGLE_UZ_COUNTRY_LISTING_ID
        )
        country_listing["custom_listing"]["targeting"][
            "search_keyword_targets"
        ] = generic_terms
        failures = []
        validate_uz_store_targeting(
            impossible_combination, generic_terms, failures
        )
        self.assertIn(
            f"{GOOGLE_UZ_COUNTRY_LISTING_ID}: targeting must be country UZ only",
            failures,
        )

        wrong_default = copy.deepcopy(metadata)
        country_listing = next(
            listing
            for listing in wrong_default["listings"]
            if listing["id"] == GOOGLE_UZ_COUNTRY_LISTING_ID
        )
        country_listing["custom_listing"]["default_store_locale"] = "ru-RU"
        failures = []
        validate_uz_store_targeting(wrong_default, generic_terms, failures)
        self.assertIn(
            f"{GOOGLE_UZ_COUNTRY_LISTING_ID}: default_store_locale must be en-US",
            failures,
        )

        wrong_description = copy.deepcopy(metadata)
        country_listing = next(
            listing
            for listing in wrong_description["listings"]
            if listing["id"] == GOOGLE_UZ_COUNTRY_LISTING_ID
        )
        country_listing["custom_listing"]["localizations"]["en-US"][
            "full_description"
        ] += " Changed."
        failures = []
        validate_uz_store_targeting(wrong_description, generic_terms, failures)
        self.assertIn(
            f"{GOOGLE_UZ_COUNTRY_LISTING_ID}: localized copy or "
            "audience/store-locale mapping differs",
            failures,
        )

        oversized_description = copy.deepcopy(metadata)
        country_listing = next(
            listing
            for listing in oversized_description["listings"]
            if listing["id"] == GOOGLE_UZ_COUNTRY_LISTING_ID
        )
        country_listing["custom_listing"]["localizations"]["en-US"][
            "full_description"
        ] = "x" * 4001
        failures = []
        validate_uz_store_targeting(
            oversized_description, generic_terms, failures
        )
        self.assertTrue(
            any("full_description: 4001 characters > 4000" in item for item in failures)
        )

        invalid_apple = copy.deepcopy(metadata)
        invalid_apple["localizations"][APPLE_UZ_DEFAULT_LOCALE]["keywords"] = (
            "weather,forecast"
        )
        failures = []
        validate_uz_store_targeting(invalid_apple, generic_terms, failures)
        self.assertTrue(
            any(
                "planned targets missing from the candidate base Apple keyword pool"
                in item
                for item in failures
            )
        )

        premature_apple_assignment = copy.deepcopy(metadata)
        cpp_listing = next(
            listing
            for listing in premature_apple_assignment["listings"]
            if listing["id"] == "app-store-uz-custom-product-page"
        )
        cpp_listing["custom_product_page"]["keyword_assignment_gate"][
            "status"
        ] = "assigned"
        failures = []
        validate_uz_store_targeting(
            premature_apple_assignment, generic_terms, failures
        )
        self.assertIn(
            "App Store UZ custom product page keyword assignment must remain "
            "blocked until the candidate base version is approved",
            failures,
        )

    def test_store_payload_shapes_match_json_schema(self) -> None:
        schema = json.loads(
            (ROOT / "store/metadata.schema.json").read_text(encoding="utf-8")
        )
        contracts = (
            (schema["$defs"]["customListing"], GOOGLE_CUSTOM_LISTING_FIELDS),
            (
                schema["$defs"]["customListing"]["properties"]["localizations"]
                ["additionalProperties"],
                GOOGLE_CUSTOM_LOCALIZATION_FIELDS,
            ),
            (schema["$defs"]["customProductPage"], APPLE_CPP_FIELDS),
            (
                schema["$defs"]["customProductPage"]["properties"][
                    "localizations"
                ]["additionalProperties"],
                APPLE_CPP_LOCALIZATION_FIELDS,
            ),
        )
        for payload_schema, expected_fields in contracts:
            with self.subTest(fields=sorted(expected_fields)):
                self.assertFalse(payload_schema["additionalProperties"])
                self.assertEqual(set(payload_schema["required"]), expected_fields)
                self.assertEqual(set(payload_schema["properties"]), expected_fields)

    def test_store_payload_shapes_fail_closed(self) -> None:
        generic_terms = configured_generic_terms()

        extra_cpp_field = self.metadata()
        cpp = next(
            listing["custom_product_page"]
            for listing in extra_cpp_field["listings"]
            if listing["id"] == "app-store-uz-custom-product-page"
        )
        cpp["localizations"][APPLE_UZ_DEFAULT_LOCALE]["keyword_targets"] = [
            "weather"
        ]
        failures: list[str] = []
        validate_uz_store_targeting(extra_cpp_field, generic_terms, failures)
        self.assertIn(
            "app-store-uz-custom-product-page.en-GB: expected exactly "
            f"{sorted(APPLE_CPP_LOCALIZATION_FIELDS)}",
            failures,
        )

        extra_cpp_payload_field = self.metadata()
        cpp = next(
            listing["custom_product_page"]
            for listing in extra_cpp_payload_field["listings"]
            if listing["id"] == "app-store-uz-custom-product-page"
        )
        cpp["keyword_targets"] = ["weather"]
        failures = []
        validate_uz_store_targeting(
            extra_cpp_payload_field, generic_terms, failures
        )
        self.assertIn(
            "App Store UZ custom product page fields must be exact and explicit",
            failures,
        )

        missing_cpp_field = self.metadata()
        cpp = next(
            listing["custom_product_page"]
            for listing in missing_cpp_field["listings"]
            if listing["id"] == "app-store-uz-custom-product-page"
        )
        cpp["localizations"][APPLE_UZ_DEFAULT_LOCALE].pop(
            "planned_keyword_targets"
        )
        failures = []
        validate_uz_store_targeting(missing_cpp_field, generic_terms, failures)
        self.assertIn(
            "app-store-uz-custom-product-page.en-GB: expected exactly "
            f"{sorted(APPLE_CPP_LOCALIZATION_FIELDS)}",
            failures,
        )

        extra_google_field = self.metadata()
        custom_listing = next(
            listing["custom_listing"]
            for listing in extra_google_field["listings"]
            if listing["id"] == GOOGLE_UZ_COUNTRY_LISTING_ID
        )
        custom_listing["localizations"]["en-US"]["unsupported"] = True
        failures = []
        validate_uz_store_targeting(extra_google_field, generic_terms, failures)
        self.assertIn(
            f"{GOOGLE_UZ_COUNTRY_LISTING_ID}.en-US: expected exactly "
            f"{sorted(GOOGLE_CUSTOM_LOCALIZATION_FIELDS)}",
            failures,
        )

        empty_google_name = self.metadata()
        custom_listing = next(
            listing["custom_listing"]
            for listing in empty_google_name["listings"]
            if listing["id"] == GOOGLE_UZ_COUNTRY_LISTING_ID
        )
        custom_listing["name"] = "  "
        failures = []
        validate_uz_store_targeting(empty_google_name, generic_terms, failures)
        self.assertIn(
            f"{GOOGLE_UZ_COUNTRY_LISTING_ID}: custom listing name must be non-empty",
            failures,
        )

        empty_cpp_name = self.metadata()
        cpp = next(
            listing["custom_product_page"]
            for listing in empty_cpp_name["listings"]
            if listing["id"] == "app-store-uz-custom-product-page"
        )
        cpp["reference_name"] = ""
        failures = []
        validate_uz_store_targeting(empty_cpp_name, generic_terms, failures)
        self.assertIn(
            "App Store UZ custom product page reference_name must be non-empty",
            failures,
        )

    def test_listing_localization_refs_reject_duplicates(self) -> None:
        failures: list[str] = []
        validate_listing_localization_refs(
            "synthetic",
            ["en-US", "en-US"],
            {"en-US", "ru-RU"},
            failures,
        )
        self.assertEqual(
            failures,
            ["synthetic: localization_refs must be unique"],
        )

    def test_cpp_upload_assets_are_explicit_per_store_locale(self) -> None:
        metadata = self.metadata()
        manifest = self.upload_manifest()
        failures: list[str] = []
        validate_cpp_upload_mapping(metadata, manifest, failures)
        self.assertEqual(failures, [])

        invalid = copy.deepcopy(manifest)
        cpp_payload = next(
            payload
            for payload in invalid["listing_payloads"]
            if payload["listing_id"] == "app-store-uz-custom-product-page"
        )
        cpp_payload["localized_asset_roots"].pop("ru-RU")
        failures = []
        validate_cpp_upload_mapping(metadata, invalid, failures)
        self.assertIn(
            "App Store UZ upload locale, copy, and localized asset mappings differ",
            failures,
        )

        ambiguous = copy.deepcopy(manifest)
        cpp_payload = next(
            payload
            for payload in ambiguous["listing_payloads"]
            if payload["listing_id"] == "app-store-uz-custom-product-page"
        )
        cpp_payload["asset_root"] = cpp_payload["localized_asset_roots"][
            APPLE_UZ_DEFAULT_LOCALE
        ]
        failures = []
        validate_cpp_upload_mapping(metadata, ambiguous, failures)
        self.assertIn(
            "App Store UZ upload requires exactly one explicit localized asset map",
            failures,
        )

        duplicated = copy.deepcopy(manifest)
        duplicated["listing_payloads"].append(copy.deepcopy(cpp_payload))
        failures = []
        validate_cpp_upload_mapping(metadata, duplicated, failures)
        self.assertIn(
            "App Store UZ upload requires exactly one CPP payload; found 2",
            failures,
        )

    def test_google_uz_country_upload_resolves_copy_and_supported_locales(self) -> None:
        metadata = self.metadata()
        manifest = self.upload_manifest()
        failures: list[str] = []
        validate_google_uz_upload_mapping(metadata, manifest, failures)
        self.assertEqual(failures, [])
        self.assertFalse(
            any(
                payload.get("targeting", {}).get("type") == "search-keywords"
                for payload in manifest["listing_payloads"]
            )
        )

        impossible_combination = copy.deepcopy(manifest)
        country_payload = next(
            payload
            for payload in impossible_combination["listing_payloads"]
            if payload["listing_id"] == GOOGLE_UZ_COUNTRY_LISTING_ID
        )
        country_payload["targeting"]["search_keyword_targets"] = (
            configured_generic_terms()
        )
        failures = []
        validate_google_uz_upload_mapping(
            metadata, impossible_combination, failures
        )
        self.assertIn(
            f"{GOOGLE_UZ_COUNTRY_LISTING_ID}: upload targeting differs from metadata",
            failures,
        )

        unsupported_locale = copy.deepcopy(manifest)
        country_payload = next(
            payload
            for payload in unsupported_locale["listing_payloads"]
            if payload["listing_id"] == GOOGLE_UZ_COUNTRY_LISTING_ID
        )
        country_payload["store_locales"][0] = "uz-UZ"
        failures = []
        validate_google_uz_upload_mapping(metadata, unsupported_locale, failures)
        self.assertIn(
            f"{GOOGLE_UZ_COUNTRY_LISTING_ID}: upload store locales must be en-US "
            "plus ru-RU",
            failures,
        )

        wrong_assets = copy.deepcopy(manifest)
        country_payload = next(
            payload
            for payload in wrong_assets["listing_payloads"]
            if payload["listing_id"] == GOOGLE_UZ_COUNTRY_LISTING_ID
        )
        country_payload["localized_asset_roots"]["en-US"] = (
            country_payload["localized_asset_roots"]["ru-RU"]
        )
        failures = []
        validate_google_uz_upload_mapping(metadata, wrong_assets, failures)
        self.assertIn(
            f"{GOOGLE_UZ_COUNTRY_LISTING_ID}: en-US must map to Uzbek assets and "
            "ru-RU to Russian assets",
            failures,
        )

        wrong_copy_sources = copy.deepcopy(manifest)
        country_payload = next(
            payload
            for payload in wrong_copy_sources["listing_payloads"]
            if payload["listing_id"] == GOOGLE_UZ_COUNTRY_LISTING_ID
        )
        country_payload["full_description_sources"]["en-US"] = (
            "metadata.localizations.en-US.description"
        )
        failures = []
        validate_google_uz_upload_mapping(metadata, wrong_copy_sources, failures)
        self.assertIn(
            f"{GOOGLE_UZ_COUNTRY_LISTING_ID}: full description source mapping "
            "must resolve UZ and RU base copy",
            failures,
        )

        wrong_copy = copy.deepcopy(metadata)
        country_listing = next(
            listing
            for listing in wrong_copy["listings"]
            if listing["id"] == GOOGLE_UZ_COUNTRY_LISTING_ID
        )
        country_listing["custom_listing"]["localizations"]["en-US"][
            "full_description"
        ] += " Changed."
        failures = []
        validate_google_uz_upload_mapping(wrong_copy, manifest, failures)
        self.assertIn(
            f"{GOOGLE_UZ_COUNTRY_LISTING_ID}: en-US full description does not "
            "resolve uz-UZ base copy",
            failures,
        )

    def test_listing_payload_ids_reject_duplicates(self) -> None:
        manifest = self.upload_manifest()
        expected_ids = {
            listing["id"] for listing in self.metadata()["listings"]
        }
        failures: list[str] = []
        validate_listing_payload_ids(manifest, expected_ids, failures)
        self.assertEqual(failures, [])

        duplicated = copy.deepcopy(manifest)
        duplicated["listing_payloads"].append(
            copy.deepcopy(duplicated["listing_payloads"][0])
        )
        failures = []
        validate_listing_payload_ids(duplicated, expected_ids, failures)
        self.assertIn(
            "upload manifest duplicate listing payload ids: ['app-store-default']",
            failures,
        )

    def test_featuring_operational_blockers_use_canonical_gate_ids(self) -> None:
        featuring = json.loads(
            (ROOT / "growth/featuring/manifest.json").read_text(encoding="utf-8")
        )
        gates = json.loads(
            (ROOT / "growth/quality/gates.json").read_text(encoding="utf-8")
        )["gates"]
        operational = {
            blocker["id"]: blocker
            for blocker in featuring["blockers"]
            if blocker["blocker_type"] == "operational_gate"
        }
        expected = {
            gate_id: gate
            for gate_id, gate in gates.items()
            if gate["status"] != "pass"
        }
        self.assertEqual(set(operational), set(expected))
        for gate_id, gate in expected.items():
            self.assertEqual(operational[gate_id]["status"], gate["status"])
            self.assertEqual(
                operational[gate_id]["evidence"], "growth/quality/gates.json"
            )
        deliverable_ids = {
            blocker["id"]
            for blocker in featuring["blockers"]
            if blocker["blocker_type"] == "deliverable"
        }
        self.assertTrue(
            all(identifier.startswith("deliverable.") for identifier in deliverable_ids)
        )

    def test_dashboard_report_must_embed_exact_canonical_artifact(self) -> None:
        artifact = {
            "surface": "dashboard",
            "manifest": {
                "title": "Nimbo dashboard test",
                "generatedAt": "2026-08-28T00:00:00Z",
                "cards": [],
                "charts": [],
                "tables": [],
                "blocks": [],
            },
            "snapshot": {
                "status": "partial",
                "accessIssues": [],
                "datasets": {},
            },
            "sources": [],
        }
        embedded = {"ok": True, "widget_type": "artifact", **artifact}
        with tempfile.TemporaryDirectory() as directory:
            artifact_path = Path(directory) / "artifact.json"
            report_path = Path(directory) / "report.html"
            artifact_path.write_text(json.dumps(artifact))
            report_path.write_text(portable_report(embedded))
            verify_dashboard_report(artifact_path, report_path)

            artifact["snapshot"]["status"] = "complete"
            artifact_path.write_text(json.dumps(artifact))
            with self.assertRaisesRegex(
                DashboardConsistencyError, "does not match artifact.json"
            ):
                verify_dashboard_report(artifact_path, report_path)

    def test_dashboard_report_rejects_stale_static_fallback(self) -> None:
        artifact = {
            "surface": "dashboard",
            "manifest": {
                "title": "Nimbo dashboard test",
                "generatedAt": "2026-08-31T18:00:00Z",
                "cards": [],
                "charts": [],
                "tables": [],
                "blocks": [],
            },
            "snapshot": {
                "status": "blocked",
                "accessIssues": [],
                "datasets": {},
            },
            "sources": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            artifact_path = Path(directory) / "artifact.json"
            report_path = Path(directory) / "report.html"
            artifact_path.write_text(json.dumps(artifact))
            report_path.write_text(
                portable_report(artifact).replace(
                    "Nimbo dashboard test", "Stale dashboard title", 1
                )
            )
            with self.assertRaisesRegex(
                DashboardConsistencyError, "static fallback does not match"
            ):
                verify_dashboard_report(artifact_path, report_path)

    def test_dashboard_cited_inputs_are_mutation_checked(self) -> None:
        artifact = json.loads(
            (ROOT / "growth/dashboard/artifact.json").read_text(encoding="utf-8")
        )
        source_paths = set(EXPECTED_SOURCE_PATHS.values()) | set(
            BACKING_JSON_PATHS.values()
        )
        json_mutations = (
            (
                BACKING_JSON_PATHS["baseline"],
                ("platforms", "apple", "metrics", "reported_impressions"),
                207,
            ),
            (
                BACKING_JSON_PATHS["rank"],
                ("surfaces", "apple", "search", "weather", "target_rank"),
                80,
            ),
            (
                BACKING_JSON_PATHS["rank"],
                ("goal_evidence_complete",),
                False,
            ),
            (
                BACKING_JSON_PATHS["evaluation"],
                ("top10_goal", "current_streak_days"),
                1,
            ),
            (
                BACKING_JSON_PATHS["evaluation"],
                ("guardrails", "metric_guardrails", 0, "status"),
                "pass",
            ),
            (
                BACKING_JSON_PATHS["framework"],
                (
                    "primary_goal",
                    "daily_requirements",
                    "apple_weather_chart_rank_lte",
                ),
                9,
            ),
            (
                BACKING_JSON_PATHS["gates"],
                ("gates", "ios_crash_gate", "reason"),
                "synthetic stale gate evidence",
            ),
        )
        for relative, field_path, replacement in json_mutations:
            with self.subTest(source=relative), tempfile.TemporaryDirectory() as directory:
                temporary_root = Path(directory)
                for source in source_paths:
                    destination = temporary_root / source
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(ROOT / source, destination)
                verify_dashboard_sources(artifact, repo_root=temporary_root)
                source_file = temporary_root / relative
                payload = json.loads(source_file.read_text(encoding="utf-8"))
                target = payload
                for field in field_path[:-1]:
                    target = target[field]
                target[field_path[-1]] = replacement
                source_file.write_text(json.dumps(payload), encoding="utf-8")
                with self.assertRaises(DashboardConsistencyError):
                    verify_dashboard_sources(artifact, repo_root=temporary_root)

        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            for source in source_paths:
                destination = temporary_root / source
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / source, destination)
            sql_path = temporary_root / EXPECTED_SOURCE_PATHS["gate_snapshot"]
            sql_path.write_text(
                sql_path.read_text(encoding="utf-8") + "\nSELECT 1;\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(DashboardConsistencyError, "SQL differs"):
                verify_dashboard_sources(artifact, repo_root=temporary_root)

    def test_local_ci_is_authoritative_and_hosted_fallback_is_manual(self) -> None:
        ci = (ROOT / ".github/workflows/ci.yml").read_text()
        local_ci = (ROOT / "scripts/local-ci.sh").read_text()
        android_ui = (ROOT / "scripts/run_local_android_ui_matrix.sh").read_text()
        device_test = (ROOT / "scripts/run_android_ui_ci.sh").read_text()
        timeout_runner = (ROOT / "scripts/run_with_timeout.py").read_text()

        self.assertTrue(
            ci.startswith(
                "name: Manual hosted CI fallback\n\non:\n  workflow_dispatch:\n"
            )
        )
        self.assertNotRegex(ci, r"(?m)^  (?:pull_request|push|schedule):")
        self.assertIn("python3 -m compileall -q scripts", local_ci)
        self.assertIn("python3 -m unittest discover -s scripts/growth/tests", local_ci)
        self.assertIn("python3 scripts/trusted_release_workflow_security.py", local_ci)
        self.assertIn(
            "python3 scripts/verify_release_artifacts.py --contract-only", local_ci
        )
        self.assertIn(
            "python3 scripts/check_release_qa_matrix.py --contract-only", local_ci
        )
        self.assertIn("permissions: {}", ci)
        self.assertNotIn("actions/checkout@", ci)
        self.assertEqual(ci.count("Checkout exact public source without credentials"), 3)
        self.assertIn("python3 scripts/check_dashboard_report.py", local_ci)
        self.assertIn("Pillow==12.2.0", ci)
        self.assertIn("command -v ffprobe", ci)
        self.assertIn("command -v ffmpeg", ci)
        self.assertIn(":app:testDebugUnitTest", local_ci)
        self.assertIn(":wearApp:testDebugUnitTest", local_ci)
        self.assertIn("./gradlew :shared:iosSimulatorArm64Test", local_ci)
        self.assertIn("bash scripts/test_ios_surfaces.sh", local_ci)
        self.assertIn("bash scripts/local-ci.sh core", ci)
        self.assertIn("bash scripts/local-ci.sh apple", ci)
        self.assertEqual(ci.count('java-version: "17"'), 3)
        self.assertEqual(ci.count('python-version: "3.11"'), 3)
        self.assertIn('java_version" != "17"', local_ci)
        self.assertIn("sys.version_info[:2] != (3, 11)", local_ci)
        for workflow in (ROOT / ".github/workflows").glob("*.yml"):
            workflow_text = workflow.read_text()
            self.assertNotRegex(workflow_text, r"(?m)^  (?:pull_request|push):")
            self.assertFalse(workflow_text.startswith("name: CI\n"))
        self.assertIn("shared/build/test-results/iosSimulatorArm64Test", ci)
        self.assertIn("shared/build/reports/tests/iosSimulatorArm64Test", ci)
        kvm_chmod = ci.index("sudo chmod 0666 /dev/kvm")
        kvm_rw_check = ci.index("test -r /dev/kvm && test -w /dev/kvm")
        self.assertLess(kvm_chmod, kvm_rw_check)
        self.assertIn("disable-linux-hw-accel: false", ci)
        self.assertIn("-accel on", ci)
        self.assertNotIn("disable-linux-hw-accel: true", ci)
        for matrix_name in ("phone-api24", "phone-api36", "tablet-api36"):
            self.assertIn(f"run_matrix_entry {matrix_name}", android_ui)
        self.assertIn("ANDROID_SERIAL=", android_ui)
        self.assertIn("scripts/run_with_timeout.py 1680 60", device_test)
        self.assertNotRegex(device_test, r"(?m)^timeout ")
        self.assertIn("os.killpg", timeout_runner)

        build_site = (ROOT / "scripts/build_site.py").read_text()
        self.assertIn("verify_dashboard_report(artifact, source)", build_site)

        pages = (ROOT / ".github/workflows/pages.yml").read_text()
        for action in (
            "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
            "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97",
            "actions/configure-pages@45bfe0192ca1faeb007ade9deae92b16b8254a0d",
            "actions/upload-pages-artifact@fc324d3547104276b827a68afc52ff2a11cc49c9",
            "actions/deploy-pages@cd2ce8fcbc39b97be8ca5fce6e763baed58fa128",
        ):
            self.assertIn(action, pages)
        self.assertNotRegex(pages, r"(?m)^\s*uses:\s+[^@\s]+@v\d+\s*$")
        self.assertIn("workflow_run:", pages)
        self.assertIn("- Trusted release verification", pages)
        self.assertIn("workflow_run.conclusion == 'success'", pages)
        self.assertIn("workflow_run.head_branch == 'master'", pages)
        self.assertIn("python3 scripts/verify_release_artifacts.py --contract-only", pages)
        self.assertIn("python3 scripts/check_release_qa_matrix.py --contract-only", pages)
        self.assertNotRegex(pages, r"(?m)^\s{2}push:\s*$")
        self.assertNotIn("workflow_dispatch", pages)


if __name__ == "__main__":
    unittest.main()
