#!/usr/bin/env bash
# Fixed-data Compose rendering/scroll/refresh benchmark. Never changes device settings.
# For comparison use the same device, app/test build type, animation settings and thermal state.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${ANDROID_SERIAL:?Set ANDROID_SERIAL to a task emulator or an authorized test device}"
label="${1:?Usage: ANDROID_SERIAL=... scripts/measure_forecast_rendering.sh before|after}"
[[ "$label" =~ ^[a-zA-Z0-9_-]+$ ]] || exit 64
sdk="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}"
adb_bin="$sdk/platform-tools/adb"
output="build/premium-quality/$label"
mkdir -p "$output"
{
  "$adb_bin" shell getprop ro.product.model
  "$adb_bin" shell getprop ro.build.version.sdk
  "$adb_bin" shell wm size
  "$adb_bin" shell wm density
  "$adb_bin" shell settings get global animator_duration_scale
} > "$output/environment.txt"
run_started="$(python3 -c 'import time; print(time.time_ns())')"
./gradlew :shared:connectedAndroidDeviceTest \
  -Pandroid.testInstrumentationRunnerArguments.class=uz.ganikhodjaev.weather.shared.ui.ForecastPerformanceTest \
  > "$output/instrumentation.log" 2>&1
python3 - "$output" "$run_started" <<'PY'
import json
import shutil
import statistics
import sys
from pathlib import Path
root = Path("shared/build/outputs/connected_android_test_additional_output")
output = Path(sys.argv[1])
for name in ("performance-render.json", "performance-frames.txt", "performance-first-screen.png"):
    matches = list(root.rglob(name))
    if len(matches) != 1:
        raise SystemExit(f"Expected one {name}, got {len(matches)}")
    if matches[0].stat().st_mtime_ns < int(sys.argv[2]):
        raise SystemExit(f"Stale instrumentation artifact from an earlier run: {matches[0]}")
    shutil.copy2(matches[0], output / name)
metrics = json.loads((output / "performance-render.json").read_text())
print(f"Compose first render: {metrics['firstComposeRenderMs']:.1f} ms")
print(f"Refresh render median: {statistics.median(metrics['refreshRenderMs']):.1f} ms (fixed data, no network)")
print(f"Frame diagnostics and environment: {output}")
PY
