#!/usr/bin/env python3
"""Validate version-controlled store graphics before release."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STORE_LOCALES = (
    "en", "ru-RU", "ar", "es-ES", "fr-FR", "de-DE", "pt-PT",
    "zh-CN", "ja-JP", "ko-KR", "hi-IN", "tr-TR", "uz-UZ",
)

EXPECTED = {
    "store/assets/google-play/icon-512.png": ((512, 512), "PNG"),
    "store/assets/google-play/feature-graphic-1024x500.jpg": ((1024, 500), "JPEG"),
    "store/screenshots/google-play/wear-os-en/01-current.jpg": ((480, 480), "JPEG"),
    "store/screenshots/app-store/apple-watch-en/01-current.jpg": ((416, 496), "JPEG"),
}

for locale in STORE_LOCALES:
    EXPECTED[
        f"store/screenshots/app-store/iphone-6.9-{locale}/01-current.png"
    ] = ((1320, 2868), "PNG")
    EXPECTED[
        f"store/screenshots/app-store/ipad-13-{locale}/01-current.png"
    ] = ((2064, 2752), "PNG")


def inspect_image(path: Path) -> tuple[tuple[int, int], str, bool]:
    data = path.read_bytes()
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        if data[12:16] != b"IHDR":
            raise ValueError("missing PNG IHDR")
        width, height, _, color_type, _, _, _ = struct.unpack(">IIBBBBB", data[16:29])
        return (width, height), "PNG", color_type in {4, 6}
    if data.startswith(b"\xff\xd8"):
        offset = 2
        while offset + 9 < len(data):
            if data[offset] != 0xFF:
                offset += 1
                continue
            marker = data[offset + 1]
            offset += 2
            if marker in {0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
                continue
            length = struct.unpack(">H", data[offset : offset + 2])[0]
            size_markers = {
                0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF,
            }
            if marker in size_markers:
                height, width = struct.unpack(">HH", data[offset + 3 : offset + 7])
                return (width, height), "JPEG", False
            offset += length
        raise ValueError("missing JPEG size marker")
    raise ValueError("unsupported image format")

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
    for name in ("01-current.png", "02-timeline-selected.png"):
        EXPECTED[
            f"store/screenshots/google-play/phone-{locale}/{name}"
        ] = ((1080, 1920), "PNG")

for name in (
    "01-overview.png",
    "02-selected-hour.png",
    "03-settings.png",
    "04-offline.png",
):
    EXPECTED[f"store/screenshots/google-play/tablet-en/{name}"] = ((2560, 1440), "PNG")


def main() -> int:
    failures: list[str] = []
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

    screenshot_root = ROOT / "store/screenshots"
    unexpected = sorted(
        path.relative_to(ROOT).as_posix()
        for path in screenshot_root.rglob("*")
        if path.is_file() and path.relative_to(ROOT).as_posix() not in EXPECTED
    )
    if unexpected:
        failures.append(f"unvalidated screenshots: {', '.join(unexpected)}")

    if failures:
        print("Store asset validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"Store asset validation passed: {len(EXPECTED)} production images.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
