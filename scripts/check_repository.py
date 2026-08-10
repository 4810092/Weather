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
ios = (ROOT / "iosApp/project.yml").read_text()
identity = "uz.ganikhodjaev.weather"
if f'applicationId = "{identity}"' not in android:
    fail("Android production applicationId changed")
if f"PRODUCT_BUNDLE_IDENTIFIER: {identity}" not in ios:
    fail("iOS production bundle identifier changed")

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

license_text = (ROOT / "LICENSE").read_text()
if "Apache License" not in license_text or "Version 2.0, January 2004" not in license_text:
    fail("LICENSE is not Apache-2.0")

canonical = (ROOT / "shared/src/commonMain/composeResources/values/strings.xml").read_text()
if "Open-Meteo" not in canonical or "GeoNames" not in canonical:
    fail("in-app provider attribution is missing")

print(f"Repository checks passed for {len(tracked) - 1} tracked paths.")
