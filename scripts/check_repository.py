#!/usr/bin/env python3
"""Fail CI when release identity, legal files, or secret hygiene regress."""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = pathlib.Path(__file__).resolve().parents[1]
REQUIRED = (
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "docs/ARCHITECTURE.md",
    "docs/PRIVACY.md",
    "docs/PROVIDERS.md",
)
FORBIDDEN_SUFFIXES = (
    ".aab",
    ".apk",
    ".jks",
    ".keystore",
    ".p12",
    ".mobileprovision",
)
SECRET_MARKERS = (
    re.compile(rb"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
    re.compile(rb"(?i)(?:api[_-]?key|client[_-]?secret)\s*[:=]\s*[\"'][^\"']{12,}"),
)


def fail(message: str) -> None:
    print(f"repository check failed: {message}", file=sys.stderr)
    raise SystemExit(1)


for relative in REQUIRED:
    if not (ROOT / relative).is_file():
        fail(f"missing {relative}")

tracked = subprocess.check_output(
    ["git", "ls-files", "-z"], cwd=ROOT
).decode().split("\0")
for relative in filter(None, tracked):
    path = ROOT / relative
    lowered = relative.lower()
    if lowered.endswith(FORBIDDEN_SUFFIXES):
        fail(f"forbidden release/signing artifact is tracked: {relative}")
    if not path.is_file() or path.stat().st_size > 2_000_000:
        continue
    payload = path.read_bytes()
    if any(pattern.search(payload) for pattern in SECRET_MARKERS):
        fail(f"possible embedded secret in {relative}")

android = (ROOT / "app/build.gradle.kts").read_text()
wear = (ROOT / "wearApp/build.gradle.kts").read_text()
ios = (ROOT / "iosApp/project.yml").read_text()
identity = "uz.ganikhodjaev.weather"
if f'applicationId = "{identity}"' not in android:
    fail("Android production applicationId changed")
if f"PRODUCT_BUNDLE_IDENTIFIER: {identity}" not in ios:
    fail("iOS production bundle identifier changed")

android_version = re.search(r"versionCode\s*=\s*([\d_]+)", android)
wear_version = re.search(r"versionCode\s*=\s*([\d_]+)", wear)
if android_version is None or int(android_version.group(1).replace("_", "")) <= 5:
    fail("Android release versionCode must be greater than uploaded version 5")
if wear_version is None:
    fail("Wear OS versionCode is missing")
if android_version.group(1).replace("_", "") == wear_version.group(1).replace("_", ""):
    fail("Wear OS versionCode must be unique across Play form factors")

if "CURRENT_PROJECT_VERSION: 3" not in ios:
    fail("iOS release build must remain newer than uploaded build 2")
for relative in (
    "iosApp/Nimbo/Info.plist",
    "iosApp/NimboSimulator/Info.plist",
    "iosApp/NimboWidget/Info.plist",
    "iosApp/NimboWatch/Info.plist",
):
    content = (ROOT / relative).read_text()
    if "$(MARKETING_VERSION)" not in content or "$(CURRENT_PROJECT_VERSION)" not in content:
        fail(f"{relative} must inherit the Xcode release version")

for bundle_id in (f"{identity}.widget", f"{identity}.watchkitapp"):
    if f"PRODUCT_BUNDLE_IDENTIFIER: {bundle_id}" not in ios:
        fail(f"missing Apple surface bundle identifier {bundle_id}")

manifest = ET.parse(ROOT / "app/src/main/AndroidManifest.xml").getroot()
android_name = "{http://schemas.android.com/apk/res/android}name"
android_required = "{http://schemas.android.com/apk/res/android}required"
location_feature = next(
    (
        feature
        for feature in manifest.findall("uses-feature")
        if feature.get(android_name) == "android.hardware.location"
    ),
    None,
)
if location_feature is None or location_feature.get(android_required) != "false":
    fail("optional city-search flow requires android.hardware.location to be optional")

wear_manifest = ET.parse(ROOT / "wearApp/src/main/AndroidManifest.xml").getroot()
watch_feature = next(
    (
        feature
        for feature in wear_manifest.findall("uses-feature")
        if feature.get(android_name) == "android.hardware.type.watch"
    ),
    None,
)
if watch_feature is None or watch_feature.get(android_required) == "false":
    fail("Wear OS package must require android.hardware.type.watch")
standalone = next(
    (
        item
        for item in wear_manifest.find("application").findall("meta-data")
        if item.get(android_name) == "com.google.android.wearable.standalone"
    ),
    None,
)
android_value = "{http://schemas.android.com/apk/res/android}value"
if standalone is None or standalone.get(android_value) != "false":
    fail("phone-dependent Wear OS package must declare standalone=false")

license_text = (ROOT / "LICENSE").read_text()
if "Apache License" not in license_text or "Version 2.0, January 2004" not in license_text:
    fail("LICENSE is not Apache-2.0")

canonical = (ROOT / "shared/src/commonMain/composeResources/values/strings.xml").read_text()
if "Open-Meteo" not in canonical or "GeoNames" not in canonical:
    fail("in-app provider attribution is missing")

print(f"Repository checks passed for {len(tracked) - 1} tracked paths.")
