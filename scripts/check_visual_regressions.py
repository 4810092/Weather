#!/usr/bin/env python3
"""Compare fixed-clock Compose screenshots on the pinned API36 phone/tablet runner."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[1]
BASELINES = ROOT / "qa" / "visual"


def compare(expected: Path, actual: Path, difference: Path) -> dict:
    with Image.open(expected) as reference, Image.open(actual) as candidate:
        if reference.size != candidate.size:
            return {"passed": False, "reason": f"size: {reference.size} != {candidate.size}"}
        delta = ImageChops.difference(reference.convert("RGB"), candidate.convert("RGB"))
        mean = sum(ImageStat.Stat(delta).mean) / 3
        # Ignore tiny per-channel antialiasing noise, never scale or align away layout drift.
        red, green, blue = delta.split()
        maximum = ImageChops.lighter(ImageChops.lighter(red, green), blue)
        changed = sum(maximum.histogram()[13:]) / (delta.width * delta.height)
        passed = mean <= 0.4 and changed <= 0.003
        if not passed:
            difference.parent.mkdir(parents=True, exist_ok=True)
            delta.point(lambda value: min(value * 4, 255)).save(difference)
        return {"passed": passed, "mean_channel_delta": mean, "changed_pixel_fraction": changed}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", required=True, choices=("phone-api36", "tablet-api36"))
    parser.add_argument("--actual", type=Path, required=True)
    parser.add_argument("--record", action="store_true", help="Record reviewed local baselines explicitly")
    args = parser.parse_args()
    baseline = BASELINES / args.matrix
    screenshots = sorted(args.actual.glob("premium-*.png"))
    if not screenshots:
        raise SystemExit("No current premium screenshots; refusing an empty visual gate")
    manifest_path = baseline / "manifest.json"
    if args.record:
        baseline.mkdir(parents=True, exist_ok=True)
        for screenshot in screenshots:
            shutil.copy2(screenshot, baseline / screenshot.name)
        manifest = {
            "clock_epoch_seconds": 1725000000,
            "night_clock_epoch_seconds": 1725036000,
            "location_timezone": "Asia/Tashkent",
            "renderer": "API36 arm64, swiftshader_indirect, animation scales 0",
            "fixtures": "PremiumForecastUiTest.deterministicVisualMatrix (no network)",
            "matrix": args.matrix,
            "image_size": list(Image.open(screenshots[0]).size),
            "locales": ["ru", "uz", "ar", "en-US"],
            "font_scales": [1, 2],
            "themes": ["light", "dark"],
            "screenshots": [path.name for path in screenshots],
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"Recorded {len(screenshots)} explicitly reviewed baselines: {baseline}")
        return 0
    manifest = json.loads(manifest_path.read_text())
    if manifest["screenshots"] != [path.name for path in screenshots]:
        raise SystemExit("Screenshot inventory changed; review missing/new fixtures before recording")
    results = {
        path.name: compare(baseline / path.name, path, args.actual / "diff" / path.name)
        for path in screenshots
    }
    (args.actual / "visual-results.json").write_text(json.dumps(results, indent=2) + "\n")
    failures = {name: result for name, result in results.items() if not result["passed"]}
    print(f"Visual regression {args.matrix}: {len(results) - len(failures)}/{len(results)} passed")
    if failures:
        print(json.dumps(failures, indent=2))
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
