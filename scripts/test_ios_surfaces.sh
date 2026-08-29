#!/usr/bin/env bash
set -euo pipefail

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
nimbo_simulator_id="${NIMBO_IOS_TEST_DESTINATION_ID:-}"

if [[ -z "${nimbo_simulator_id}" ]]; then
  nimbo_simulator_id="$(
    xcrun simctl list devices available -j | python3 -c '
import json
import re
import sys

payload = json.load(sys.stdin)
candidates = []
for runtime, devices in payload.get("devices", {}).items():
    match = re.search(r"iOS-(\d+)(?:-(\d+))?", runtime)
    if match is None:
        continue
    version = tuple(int(value or 0) for value in match.groups())
    for device in devices:
        if device.get("isAvailable") and device.get("name", "").startswith("iPhone"):
            candidates.append((version, device["udid"]))

if not candidates:
    raise SystemExit("No available iPhone simulator was found")
print(max(candidates)[1])
'
  )"
fi

xcodebuild \
  -project "${repository_root}/iosApp/Nimbo.xcodeproj" \
  -scheme NimboSurfaceTests \
  -configuration Debug \
  -sdk iphonesimulator \
  -destination "platform=iOS Simulator,id=${nimbo_simulator_id}" \
  CODE_SIGNING_ALLOWED=NO \
  test
