#!/usr/bin/env python3
"""Validate version-controlled store graphics before release."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CREATIVE_MANIFEST = ROOT / "store/creative-sets/growth-2026-08.json"

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
    "store/screenshots/app-store/apple-watch-en/01-current.jpg": ((416, 496), "JPEG"),
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


def inspect_image(path: Path) -> tuple[tuple[int, int], str, bool]:
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            image.load()
            image_format = image.format or ""
            has_alpha = "A" in image.getbands() or "transparency" in image.info
            return image.size, image_format, has_alpha
    except (Image.DecompressionBombError, OSError, SyntaxError, ValueError) as error:
        raise ValueError(f"image decode/verification failed: {error}") from error


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
    if set(manifest.get("excluded_until_captured", [])) != {
        "home-screen widgets"
    }:
        failures.append("uncaptured product surfaces must remain explicitly excluded")

    for locale, locale_data in locales.items():
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
        watch_source = platform_data.get("watch_source")
        if watch_source:
            source_paths.add(watch_source)
        for locale_data in locales.values():
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
    return manifest, failures


def main() -> int:
    manifest, failures = load_creative_manifest()
    if manifest:
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
        try:
            actual_size, actual_format, has_alpha = inspect_image(path)
        except ValueError as error:
            failures.append(f"{relative}: {error}")
            continue
        if actual_size != size:
            failures.append(f"{relative}: expected {size}, found {actual_size}")
        if actual_format != image_format:
            failures.append(
                f"{relative}: expected {image_format}, found {actual_format}"
            )
        if has_alpha and "/assets/" in relative:
            failures.append(f"{relative}: alpha channel is not allowed")
        if has_alpha and "/creatives/" in relative:
            failures.append(f"{relative}: store creative must be opaque")

    screenshot_root = ROOT / "store/screenshots"
    unexpected = sorted(
        path.relative_to(ROOT).as_posix()
        for path in screenshot_root.rglob("*")
        if path.is_file() and path.relative_to(ROOT).as_posix() not in EXPECTED
    )
    if unexpected:
        failures.append(f"unvalidated screenshots: {', '.join(unexpected)}")

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
