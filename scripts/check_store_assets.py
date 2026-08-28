#!/usr/bin/env python3
"""Validate version-controlled store graphics before release."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

try:
    from scripts.build_store_creatives import (
        validate_output_sha256_contract,
        validate_source_sha256_contract,
    )
except ModuleNotFoundError:  # Direct execution: python3 scripts/check_store_assets.py
    from build_store_creatives import (
        validate_output_sha256_contract,
        validate_source_sha256_contract,
    )

ROOT = Path(__file__).resolve().parents[1]
CREATIVE_MANIFEST = ROOT / "store/creative-sets/growth-2026-08.json"
GOOGLE_PLAY_ICON = "store/assets/google-play/icon-512.png"
GOOGLE_PLAY_ICON_MAX_BYTES = 1024 * 1024

STORE_LOCALES = (
    "en",
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
)

EXPECTED = {
    "store/assets/google-play/icon-512.png": ((512, 512), "PNG"),
    "store/assets/google-play/feature-graphic-1024x500.jpg": ((1024, 500), "JPEG"),
    "store/screenshots/google-play/wear-os-en/01-current.jpg": ((480, 480), "JPEG"),
    "store/screenshots/google-play/wear-os-ru-RU/01-current.png": ((480, 480), "PNG"),
    "store/screenshots/google-play/wear-os-uz-UZ/01-current.png": ((480, 480), "PNG"),
    "store/screenshots/app-store/apple-watch-en/01-current.jpg": ((416, 496), "JPEG"),
    "store/screenshots/app-store/apple-watch-ru-RU/01-current.png": ((416, 496), "PNG"),
    "store/screenshots/app-store/apple-watch-uz-UZ/01-current.png": ((416, 496), "PNG"),
}

for locale in STORE_LOCALES:
    EXPECTED[f"store/screenshots/app-store/iphone-6.9-{locale}/01-current.png"] = (
        (1320, 2868),
        "PNG",
    )
    EXPECTED[f"store/screenshots/app-store/ipad-13-{locale}/01-current.png"] = (
        (2064, 2752),
        "PNG",
    )


def inspect_image(path: Path) -> tuple[tuple[int, int], str, str, bool]:
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            image.load()
            image_format = image.format or ""
            has_alpha = "A" in image.getbands() or "transparency" in image.info
            return image.size, image_format, image.mode, has_alpha
    except (Image.DecompressionBombError, OSError, SyntaxError, ValueError) as error:
        raise ValueError(f"image decode/verification failed: {error}") from error


def png_bit_depth_and_color_type(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as stream:
        header = stream.read(26)
    if len(header) < 26 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return header[24], header[25]


def validate_store_image(
    relative: str,
    path: Path,
    expected_size: tuple[int, int],
    expected_format: str,
    *,
    require_alpha: bool = False,
    max_bytes: int | None = None,
) -> list[str]:
    """Validate one delivery image using its store-surface alpha policy."""
    failures: list[str] = []
    try:
        actual_size, actual_format, mode, has_alpha = inspect_image(path)
    except ValueError as error:
        return [f"{relative}: {error}"]
    if actual_size != expected_size:
        failures.append(f"{relative}: expected {expected_size}, found {actual_size}")
    if actual_format != expected_format:
        failures.append(
            f"{relative}: expected {expected_format}, found {actual_format}"
        )
    if require_alpha and (
        not has_alpha or mode != "RGBA" or png_bit_depth_and_color_type(path) != (8, 6)
    ):
        failures.append(f"{relative}: must be a 32-bit RGBA image with alpha")
    elif not require_alpha and has_alpha:
        failures.append(f"{relative}: alpha channel is not allowed")
    if max_bytes is not None and path.stat().st_size > max_bytes:
        failures.append(
            f"{relative}: exceeds {max_bytes}-byte store limit "
            f"({path.stat().st_size} bytes)"
        )
    return failures


for index, name in enumerate(
    (
        "01-current.png",
        "02-timeline-selected.png",
        "03-details.png",
        "04-settings-privacy.png",
        "05-offline-cache.png",
    ),
    start=1,
):
    EXPECTED[f"store/screenshots/google-play/phone-en/{name}"] = ((1080, 1920), "PNG")

for locale in STORE_LOCALES:
    if locale == "en":
        continue
    names = ["01-current.png", "02-timeline-selected.png"]
    if locale in {"ru-RU", "uz-UZ"}:
        names.extend(
            ["03-details.png", "04-settings-privacy.png", "05-offline-cache.png"]
        )
    for name in names:
        EXPECTED[f"store/screenshots/google-play/phone-{locale}/{name}"] = (
            (1080, 1920),
            "PNG",
        )

for name in (
    "01-overview.png",
    "02-selected-hour.png",
    "03-settings.png",
    "04-offline.png",
):
    EXPECTED[f"store/screenshots/google-play/tablet-en/{name}"] = ((2560, 1440), "PNG")


def load_creative_manifest() -> tuple[dict, list[str]]:
    failures: list[str] = []
    try:
        manifest = json.loads(CREATIVE_MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {}, [f"creative manifest: {error}"]
    if manifest.get("schema_version") != 1:
        failures.append("creative manifest schema_version must be 1")
    if manifest.get("generated_by") != "scripts/build_store_creatives.py":
        failures.append("creative manifest must name the deterministic renderer")
    platforms = manifest.get("platforms", {})
    if set(platforms) != {"app-store", "google-play"}:
        failures.append("creative manifest must cover App Store and Google Play")
    google_platform = platforms.get("google-play", {})
    feature_source = google_platform.get("feature_graphic_source")
    if not isinstance(feature_source, str) or not feature_source.startswith(
        "branding/source/"
    ):
        failures.append("Google feature graphic source must stay under branding/source")
    feature_graphics = google_platform.get("feature_graphics", {})
    if set(feature_graphics) != {"en-US", "ru-RU", "uz-UZ"}:
        failures.append("Google feature graphics must map en-US, ru-RU, and uz-UZ")
    else:
        for locale, feature in feature_graphics.items():
            if not isinstance(feature, dict) or set(feature) != {
                "output",
                "subtitle",
                "body",
            }:
                failures.append(f"Google feature graphic {locale}: invalid schema")
                continue
            if not feature["output"].startswith("store/assets/google-play/"):
                failures.append(f"Google feature graphic {locale}: invalid output path")
            if not feature["subtitle"].strip() or not feature["body"].strip():
                failures.append(f"Google feature graphic {locale}: blank copy")
    if google_platform.get("legacy_feature_graphic") != (
        "store/assets/google-play/feature-graphic-1024x500.jpg"
    ):
        failures.append("Google legacy feature graphic path changed")
    if google_platform.get("legacy_feature_graphic_locale") != "en-US":
        failures.append("Google global legacy feature graphic must use en-US")
    locales = manifest.get("locales", {})
    if set(locales) != {"en-US", "ru-RU", "uz-UZ"}:
        failures.append("creative manifest must cover en-US, ru-RU, and uz-UZ")
    stories = manifest.get("stories", [])
    if [story.get("sequence") for story in stories] != list(range(1, 7)):
        failures.append("creative manifest must contain exactly six ordered stories")
    filenames = [story.get("filename") for story in stories]
    if len(set(filenames)) != 6 or any(
        not str(name).endswith(".png") for name in filenames
    ):
        failures.append("creative story filenames must be six unique PNG names")
    if set(manifest.get("excluded_until_captured", [])) != {"home-screen widgets"}:
        failures.append("uncaptured product surfaces must remain explicitly excluded")

    for locale, locale_data in locales.items():
        watch_sources = locale_data.get("watch_sources", {})
        if set(watch_sources) != {"app-store", "google-play"}:
            failures.append(f"{locale}: watch sources must cover both platforms")
        else:
            expected_locale_segment = "en" if locale == "en-US" else locale
            for platform, relative in watch_sources.items():
                if (
                    not isinstance(relative, str)
                    or expected_locale_segment not in relative
                ):
                    failures.append(
                        f"{locale}/{platform}: watch source must match the locale"
                    )
        captions = locale_data.get("captions", {})
        for platform in ("app-store", "google-play"):
            values = captions.get(platform, [])
            if len(values) != 6 or any(
                not isinstance(value, str) or not value.strip() for value in values
            ):
                failures.append(f"{locale}/{platform}: expected six non-empty captions")
            lowered = " ".join(values).lower()
            unsupported_claims = ["home-screen widget", "виджет", "vidjet"]
            if platform == "app-store":
                unsupported_claims.extend(
                    [
                        "10-day",
                        "air quality",
                        "качество воздуха",
                        "10 kunlik",
                        "havo sifati",
                    ]
                )
            for unsupported in unsupported_claims:
                if unsupported in lowered:
                    failures.append(
                        f"{locale}/{platform}: uncaptured claim {unsupported!r}"
                    )

    source_paths: set[str] = set()
    for platform, platform_data in platforms.items():
        for locale_data in locales.values():
            watch_source = locale_data.get("watch_sources", {}).get(platform)
            if watch_source:
                source_paths.add(watch_source)
            for story in stories:
                if platform == "google-play" and story.get("google_source"):
                    failures.append(
                        f"{story.get('id', 'unknown')}: fixed Google source is not "
                        "allowed for a localized creative set"
                    )
                    source_paths.add(story["google_source"])
                elif platform == "google-play":
                    source_paths.add(
                        platform_data["phone_source"].format(
                            source_locale=locale_data["source_locale"],
                            source_name=story["google_source_name"],
                        )
                    )
                else:
                    source_paths.add(
                        platform_data["phone_source"].format(
                            source_locale=locale_data["source_locale"]
                        )
                    )
    for relative in source_paths:
        if not relative.startswith("store/screenshots/"):
            failures.append(
                f"creative source is not a production screenshot: {relative}"
            )
        elif not (ROOT / relative).is_file():
            failures.append(f"missing creative source {relative}")
    failures.extend(validate_source_sha256_contract(manifest, root=ROOT))
    failures.extend(
        validate_output_sha256_contract(manifest, root=ROOT, verify_files=False)
    )
    return manifest, failures


def main() -> int:
    manifest, failures = load_creative_manifest()
    if manifest:
        failures.extend(validate_output_sha256_contract(manifest, root=ROOT))
        for feature in manifest["platforms"]["google-play"][
            "feature_graphics"
        ].values():
            EXPECTED[feature["output"]] = ((1024, 500), "JPEG")
        for platform, platform_data in manifest["platforms"].items():
            size = tuple(platform_data["size"])
            for locale in manifest["locales"]:
                for story in manifest["stories"]:
                    relative = (
                        Path(platform_data["output_dir"]) / locale / story["filename"]
                    ).as_posix()
                    EXPECTED[relative] = (size, "PNG")
    for relative, (size, image_format) in EXPECTED.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing {relative}")
            continue
        failures.extend(
            validate_store_image(
                relative,
                path,
                size,
                image_format,
                require_alpha=relative == GOOGLE_PLAY_ICON,
                max_bytes=(
                    GOOGLE_PLAY_ICON_MAX_BYTES if relative == GOOGLE_PLAY_ICON else None
                ),
            )
        )

    if manifest:
        google_platform = manifest["platforms"]["google-play"]
        legacy = ROOT / google_platform["legacy_feature_graphic"]
        selected = (
            ROOT
            / google_platform["feature_graphics"][
                google_platform["legacy_feature_graphic_locale"]
            ]["output"]
        )
        if (
            legacy.is_file()
            and selected.is_file()
            and legacy.read_bytes() != selected.read_bytes()
        ):
            failures.append("Google global legacy feature graphic differs from en-US")

    screenshot_root = ROOT / "store/screenshots"
    unexpected = sorted(
        path.relative_to(ROOT).as_posix()
        for path in screenshot_root.rglob("*")
        if path.is_file() and path.relative_to(ROOT).as_posix() not in EXPECTED
    )
    if unexpected:
        failures.append(f"unvalidated screenshots: {', '.join(unexpected)}")

    asset_root = ROOT / "store/assets"
    unexpected_assets = sorted(
        path.relative_to(ROOT).as_posix()
        for path in asset_root.rglob("*")
        if path.is_file() and path.relative_to(ROOT).as_posix() not in EXPECTED
    )
    if unexpected_assets:
        failures.append(f"unvalidated assets: {', '.join(unexpected_assets)}")

    creative_root = ROOT / "store/creatives"
    unexpected_creatives = sorted(
        path.relative_to(ROOT).as_posix()
        for path in creative_root.rglob("*")
        if path.is_file() and path.relative_to(ROOT).as_posix() not in EXPECTED
    )
    if unexpected_creatives:
        failures.append(f"unvalidated creatives: {', '.join(unexpected_creatives)}")

    if failures:
        print("Store asset validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"Store asset validation passed: {len(EXPECTED)} production images.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
