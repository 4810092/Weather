#!/usr/bin/env python3
"""Collect sustained QA-package rendering evidence; never changes device settings.

Use --swipes only with authorization for scripted device input. Otherwise scroll
manually while this collector runs. Keep APK, data, display and thermal conditions
matched. Frame samples are deduplicated across the gfxinfo rolling buffer.
"""

import argparse
import csv
import json
import math
import pathlib
import subprocess
import threading
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial", required=True)
    parser.add_argument("--package", default="uz.ganikhodjaev.weather.physicalqa")
    parser.add_argument("--output", required=True, type=pathlib.Path)
    parser.add_argument("--seconds", type=int, default=120)
    parser.add_argument("--swipes", action="store_true")
    parser.add_argument("--mirroring", choices=("on", "off"), required=True)
    args = parser.parse_args()
    if not args.package.startswith("uz.ganikhodjaev.weather."):
        parser.error("Use a separate Nimbo QA package, never the main installation")
    args.output.mkdir(parents=True, exist_ok=False)

    def adb(*words):
        return subprocess.check_output(
            ["adb", "-s", args.serial, *words], text=True, timeout=20
        )

    def capture(name, command):
        value = adb("shell", command)
        (args.output / name).write_text(value)
        return value

    for service in ("display", "thermalservice", f"meminfo {args.package}"):
        capture("before-" + service.split()[0] + ".txt", "dumpsys " + service)
    for ns in ("system", "global", "secure"):
        keys = {
            "system": ("peak_refresh_rate", "min_refresh_rate", "font_scale", "screen_brightness", "screen_brightness_mode"),
            "global": ("animator_duration_scale", "low_power"),
            "secure": ("high_text_contrast_enabled",),
        }[ns]
        (args.output / f"settings-{ns}.json").write_text(json.dumps({
            key: adb("shell", "settings", "get", ns, key).strip() for key in keys
        }, indent=2))
    capture("package.txt", f"dumpsys package {args.package}")
    reset = capture("gfx-reset.txt", f"dumpsys gfxinfo {args.package} reset")
    cutoff = max((int(line.split()[2].removesuffix("ns")) for line in reset.splitlines()
                  if line.startswith("Stats since:")), default=0)
    start = time.monotonic()
    stop = threading.Event()
    errors = []

    def gestures():
        try:
            # Identical physical-pixel path on SM-S908E 1440x3088 portrait.
            # Two upward drags traverse the content, two reverse the same path.
            index = 0
            while not stop.is_set() and time.monotonic() - start < args.seconds:
                y1, y2 = (2450, 950) if index % 4 < 2 else (950, 2450)
                adb("shell", f"input touchscreen swipe 720 {y1} 720 {y2} 650")
                index += 1
                stop.wait(0.15)
        except Exception as error:
            errors.append(str(error))
            stop.set()

    worker = threading.Thread(target=gestures) if args.swipes else None
    if worker:
        worker.start()
    frames = {}
    count = 0
    try:
        while not stop.is_set() and time.monotonic() - start < args.seconds:
            raw = capture(f"gfx-{count:03d}.txt", f"dumpsys gfxinfo {args.package} framestats")
            columns = None
            for line in raw.splitlines():
                if line.startswith("Flags,") and "IntendedVsync," in line:
                    columns = line.rstrip(",").split(",")
                elif columns and line and line[0].isdigit() and "," in line:
                    values = line.rstrip(",").split(",")
                    if len(values) == len(columns):
                        row = dict(zip(columns, map(int, values)))
                        if row.get("FrameCompleted", 0) > 0 and row["IntendedVsync"] >= cutoff:
                            frames[row["IntendedVsync"]] = row
            count += 1
            stop.wait(0.75)
    finally:
        stop.set()
        if worker:
            worker.join(timeout=25)
    elapsed = time.monotonic() - start
    for service in ("display", "thermalservice", f"meminfo {args.package}"):
        capture("after-" + service.split()[0] + ".txt", "dumpsys " + service)
    capture("gfx-final.txt", f"dumpsys gfxinfo {args.package} framestats")
    ordered = sorted(frames.values(), key=lambda row: row["IntendedVsync"])
    if not ordered:
        raise SystemExit("No frame samples; do not interpret as a pass")
    with (args.output / "frames.csv").open("w") as file:
        writer = csv.DictWriter(file, fieldnames=ordered[0].keys())
        writer.writeheader()
        writer.writerows(ordered)
    valid = [row for row in ordered if row["Flags"] == 0 and
             0 < row["FrameCompleted"] - row["IntendedVsync"] < 10_000_000_000]
    times = sorted((row["FrameCompleted"] - row["IntendedVsync"]) / 1e6 for row in valid)
    def percentile(p):
        return times[max(0, math.ceil(len(times) * p) - 1)] if times else None
    summary = {
        "package": args.package, "serial": args.serial, "seconds": elapsed,
        "mirroring": args.mirroring, "scriptedSwipes": args.swipes,
        "samples": len(ordered), "validFrames": len(valid),
        "excludedFlaggedOrInvalid": len(ordered) - len(valid),
        "frameMs_p50": percentile(0.5), "frameMs_p95": percentile(0.95),
        "frameMs_p99": percentile(0.99),
        "deadlineMissPercent": 100 * sum(row["FrameCompleted"] > row["FrameDeadline"] for row in valid) / len(valid) if valid else None,
        "over16_7msPercent": 100 * sum(value > 16.7 for value in times) / len(times) if times else None,
        "errors": errors,
        "definition": "FrameCompleted - IntendedVsync; deadline from each frame's FrameDeadline; nearest-rank percentiles; all valid frames including stalls",
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
