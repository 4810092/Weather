# ADR 0004: Platform and toolchain baseline

Status: accepted  
Date: 2026-08-09

Amended: 2026-08-28 — phone/tablet minimum lowered from API 26 to API 24 after
the Uzbekistan growth QA matrix made API 24 an explicit supported-device gate;
iOS 15 evidence language was narrowed after auditing the linked native archive.

Amended: 2026-08-29 — the WidgetKit extension was aligned with the iOS 15 app
floor; accessory families remain conditional on iOS 16 and removable container
background behavior remains conditional on iOS 17.

## Decision

- Android phone/tablet min SDK 24, Wear OS min SDK 30, compile/target SDK 36.
- iOS deployment target 15.0 for iPhone, iPad, and the home-screen widget.
- Accessory widgets are exposed on iOS 16+, and WidgetKit container-background
  behavior is used on iOS 17+ with an older-system fallback.
- Production toolchain starts from stable Kotlin 2.4.10 and Compose Multiplatform 1.11.1, subject to dependency compatibility validation during the foundation build.
- Xcode 26+ and iOS 26 SDK are required for App Store archives.

## Rationale

Compose Multiplatform 1.11.1 supports Android 5+ and iOS 14+, and Android/iOS
targets are stable. The original API 26 floor avoided compatibility work below
the legacy minimum. The growth amendment accepts that work for API 24–25 and
requires an API 24 emulator plus a lower-API physical smoke before release. Wear
OS remains at API 30. Kotlin/Native and the final app binary target iOS 15, but
the current Skiko archive contains a data-only ICU object whose load-command
metadata says iOS Simulator 18.5. That object has zero bytes of executable text
and no undefined symbols, while the final app binary reports minimum iOS 15;
Xcode still emits a linker-version warning. This is build evidence, not an iOS
15 runtime pass, so physical iOS 15 smoke remains a release gate. Google Play's
2026 submission deadline requires target API 36.

## Consequences

CI needs Linux/Android and macOS/iOS jobs. Stable-version compatibility is
verified by actual Android and iOS builds. API 24 remains a release gate rather
than an assumption: manifest merge, install, cold start, city selection, network,
and cached/offline behavior must pass on that floor. A dependency incompatibility
may justify pinning the newest compatible stable Kotlin patch and updating this
ADR.

Widget compatibility follows the same evidence boundary. The extension must
compile with a minimum iOS 15 load command; iOS 15 exposes the home-screen
families, iOS 16 adds accessory families, and iOS 17 adds removable container
background behavior. Compiler and binary evidence do not replace runtime smoke
on those system generations.

The Android 7 trust store is also part of that floor. Nimbo uses a
domain-scoped Network Security Configuration with the official ISRG public roots
for its three Open-Meteo hosts; cleartext, user-installed CA trust, and global
custom trust remain prohibited. The policy must be exercised on API 24 rather
than inferred from a successful API 36 build.
