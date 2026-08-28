# Apple runtime smoke — 2026-08-28

## Verdict

- **iOS 18.1 simulator: PASS** for Release build, clean onboarding render, live Bukhara weather from Open-Meteo, persisted-location cold launch, and absence of a captured fatal/error log line.
- **Physical iPad mini: PASS (bounded)** for local Release signing, install, launch, real forecast/cache population, Widget extension process startup, cold relaunch, and cleanup. Visual interaction, VoiceOver, permission denial, offline recovery, and widget rendering were not proven on the physical device.
- **Physical iPhone 14 Pro: BLOCKED** before build/install. The paired device is visible with Developer Mode enabled, but CoreDevice reports `connected (no DDI)` and Xcode reports `The developer disk image could not be mounted on this device.` No app was installed or modified on that iPhone.
- **iOS 15 runtime: NOT RUN.** The oldest installed simulator runtime is iOS 18.1 and the connected devices run iOS/iPadOS 26.x. The app binary itself declares `minos 15.0`, but that is build evidence, not runtime evidence.

## Release artifacts

| Artifact | Result |
|---|---|
| `NimboSimulator.app`, Release arm64 simulator | Xcode build passed and launched on iPhone 16 / iOS 18.1 |
| `Nimbo.app`, Release arm64 device | Xcode build passed, deep signature verification passed |
| `NimboWatch.app`, Release arm64 watch simulator | Xcode build and validation passed for watchOS simulator target 10.0 |
| Main device binary SHA-256 | `e557eddd2a31f76183b13337accc219ab1a6128f8517d4a2f8ea1831295b371c` |
| Main device binary / dSYM UUID | `11A5C54B-6B66-3187-AE0E-8A850CF89EE7` on both |
| Main binary deployment target | `LC_BUILD_VERSION minos 15.0`, SDK 26.5 |
| Local identifier | `uz.ganikhodjaev.weather`, `1.0.1 (4)` |

The growth worktree intentionally remains an unnumbered candidate: its checked-in
version still matches the distributed build until an external upload is
authorized. This locally built binary was not uploaded to TestFlight or App
Store Connect.

The simulator linker still emits the documented warning that the data-only
`libicu.icudtl_dat.o` member was built with simulator minOS 18.5 while the app
links for 15.0. The final app executable records minOS 15.0 and runs on iOS
18.1, but an actual iOS 15 runtime remains the release gate for that boundary.

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

1. Unlock/connect the iPhone so Xcode can mount its Developer Disk Image, then
   repeat clean install, denied location, city search, live forecast, cached
   offline recovery, large text, VoiceOver, share, widget, and cold start.
2. Run an actual iOS 15 device/runtime smoke or explicitly raise the declared
   deployment floor after a separate product decision.
3. Re-run the paired Apple Watch/widget UI smoke for any versioned upload.
4. Keep acquisition blocked until the existing production iOS crash report is
   obtained and symbolicated; a clean candidate smoke cannot close that gate.
