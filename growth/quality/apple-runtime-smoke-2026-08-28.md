# Apple runtime smoke — 2026-08-28

## Verdict

- **iOS 18.1 simulator: PASS** for Release build, clean onboarding render, live Bukhara weather from Open-Meteo, persisted-location cold launch, and absence of a captured fatal/error log line.
- **Physical iPad mini: PASS (bounded) on 1.0.1 (4)** for local Release signing, install, launch, real forecast/cache population, Widget extension process startup, cold relaunch, and cleanup. On 2026-08-29 the exact archived `1.1.0 (5)` candidate also installed and reported the correct identity, but launch was blocked because the iPad was locked; it was immediately removed and is not counted as a runtime pass.
- **Physical iPhone 14 Pro: BLOCKED** before build/install. The earlier paired session reached `connected (no DDI)` and Xcode could not mount the developer disk image; on the 2026-08-29 recheck the device was unavailable. No app was installed or modified on that iPhone.
- **iOS 15 runtime: NOT RUN.** The oldest installed simulator runtime is iOS 18.1 and the connected devices run iOS/iPadOS 26.x. The app binary itself declares `minos 15.0`, but that is build evidence, not runtime evidence.

## Historical release artifacts

| Artifact | Result |
|---|---|
| `NimboSimulator.app`, Release arm64 simulator | Xcode build passed and launched on iPhone 16 / iOS 18.1 |
| `Nimbo.app`, Release arm64 device | Xcode build passed, deep signature verification passed |
| `NimboWatch.app`, Release arm64 watch simulator | Xcode build and validation passed for watchOS simulator target 10.0 |
| Main device binary SHA-256 | `e557eddd2a31f76183b13337accc219ab1a6128f8517d4a2f8ea1831295b371c` |
| Main device binary / dSYM UUID | `11A5C54B-6B66-3187-AE0E-8A850CF89EE7` on both |
| Main binary deployment target | `LC_BUILD_VERSION minos 15.0`, SDK 26.5 |
| Local identifier | `uz.ganikhodjaev.weather`, `1.0.1 (4)` |

The current source identity is `1.1.0 (6)`. It has an unsigned/ad-hoc simulator
build only; no distribution-signed build-6 archive exists and nothing from this
growth update has been uploaded to TestFlight or App Store Connect. The table
above remains scoped to the historical build-4 device candidate and the
previous simulator/watch checks.

## Current build-6 simulator recheck — 2026-08-29

The final growth-update source built both `NimboSimulator` and `NimboWatch` in
Release configuration without signing. A clean install of
`uz.ganikhodjaev.weather` `1.1.0 (6)` then launched on an iPhone 17 simulator
running iOS 26.5 and rendered the complete English onboarding surface. The
simulator executable SHA-256 was
`4bb8bf2707cd1170b2897d105e2ea9d7b41da25253ead829a809d73ce6099f3a`;
its signature was ad-hoc and had no TeamIdentifier.

The bounded log window contained no fatal, crash, uncaught-exception, or app
termination entry. It did contain the expected
`WCErrorCodeWatchAppNotInstalled`, because the intentionally contributor-safe
`NimboSimulator` scheme omits the watch companion. This is not counted as a
paired-watch pass or as physical evidence.

The simulator linker still emits the documented warning that the data-only
`libicu.icudtl_dat.o` member was built with simulator minOS 18.5 while the app
links for 15.0. The exact dependency path is Compose Multiplatform `1.11.1` ->
Skiko `0.144.6` -> `skiko-iosSimulatorArm64Main-0.144.6.klib` -> bundled
`libicu.a` -> `libicu.icudtl_dat.o`. `vtool -show-build` reports simulator
minOS 18.5 for that member; `otool`, `size`, and `nm` show a 6,296,800-byte
`__const` section, zero-byte `__text`, and no undefined symbols. The matching
iOS-device member reports minOS 12.0. A clean unsigned Release simulator build
still emits the warning and succeeds.

The latest stable Skiko artifact available during the 2026-08-29 audit,
`0.150.1` (Maven SHA-256
`f6d557c83ce431988913341d1030e188e4ac310cbaca71a2f39cc4ebe370f09f`),
contains the same simulator minOS 18.5 marker, so there is no verified
dependency-only upgrade that removes it. The audit did not rewrite the Mach-O
load command, suppress the warning, or raise the deployment target: each would
hide or redefine the compatibility boundary rather than prove it. The final app
executable records minOS 15.0 and runs on iOS 18.1, but **iOS 15 support remains
NOT VERIFIED and release-blocked** until an actual iOS 15 device/runtime passes,
or a separate product decision raises the declared deployment floor.

## Exact storage-hardening product recheck — 2026-08-29 22:11 +05:00

Product source `9c2dce4200dbba5487c8c458ade4616005fde6e6`
was rebuilt in isolated DerivedData with `CODE_SIGNING_ALLOWED=NO`, arm64-only
Release simulator destinations. The source closes deterministic database-error
escapes in saved-place deletion, unit-preference persistence, and
reverse-geocode enrichment; four throwing-repository regressions pass.

| Product | Executable SHA-256 | Binary / dSYM UUID | Result |
| --- | --- | --- | --- |
| `NimboSimulator.app` `1.1.0 (6)` | `b7c3ba937658007b07ee9ad8e85ddc892e90f423e7839e0dc112a1070ea04849` | `44F5F65F-080A-3F89-B5E5-D052EDF9A219` | Release simulator build and dSYM verification pass |
| `NimboWidget.appex` | `7191acd40334d4d9fec6062bc5023450fefbb55006fbd92f57109f41eb27a7ff` | `4DB04672-B8CF-3BD7-909B-D0869C744ABB` | Embedded extension build and dSYM verification pass |
| `NimboWatch.app` | `c310c785750ffa779e5dfdc30384088fca889deddb11417f2b4e8e0e30109728` | `58CE68C5-A8B1-32B9-BE4D-BEE8A8C531C0` | Release watch-simulator build and dSYM verification pass |

All three executables carry linker-generated ad-hoc signatures with no Team
Identifier. The shared iOS simulator suite, 18-case Swift surface suite, full
Gradle release gate, and 121-resource localization parity pass. The existing
Skiko `libicu` simulator minOS warning remains unchanged. This is exact-source
build/test evidence only: it is not distribution signing, iOS 15 runtime,
physical-device, Widget gallery, paired-watch, TestFlight, review, rollout, or
public-availability evidence.

## iOS 18.1 simulator scenarios

| Scenario | Result | Evidence |
|---|---|---|
| Fresh installation | PASS | No previous app container existed; `simctl install` succeeded |
| Clean onboarding | PASS | Accessibility tree exposed the value statement, Toshkent/Samarqand/Namangan, city search, and optional approximate location |
| Live Bukhara forecast | PASS | A bounded QA fixture inserted one active Bukhara row into the fresh app database; the released app then fetched and rendered current weather, yesterday comparison, first-forecast tip, and timeline |
| Persisted cold launch | PASS | Explicit terminate and relaunch reopened the live Bukhara surface |
| Crash/log check | PASS within path | No `fatal`, `crash`, `uncaught`, `exception`, or `error` line matched the NimboSimulator process log window |

Evidence:

- [iOS 18.1 live Bukhara screenshot](evidence/ios-simulator-2026-08-28-ios18.1-bukhara.png)
- [iOS 18.1 cold-launch screenshot](evidence/ios-simulator-2026-08-28-ios18.1-cold.png)

## Exact Apple 1.1.0 archive installation recheck — 2026-08-29

The available iPad mini's UDID was present in the archive's development
provisioning profile. The exact archived app at
`/Users/khasan/work/ganikhodjaev/.nimbo-release/ios/1.1.0-5/Nimbo.xcarchive/Products/Applications/Nimbo.app`
installed successfully and the device reported bundle `uz.ganikhodjaev.weather`,
version `1.1.0`, build `5`. The first launch was denied by SpringBoard with
reason `Locked`; no Nimbo process started, so provider, cache, widget, cold-start,
or visual behavior is not claimed. The app was immediately uninstalled and a
follow-up application listing confirmed it was absent.

The raw CoreDevice JSON contains device identifiers and is retained with mode
`0600` in the private release evidence directory rather than committed.

Computer accessibility could read the Simulator hierarchy but its native pipe
closed on every click. The QA fixture was therefore used only to exercise the
post-selection runtime path. It does not count as a permission-denial or city-
search UI pass.

## Physical iPad mini scenarios

The device was an iPad mini (5th generation) on iPadOS 26.6 with Developer Mode
enabled and DDI services available. Nimbo was absent before the run.

| Scenario | Result | Evidence |
|---|---|---|
| Signed Release install | PASS | `devicectl device install app` installed `uz.ganikhodjaev.weather 1.0.1 (4)` |
| Initial launch | PASS | Main app and Widget extension processes were present after five seconds |
| Physical live provider path | PASS | After inserting the active Bukhara row into this fresh QA container and running 12 seconds, the pulled database contained 408 weather-hour, 17 daily, 120 AQI, and 48 forecast-snapshot rows |
| Cold relaunch | PASS | A terminate-existing launch produced stable main-app and widget processes after six seconds |
| Cleanup | PASS | `devicectl device uninstall app` succeeded and a follow-up app listing confirmed removal |

The exact database observation is preserved in
[ios-physical-2026-08-28-ipad-db-counts.txt](evidence/ios-physical-2026-08-28-ipad-db-counts.txt).

## Remaining Apple gates

1. Build and distribution-sign current `1.1.0 (6)`, then unlock/connect the
   iPhone so Xcode can mount its Developer Disk Image and run that exact artifact
   on an unlocked iPad and iPhone for clean launch, denied location, city
   search, live forecast, cached offline recovery, large text, VoiceOver, share,
   widget, and cold start. Build 5 remains historical evidence only.
2. Run an actual iOS 15 device/runtime smoke or explicitly raise the declared
   deployment floor after a separate product decision.
3. Re-run the paired Apple Watch/widget UI smoke for any versioned upload.
4. Keep acquisition blocked until the existing production iOS crash report is
   obtained and symbolicated; a clean candidate smoke cannot close that gate.
