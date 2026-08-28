#!/usr/bin/env python3
"""Fail CI when release identity, legal files, or secret hygiene regress."""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from urllib.parse import unquote


ROOT = pathlib.Path(__file__).resolve().parents[1]
REQUIRED = (
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "SUPPORT.md",
    "CHANGELOG.md",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
    "docs/ARCHITECTURE.md",
    "docs/DEVELOPMENT.md",
    "docs/TESTING.md",
    "docs/LOCALIZATION.md",
    "docs/PRIVACY.md",
    "docs/PROVIDERS.md",
    "docs/CODEX_FOR_OSS_APPLICATION.md",
)
FORBIDDEN_SUFFIXES = (
    ".aab",
    ".apk",
    ".ipa",
    ".jks",
    ".keystore",
    ".p12",
    ".p8",
    ".pem",
    ".key",
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

markdown_link = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
for relative in filter(None, tracked):
    path = ROOT / relative
    if path.suffix.lower() != ".md" or not path.is_file():
        continue
    for raw_target in markdown_link.findall(path.read_text(encoding="utf-8")):
        target = raw_target.strip().strip("<>").split(maxsplit=1)[0]
        if (
            not target
            or target.startswith(("#", "/"))
            or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE)
        ):
            continue
        local_target = unquote(target.split("#", 1)[0].split("?", 1)[0])
        if local_target and not (path.parent / local_target).exists():
            fail(f"broken local Markdown link in {relative}: {raw_target}")

application_notes = (ROOT / "docs/CODEX_FOR_OSS_APPLICATION.md").read_text()
answer_pattern = re.compile(
    r"^### .+ — (?P<reported>\d+) characters\n\n(?P<answer>[^\n]+)$",
    re.MULTILINE,
)
answers = list(answer_pattern.finditer(application_notes))
if len(answers) != 4:
    fail("expected four counted Codex for OSS application answers")
for answer in answers:
    reported = int(answer.group("reported"))
    actual = len(answer.group("answer"))
    if reported != actual:
        fail(f"application answer count is {actual}, documented as {reported}")
    if actual > 500:
        fail(f"application answer exceeds 500 characters: {actual}")

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
if int(wear_version.group(1).replace("_", "")) <= 1_000_006:
    fail("Wear OS versionCode must be newer than rejected version 1000006")
if android_version.group(1).replace("_", "") == wear_version.group(1).replace("_", ""):
    fail("Wear OS versionCode must be unique across Play form factors")
if "implementation(libs.androidx.core.splashscreen)" not in wear:
    fail("Wear OS must use the AndroidX splash screen compatibility library")

version_catalog = (ROOT / "gradle/libs.versions.toml").read_text()
if "androidx.core:core-splashscreen" not in version_catalog:
    fail("AndroidX core splash screen dependency is missing from the version catalog")
if 'coreSplashscreen = "1.2.0"' not in version_catalog:
    fail("Wear OS must use the reviewed AndroidX Core SplashScreen 1.2.0 release")

if "CURRENT_PROJECT_VERSION: 4" not in ios:
    fail("iOS release build must remain newer than uploaded build 3")
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
wear_application = wear_manifest.find("application")
if wear_application is None:
    fail("Wear OS application manifest entry is missing")
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
        for item in wear_application.findall("meta-data")
        if item.get(android_name) == "com.google.android.wearable.standalone"
    ),
    None,
)
android_value = "{http://schemas.android.com/apk/res/android}value"
if standalone is None or standalone.get(android_value) != "false":
    fail("phone-dependent Wear OS package must declare standalone=false")

android_theme = "{http://schemas.android.com/apk/res/android}theme"
android_icon = "{http://schemas.android.com/apk/res/android}icon"
if wear_application.get(android_icon) != "@drawable/ic_watch":
    fail("Wear OS launcher icon must remain @drawable/ic_watch")
launcher_activity = next(
    (
        activity
        for activity in wear_application.findall("activity")
        if activity.get(android_name) == ".WearWeatherActivity"
    ),
    None,
)
if launcher_activity is None or launcher_activity.get(android_theme) != (
    "@style/Theme.Nimbo.Wear.Starting"
):
    fail("Wear OS launcher activity must use the branded starting theme")

wear_resource_root = ROOT / "wearApp/src/main/res"
wear_color_paths = sorted(wear_resource_root.glob("values*/colors.xml"))
for path in wear_color_paths:
    colors = ET.parse(path).getroot()
    background = next(
        (color for color in colors.findall("color") if color.get("name") == "weather_background"),
        None,
    )
    if background is None or (background.text or "").strip().upper() != "#000000":
        fail(f"Wear OS background must be pure black in {path.relative_to(ROOT)}")

wear_style_paths = sorted(wear_resource_root.glob("values*/styles.xml"))
for path in wear_style_paths:
    styles = ET.parse(path).getroot()
    app_theme = next(
        (style for style in styles.findall("style") if style.get("name") == "Theme.Nimbo.Wear"),
        None,
    )
    theme_items = {
        item.get("name"): (item.text or "").strip()
        for item in app_theme.findall("item")
    } if app_theme is not None else {}
    if theme_items.get("android:windowBackground") != "@color/weather_background":
        fail(f"Wear OS window background is not policy-backed in {path.relative_to(ROOT)}")
    if theme_items.get("android:windowLightStatusBar") != "false":
        fail(f"Wear OS must use light status-bar content in {path.relative_to(ROOT)}")

android_background = "{http://schemas.android.com/apk/res/android}background"
wear_layout = ET.parse(
    ROOT / "wearApp/src/main/res/layout/activity_weather.xml"
).getroot()
if wear_layout.get(android_background) != "@color/weather_background":
    fail("Wear OS root layout must use the policy-backed black background")

starting_styles = ET.parse(
    ROOT / "wearApp/src/main/res/values/styles.xml"
).getroot()
starting_theme = next(
    (
        style
        for style in starting_styles.findall("style")
        if style.get("name") == "Theme.Nimbo.Wear.Starting"
    ),
    None,
)
starting_items = {
    item.get("name"): (item.text or "").strip()
    for item in starting_theme.findall("item")
} if starting_theme is not None else {}
if starting_theme is None or starting_theme.get("parent") != "Theme.SplashScreen":
    fail("Wear OS starting theme must inherit Theme.SplashScreen")
if starting_items.get("windowSplashScreenBackground") != "@android:color/black":
    fail("Wear OS splash screen background must be black")
if starting_items.get("windowSplashScreenAnimatedIcon") != "@drawable/splash_screen":
    fail("Wear OS splash screen must use the policy-sized icon drawable")
if starting_items.get("postSplashScreenTheme") != "@style/Theme.Nimbo.Wear":
    fail("Wear OS splash screen must transition to Theme.Nimbo.Wear")

android_width = "{http://schemas.android.com/apk/res/android}width"
android_height = "{http://schemas.android.com/apk/res/android}height"
android_drawable = "{http://schemas.android.com/apk/res/android}drawable"
android_gravity = "{http://schemas.android.com/apk/res/android}gravity"
splash = ET.parse(ROOT / "wearApp/src/main/res/drawable/splash_screen.xml").getroot()
splash_item = splash.find("item")
if splash_item is None or (
    splash_item.get(android_width) != "@dimen/splash_screen_icon_size"
    or splash_item.get(android_height) != "@dimen/splash_screen_icon_size"
    or splash_item.get(android_drawable) != "@drawable/ic_watch"
    or splash_item.get(android_gravity) != "center"
):
    fail("Wear OS splash drawable must center the launcher icon at the policy size")

dimensions = ET.parse(ROOT / "wearApp/src/main/res/values/dimens.xml").getroot()
splash_size = next(
    (item for item in dimensions.findall("dimen") if item.get("name") == "splash_screen_icon_size"),
    None,
)
if splash_size is None or (splash_size.text or "").strip() != "48dp":
    fail("Wear OS splash screen icon must be exactly 48dp")

wear_activity = (
    ROOT
    / "wearApp/src/main/java/uz/ganikhodjaev/weather/wear/WearWeatherActivity.kt"
).read_text()
install_position = wear_activity.find("installSplashScreen()")
super_position = wear_activity.find("super.onCreate(savedInstanceState)")
if install_position < 0 or super_position < 0 or install_position > super_position:
    fail("Wear OS activity must install the splash screen before super.onCreate")

license_text = (ROOT / "LICENSE").read_text()
if "Apache License" not in license_text or "Version 2.0, January 2004" not in license_text:
    fail("LICENSE is not Apache-2.0")

canonical = (ROOT / "shared/src/commonMain/composeResources/values/strings.xml").read_text()
if "Open-Meteo" not in canonical or "GeoNames" not in canonical:
    fail("in-app provider attribution is missing")

print(f"Repository checks passed for {len(tracked) - 1} tracked paths.")
