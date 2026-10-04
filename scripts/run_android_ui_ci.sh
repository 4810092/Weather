#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <matrix-name> <expected-api-level>" >&2
  exit 64
fi

matrix_name="$1"
expected_api_level="$2"

if [[ ! "$matrix_name" =~ ^[a-z0-9-]+$ ]]; then
  echo "Invalid matrix name: $matrix_name" >&2
  exit 64
fi

if [[ ! "$expected_api_level" =~ ^[0-9]+$ ]]; then
  echo "Invalid expected API level: $expected_api_level" >&2
  exit 64
fi

diagnostics_dir="build/android-ui-diagnostics"
device_file="$diagnostics_dir/${matrix_name}-device.txt"
logcat_file="$diagnostics_dir/${matrix_name}-logcat.txt"
mkdir -p "$diagnostics_dir"

capture_logcat() {
  adb logcat -d -v threadtime > "$logcat_file" 2>&1 || true
}
trap capture_logcat EXIT

adb wait-for-device
actual_api_level="$(adb shell getprop ro.build.version.sdk | tr -d '\r')"
if [[ "$actual_api_level" != "$expected_api_level" ]]; then
  echo "Expected emulator API $expected_api_level, got $actual_api_level" >&2
  exit 1
fi

{
  printf 'matrix=%s\n' "$matrix_name"
  printf 'expected_api_level=%s\n' "$expected_api_level"
  printf 'actual_api_level=%s\n' "$actual_api_level"
  adb shell getprop ro.product.model
  adb shell wm size
  adb shell wm density
} > "$device_file"

adb logcat -c

set +e
python3 scripts/run_with_timeout.py 1680 60 -- \
  ./gradlew --no-daemon --max-workers=2 \
    :shared:connectedAndroidDeviceTest --stacktrace
gradle_status="$?"
set -e

if [[ "$gradle_status" -eq 124 ]]; then
  echo "Android UI Gradle task exceeded the 28-minute execution budget." >&2
fi

if [[ "$gradle_status" -ne 0 ]]; then
  exit "$gradle_status"
fi

python3 scripts/verify_android_ui_results.py \
  --root shared/build/outputs/androidTest-results \
  --expected-tests 17

# Gradle collects additional test output before uninstalling the test APK.
python3 - "$matrix_name" <<'PY_CAPTURE'
import shutil
import sys
from pathlib import Path

root = Path("shared/build/outputs/connected_android_test_additional_output")
destination = Path("build/android-ui-diagnostics") / f"{sys.argv[1]}-glass"
destination.mkdir(parents=True, exist_ok=True)
for name in (
    "light.png", "dark.png", "daily-details.png", "ru-settings-font-200.png",
    "city-picker-light.png", "city-picker-dark.png", "city-picker-ru-font-200.png",
):
    matches = list(root.rglob(name))
    if len(matches) != 1:
        raise SystemExit(f"Expected one current {name} screenshot under {root}, found {len(matches)}")
    shutil.copy2(matches[0], destination / name)
print(f"Glass screenshots saved to {destination}")
PY_CAPTURE
