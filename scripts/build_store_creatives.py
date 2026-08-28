#!/usr/bin/env python3
"""Build deterministic Nimbo store creatives from checked-in production captures.

The renderer only crops, scales, frames, and captions existing screenshots. It
does not synthesize or retouch application UI. Exact Pillow and font hashes are
declared in the creative-set manifest so a rebuild fails closed on renderer
drift instead of silently producing different artwork.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, __version__

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "store/creative-sets/growth-2026-08.json"
FONT_DIRECTORIES = (
    Path("/System/Library/Fonts/Supplemental"),
    Path("/Library/Fonts"),
    Path("/usr/share/fonts/truetype/msttcorefonts"),
)


def parse_color(value: str) -> tuple[int, int, int]:
    value = value.removeprefix("#")
    if len(value) != 6:
        raise ValueError(f"expected six-digit color, found {value!r}")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_font(font_spec: dict[str, str]) -> Path:
    filename = font_spec["filename"]
    expected_hash = font_spec["sha256"]
    candidates = [directory / filename for directory in FONT_DIRECTORIES]
    for candidate in candidates:
        if candidate.is_file() and sha256(candidate) == expected_hash:
            return candidate
    locations = ", ".join(str(path) for path in candidates)
    raise RuntimeError(
        f"missing deterministic font {filename} ({expected_hash}); checked {locations}"
    )


def gradient(
    size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]
) -> Image.Image:
    mask = Image.linear_gradient("L").resize(size, Image.Resampling.BILINEAR)
    return Image.composite(
        Image.new("RGB", size, bottom), Image.new("RGB", size, top), mask
    )


def focused_crop(image: Image.Image, focus: list[float]) -> Image.Image:
    center_x, center_y, zoom = focus
    if not (0.0 <= center_x <= 1.0 and 0.0 <= center_y <= 1.0 and zoom >= 1.0):
        raise ValueError(f"invalid focus {focus!r}")
    crop_width = max(1, round(image.width / zoom))
    crop_height = max(1, round(image.height / zoom))
    left = round(image.width * center_x - crop_width / 2)
    top = round(image.height * center_y - crop_height / 2)
    left = min(max(0, left), image.width - crop_width)
    top = min(max(0, top), image.height - crop_height)
    return image.crop((left, top, left + crop_width, top + crop_height))


def wrap_text(
    draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, width: int
) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = word if not current else f"{current} {word}"
        if draw.textlength(candidate, font=font) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_caption(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_path: Path,
    max_width: int,
    max_lines: int,
    initial_size: int,
    minimum_size: int,
) -> tuple[ImageFont.FreeTypeFont, str]:
    for size in range(initial_size, minimum_size - 1, -2):
        font = ImageFont.truetype(font_path, size=size)
        lines = wrap_text(draw, text, font, max_width)
        if len(lines) <= max_lines:
            return font, "\n".join(lines)
    raise RuntimeError(f"caption does not fit: {text!r}")


def paste_rounded(
    canvas: Image.Image,
    source: Image.Image,
    box: tuple[int, int, int, int],
    radius: int,
    shadow_blur: int,
) -> None:
    left, top, right, bottom = box
    size = (right - left, bottom - top)
    rendered = ImageOps.fit(
        source.convert("RGB"), size, method=Image.Resampling.LANCZOS
    )
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255
    )

    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(shadow_mask).rounded_rectangle(
        (
            left,
            top + max(8, shadow_blur // 3),
            right,
            bottom + max(8, shadow_blur // 3),
        ),
        radius=radius,
        fill=125,
    )
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(shadow_blur))
    shadow.putalpha(shadow_mask)
    canvas.paste(shadow, (0, 0), shadow)
    canvas.paste(rendered, (left, top), mask)


def source_path(
    manifest: dict,
    platform: str,
    locale_data: dict,
    story: dict,
) -> Path:
    if platform == "google-play" and "google_source" in story:
        relative = story["google_source"]
    elif platform == "google-play":
        template = manifest["platforms"][platform]["phone_source"]
        relative = template.format(
            source_locale=locale_data["source_locale"],
            source_name=story["google_source_name"],
        )
    else:
        template = manifest["platforms"][platform]["phone_source"]
        relative = template.format(source_locale=locale_data["source_locale"])
    path = ROOT / relative
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def decorate_background(canvas: Image.Image, accent: tuple[int, int, int]) -> None:
    draw = ImageDraw.Draw(canvas)
    width, height = canvas.size
    line = (*accent, 28)
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    for inset in (0, round(width * 0.12), round(width * 0.24)):
        overlay_draw.arc(
            (
                -round(width * 0.45) + inset,
                round(height * 0.49),
                round(width * 1.25) - inset,
                round(height * 1.16),
            ),
            202,
            338,
            fill=line,
            width=max(3, width // 170),
        )
    canvas.paste(overlay, (0, 0), overlay)
    draw.line(
        (width // 2 - width // 22, height - 24, width // 2 + width // 22, height - 24),
        fill=accent,
        width=5,
    )


def render_creative(
    manifest: dict,
    platform: str,
    locale: str,
    locale_data: dict,
    story: dict,
    regular_font: Path,
    bold_font: Path,
) -> Path:
    platform_data = manifest["platforms"][platform]
    width, height = platform_data["size"]
    colors = manifest["rendering"]
    foreground = parse_color(colors["foreground"])
    accent = parse_color(colors["accent"])
    canvas = gradient(
        (width, height),
        parse_color(colors["background_top"]),
        parse_color(colors["background_bottom"]),
    )
    decorate_background(canvas, accent)
    draw = ImageDraw.Draw(canvas)

    scale = width / 1080
    brand_font = ImageFont.truetype(regular_font, size=round(25 * scale))
    draw.text(
        (width // 2, round(56 * scale)),
        "N I M B O",
        font=brand_font,
        fill=accent,
        anchor="ma",
    )
    caption = locale_data["captions"][platform][story["sequence"] - 1]
    initial_size = round((68 if platform == "google-play" else 78) * scale)
    minimum_size = round((46 if platform == "google-play" else 52) * scale)
    font, wrapped = fit_caption(
        draw,
        caption,
        bold_font,
        max_width=round(width * 0.84),
        max_lines=3,
        initial_size=initial_size,
        minimum_size=minimum_size,
    )
    caption_y = round((112 if platform == "google-play" else 104) * scale)
    draw.multiline_text(
        (width // 2, caption_y),
        wrapped,
        font=font,
        fill=foreground,
        anchor="ma",
        align="center",
        spacing=round(10 * scale),
    )

    phone_path = source_path(manifest, platform, locale_data, story)
    phone = Image.open(phone_path).convert("RGB")
    focus_key = "google_focus" if platform == "google-play" else "app_store_focus"
    phone = focused_crop(phone, story[focus_key])

    if story.get("watch_overlay"):
        phone_width = round(width * 0.57)
        phone_height = (
            round(phone_width * 1920 / 1080)
            if platform == "google-play"
            else round(phone_width * 2868 / 1320)
        )
        phone_left = round(width * 0.08)
        phone_top = round(height * (0.35 if platform == "google-play" else 0.34))
    else:
        phone_width = round(width * (0.74 if platform == "google-play" else 0.76))
        phone_height = (
            round(phone_width * 1920 / 1080)
            if platform == "google-play"
            else round(phone_width * 2868 / 1320)
        )
        phone_left = (width - phone_width) // 2
        phone_top = round(height * (0.245 if platform == "google-play" else 0.238))
    phone_bottom = min(height - round(32 * scale), phone_top + phone_height)
    if phone_bottom - phone_top != phone_height:
        phone_width = round((phone_bottom - phone_top) * phone.width / phone.height)
        phone_left = (width - phone_width) // 2
    paste_rounded(
        canvas,
        phone,
        (phone_left, phone_top, phone_left + phone_width, phone_bottom),
        radius=round(42 * scale),
        shadow_blur=round(24 * scale),
    )

    if story.get("watch_overlay"):
        watch_path = ROOT / platform_data["watch_source"]
        if not watch_path.is_file():
            raise FileNotFoundError(watch_path)
        watch = Image.open(watch_path).convert("RGB")
        watch_width = round(width * (0.30 if platform == "google-play" else 0.31))
        watch_height = round(watch_width * watch.height / watch.width)
        watch_left = round(width * 0.65)
        watch_top = round(height * (0.61 if platform == "google-play" else 0.64))
        paste_rounded(
            canvas,
            watch,
            (watch_left, watch_top, watch_left + watch_width, watch_top + watch_height),
            radius=round(28 * scale),
            shadow_blur=round(22 * scale),
        )

    output_dir = ROOT / platform_data["output_dir"] / locale
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / story["filename"]
    canvas.save(output, format="PNG", compress_level=9, optimize=False)
    return output


def render_feature_graphic(manifest: dict, regular_font: Path, bold_font: Path) -> Path:
    output = ROOT / manifest["platforms"]["google-play"]["feature_graphic"]
    size = (1024, 500)
    canvas = gradient(size, (4, 18, 47), (10, 48, 77))
    draw = ImageDraw.Draw(canvas)
    accent = (142, 191, 230)
    for inset in (0, 42, 84):
        draw.arc(
            (620 + inset, 52 + inset, 1090 - inset, 514 - inset),
            195,
            345,
            fill=accent,
            width=4,
        )

    master = Image.open(ROOT / "branding/source/nimbo-icon-master.png").convert("RGB")
    mark = ImageOps.fit(master, (360, 360), method=Image.Resampling.LANCZOS)
    paste_rounded(canvas, mark, (650, 70, 1010, 430), radius=54, shadow_blur=18)

    title_font = ImageFont.truetype(bold_font, size=74)
    subtitle_font = ImageFont.truetype(bold_font, size=38)
    body_font = ImageFont.truetype(regular_font, size=28)
    draw.text((62, 94), "NIMBO", font=title_font, fill=(247, 251, 255))
    draw.text((64, 201), "Ob-havo va prognoz", font=subtitle_font, fill=(210, 232, 249))
    draw.multiline_text(
        (65, 276),
        "Tashqariga chiqish uchun\neng yaxshi vaqtni toping",
        font=body_font,
        fill=(176, 208, 232),
        spacing=9,
    )
    canvas.save(
        output,
        format="JPEG",
        quality=95,
        subsampling=0,
        optimize=False,
        progressive=False,
    )
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    manifest_path = (
        args.manifest if args.manifest.is_absolute() else ROOT / args.manifest
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_pillow = manifest["rendering"]["pillow_version"]
    if __version__ != expected_pillow:
        print(
            f"Pillow drift: manifest requires {expected_pillow}, found {__version__}",
            file=sys.stderr,
        )
        return 2
    regular_font = resolve_font(manifest["rendering"]["font_regular"])
    bold_font = resolve_font(manifest["rendering"]["font_bold"])

    outputs: list[Path] = []
    for platform in ("app-store", "google-play"):
        for locale, locale_data in manifest["locales"].items():
            for story in manifest["stories"]:
                outputs.append(
                    render_creative(
                        manifest,
                        platform,
                        locale,
                        locale_data,
                        story,
                        regular_font,
                        bold_font,
                    )
                )
    outputs.append(render_feature_graphic(manifest, regular_font, bold_font))
    print(f"Built {len(outputs)} deterministic store assets from production captures.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
