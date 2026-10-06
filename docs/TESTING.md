# Testing and validation

Nimbo combines deterministic tests, repository policy scripts, cross-platform compilation, and manual release evidence. The scopes are intentionally separated so a passing unit suite is not mistaken for completed device or store QA.

## Automated inventory

The source tree keeps common Kotlin tests, Android-host persistence/migration
tests, Android app unit tests, and iOS-specific tests in their native source
sets. Common tests execute for both Android host and iOS Simulator. Use the
Gradle/JUnit reports from the current commit as the authoritative count instead
of copying a number into this document. The Python validation suite is likewise
discovered dynamically with `python3 -m unittest discover -s
scripts/growth/tests -p 'test_*.py'`; its `Ran N tests` summary is authoritative.

| Area | Current evidence |
| --- | --- |
| Provider decoding/mapping | Ktor mock-engine city search/fallback; complete-row truncation; optional-array defaults; air-quality mapping. |
| Domain | Weather comparison, upcoming rain/temperature changes, two-hour outdoor scoring/hazards. |
| Time | IANA timezone conversion, spring/fall DST, local-day boundaries, ±24-hour timeline selection. |
| Privacy boundary | Positive and negative coordinates rounded symmetrically before use. |
| Presentation helpers | Unit preference/conversion, theme preference parsing, dark color contrast. |
| Growth paths | First-run state and UZ quick cities, denied/disabled/unavailable location outcomes, review retry/once-per-version rules, canonical share links, transient background retry classification, and stale activation/refresh race rejection. |
| Persistence | Saved-location/cache retention with the SQLite driver; released v1 fixture migration and retained data. |
| Compose UI | Android device-test coverage for no-auto-location onboarding, denied-location city search, forecast/tip/header semantics, cached-error retry, Uzbek LTR, Arabic RTL, and Russian UI at 200% font scale. |

The Compose suite renders deterministic production `WeatherScreen` states; it
does not call the live provider and does not replace signed physical-device or
assistive-technology QA. Fixed-state screenshot goldens now run on the pinned API36 phone/tablet.
Automated end-to-end live-provider tests remain a known gap. [QUALITY.md](QUALITY.md) and [QA_MATRIX.md](QA_MATRIX.md)
distinguish emulator automation from manual evidence.

## Fast contributor checks

For a common Kotlin/domain/data change:

```sh
./gradlew ktlintCheck \
  :shared:allTests \
  :shared:testAndroidHostTest \
  :shared:verifySqlDelightMigration
```

For documentation, resources, provider, privacy, or store inputs:

```sh
python3 scripts/check_repository.py
python3 scripts/check_localizations.py
python3 scripts/check_store_metadata.py
python3 scripts/check_store_assets.py
python3 scripts/check_store_previews.py
python3 scripts/check_dashboard_report.py
python3 scripts/build_site.py --output build/pages-check
python3 scripts/build_site.py --output build/pages-drafts-check --include-drafts
git diff --check
```

Run only the targeted checks that help during development. Before integration,
`bash scripts/local-ci.sh full` is the complete locally reproducible gate.
GitHub-hosted CI is not the routine authority and is not started by pushes or
pull requests.

## Android/shared gate

```sh
./gradlew ktlintCheck \
  :shared:allTests \
  :shared:testAndroidHostTest \
  :app:testDebugUnitTest \
  :wearApp:testDebugUnitTest \
  :shared:verifySqlDelightMigration \
  :app:assembleDebug \
  :app:lintRelease \
  :app:bundleRelease \
  :wearApp:assembleDebug \
  :wearApp:lintRelease \
  :wearApp:bundleRelease
```

The explicit release-lint tasks cover the full Android Lint surface; the release
bundles separately exercise R8/resource shrinking and lint-vital tasks. They are
unsigned development artifacts unless maintainer signing is supplied outside Git.

The phone and Wear unit-test tasks both execute the shared Android surface contract. Fixed timestamps cover empty and partial payloads, real zero values, the strict six-hour stale boundary, bounded clock skew, malformed future timestamps, and the visibility flags consumed by both UIs.

## Apple gate

Run `bash scripts/test_ios_surfaces.sh` for the deterministic Swift surface and widget-refresh suites. They cover Empty/Fresh/Stale rendering, the six-hour boundary, Open-Meteo request/response mapping, original fetch timestamps, legacy migration, cross-instance host/widget claim races, hour-long failure cooldowns, city changes during downloads, manual refresh, optional AQI and recovery with a newly created store instance. The primary forecast is committed without waiting for AQI; a later AQI delivery cannot be accidentally acknowledged by an earlier host import.

WidgetKit now starts its own background URLSession downloads and always requests another timeline, including for stale and empty caches. For natural scheduling QA, install the candidate, open it once to export the selected city, add the widget, then leave Nimbo backgrounded. Inspect `weather-refresh-v1.json` in the App Group: `lastEvent=widget_updated` and an advancing `snapshot.updatedAt` prove an extension-side completion. Check fresh app/extension crash reports and the visible widget; launching Nimbo, debugger-triggered tasks, or existing build-10 observations do not prove this candidate's natural refresh. iOS owns scheduling, so the requested hour is not a deadline.

The unsigned iOS and watchOS commands are documented in [DEVELOPMENT.md](DEVELOPMENT.md).
`bash scripts/local-ci.sh apple` runs both `:shared:iosSimulatorArm64Test`, the
Swift surface suite, and the two unsigned simulator builds.

## Android Compose UI gate

The `androidDeviceTest` source set uses the AndroidJUnitRunner and Compose UI
test v2. `bash scripts/local-ci.sh android-ui` runs
`:shared:connectedAndroidDeviceTest` sequentially on a local API 24 phone, API
36 phone, and API 36 tablet AVD. The runner auto-selects matching AVDs. Override
them with `NIMBO_AVD_PHONE_API24`, `NIMBO_AVD_PHONE_API36`, and
`NIMBO_AVD_TABLET_API36` when needed; a missing exact form factor/API fails
closed rather than silently reducing coverage.

The suite verifies deterministic UI behavior and semantics only. Emulator
success is not upload signing, Play delivery, physical phone/tablet evidence,
TalkBack gesture/audio proof, widget runtime proof, or Wear OS pairing.

## SQLDelight migrations

Schema changes require both migration layers:

- `:shared:verifySqlDelightMigration` verifies migration/schema parity;
- `:shared:testAndroidHostTest` includes [ReleasedDatabaseMigrationTest](../shared/src/androidHostTest/kotlin/uz/ganikhodjaev/weather/shared/data/ReleasedDatabaseMigrationTest.kt), which migrates `nimbo-v1.db` with the production Android driver path.

Do not replace a released fixture with a database produced only from the new schema; that would stop testing the upgrade boundary. New fixtures must be synthetic or sanitized.

## Manual validation

UI changes should be checked for:

- cached and first-run states;
- online, offline, stale, and provider-failure behavior;
- optional location grant/deny/disabled services and manual search;
- light/dark appearance and increased contrast;
- large text and narrow/expanded layouts;
- Arabic RTL with a left-to-right chronological timeline;
- TalkBack/VoiceOver semantics and selected-hour activation;
- widget/watch parity when the compact snapshot changes.

Simulator/emulator evidence is useful but does not prove physical-device battery behavior, Bluetooth/watch handoff, actual background scheduling cadence, VoiceOver gestures/audio, store delivery, or signing. The dated [QA matrix](QA_MATRIX.md) records which release checks were actually performed.

## CI behavior

`scripts/local-ci.sh` is the canonical ordinary CI entrypoint. `core`,
`android-ui`, and `apple` correspond to the former hosted jobs; `full` runs all
three. The Android emulator runner uses a portable TERM-then-KILL timeout and
writes local diagnostics below `build/android-ui-diagnostics`.

`.github/workflows/ci.yml` has only a manual trigger and must not be dispatched
for routine validation. It remains a separately authorized hosted fallback,
keeps read-only repository permissions, and delegates its core and Apple work
to the same local script to prevent command drift. Automatic GitHub execution
is reserved for capabilities that need a hosted trust boundary, OIDC, or the
unattended canonical rank writer. The former Trusted-to-Pages chain is dormant;
restoring a manual Pages publication path is a separately authorized workflow
change. The Gradle wrapper validates the official 9.7.0 distribution SHA-256,
and normal task resolution enforces the checked-in dependency verification
metadata.

`.github/workflows/signed-candidate.yml` is a distinct manual, environment-
protected GitHub-hosted path for maintainer release bytes. It never runs for a
pull request or push, accepts only `4810092/Weather` `master`, keeps
`contents: read`, and separates an exact-source unsigned build job with no
secrets from a fresh protected signing job. The first job transfers only a
checksummed inert unsigned package retained for one day. All third-party
actions are pinned to full reviewed commits; the repository validator binds
complete action blocks, run bodies, shells, exact secret environments, and
upload paths. The final job uploads only a receipt-bound signed tarball and
receipt after phone, Wear OS, Apple archive/IPA, profile, signer, Bundletool,
source-revision, closed-tree, mapping, and dSYM checks all pass. Ordinary
contributors and local CI never receive signing material.

No mutable repository script executes on the protected runner while secret
files or the unlocked ephemeral Keychain exist. The verifier scripts are
checked against reviewed SHA-256 pins before signing, copied outside the
checkout, rehashed after signing material is destroyed, and launched with
isolated Python path handling. The verifier rejects either detached-build or
current-checkout release-source drift from the manifest revision.

## Premium forecast visual and interaction checks

`PremiumForecastUiTest` uses a fixed clock (1725000000; night fixture +10 hours), fixed Tashkent timezone/data, explicit locale/theme/font scale and no provider network. The API24/36 phone and API36 tablet matrix covers sticky city/actions, all-day rain, stale/retry, preserved selection and vertical/horizontal scroll, pull refresh and tap/hold-drag selection. Arabic keeps the surrounding UI RTL and the time axis LTR. A semantic assertion does **not** prove TalkBack/VoiceOver speech.

API36 visual baselines live under `qa/visual/<matrix>`. The screenshot comparison preserves original dimensions; it tolerates channel deltas ≤12, at most 0.3% changed pixels and a mean channel delta ≤0.4. It writes amplified differences and JSON results beside actual screenshots. A changed inventory, resolution, or artifact predating the current run fails. These are pinned SwiftShader emulator baselines, not cross-device pixel expectations. The recorded environment is Android Emulator 37.1.11.0 (build 15917651), Google APIs API36 arm64 image revision 7 / extension 17, phone 1080×2424 at 420dpi and tablet 1600×2560 at 320dpi, with system animation scales 0. Test locale/theme/font and time are set in the fixtures; system-image/emulator changes require a reviewed baseline update. Review new screenshots before explicitly using `python3 scripts/check_visual_regressions.py --matrix phone-api36 --actual build/android-ui-diagnostics/phone-api36-glass --record` (similarly for tablet). Recording is never part of a normal gate.

`scripts/measure_forecast_rendering.sh` repeats the same fixed-data render, five refresh transitions and eight horizontal swipes. It records device/API/density/animation setting and gfx frame diagnostics. It deliberately does not change device settings. Run with an explicit `ANDROID_SERIAL` and before/after label. The first-render number includes Compose test synchronization; refresh is a rendering measurement, not provider latency or network recovery. Compare like-for-like and keep physical-device results separate from emulator results.


## Independent acceptance — October 7, 2026

Final acceptance source is `90ec87f` (product fixes `b845cfb`, then a UI test correction); metadata HEAD during the gate was `4e479cc`. `scripts/local-ci.sh full` passed: 368 Python checks, 173 Android-host/shared tests, 159 shared iOS Simulator tests, 13 phone and 10 Wear unit tests, 37 Swift surface/widget tests, lint/migrations, Android/Wear bundles and unsigned Apple builds. The API24/36 phone and API36 tablet matrix passed **75/75 UI tests without skips**. All **28/28** visual comparisons had zero pixel differences. No baseline was changed. The retained log is `build/acceptance-2026-10-06/local-ci-full.log`; raw matrix diagnostics remain under `build/android-ui-diagnostics`.

Two product defects were reproduced before fixing:

- The city picker/loading path restored another city's selected hour and scroll. The saved screen provider now uses the city ID. The new UI regression selects a future hour, switches through loading, checks the new city's current hour, then restores the first city's selection. Live iOS switching also passed. The older recent-days test now scrolls the new city's **vertical** page to the row while retaining its horizontal chronological-position assertion.
- A failed city persistence operation canceled observation of the previous city. Further successful refreshes could leave stale visible data, and an interrupted refresh could leave the spinner set. Failure recovery resumes observation and clears the canceled refresh state while preserving the picker. Saved-limit and persistence-failure regressions both failed against the original implementation, then passed with the fix, including a subsequent successful refresh.

Current normal runtime binaries were built at `b845cfb`; the later `90ec87f` change is test-only, and a product-path diff is empty. Android debug APK identity/hash is recorded in [PERFORMANCE.md](PERFORMANCE.md). Live inspection used API36 phone, iPhone18Pro/iOS27 and iPad11M4/iPadOS18.5 simulators. Screenshots in `build/acceptance-2026-10-06` cover EN/light Android, UZ/dark iPhone, RU/light iPad portrait and landscape, Arabic RTL with actual `accessibility-large` text on iPhone, reduced motion/transparency, selected-hour/settings return and the local midnight boundary. Main screens and current phone/tablet golden outputs were visually reviewed, including all-day rain97%, missing/equal negative hours, large Russian text and stale Arabic data. iPad's requested Device Hub size8/9 resolved only to `extra-large`; the actual accessibility category was verified separately on iPhone. Simulator display settings were restored to level3/effects off.

An isolated Android `.acceptance` package exercised first launch without network, denied location, visible first-fetch failure and retry after network recovery. Network changes were confined to that AVD and restored. After usable data was cached, Home → process termination (PID disappearance verified) → offline cold relaunch restored city, selected01:00 hour and vertical scroll; the visible before/after semantic tuples matched. The first `am kill` attempt did not terminate the process and was excluded. Existing deterministic tests additionally cover manual search/cancellation, city-switch races, late noncooperative responses, partial provider data, refresh failures, persistent cooldown, date rollover and stale recommendation boundaries. This is not proof of hours-long physical background behavior.

TalkBack on the own Android AVD was sampled for visible focus, hour selection and settings/back actions; VoiceOver-enabled iOS checks covered semantics and activation. Actual speech was not captured or evaluated, and full focus traversal was not established. Semantic assertions and successful clicks do not count as full screen-reader acceptance. TalkBack and VoiceOver were restored off on those test environments; physical accessibility preferences were untouched.

WatchConnectivity was tested with the existing paired iPhone/Watch simulators. The unsigned phone could not access its App Group and sent an empty context; logs proved receipt of that empty payload. A **compiled simulator fixture**, embedding the current Watch app and locally ad-hoc signed with the existing App Group entitlements (no credentials or distribution signing), then delivered real foreground snapshots: Fergana14°C/rain36%, followed by Samarkand10°C/rain0% after a city switch, with updated timestamps. Screenshots `watch-foreground-delivery.png` and `watch-city-switch.png` and the `phone-watch-*.log` files distinguish these cases. This proves foreground delivery/rendering, not autonomous refresh or signed physical operation. Wear API36/480×480 launched the source-equivalent debug APK (SHA-256 `5dac5cbf8769119c5052d2c25f45217d530c2ef561158fa8b8a3d69f1fe6a519`): empty state and the existing explicit demo fixture with negative temperatures/rain97% were inspected (`wear-final.png`, `wear-demo.png`). The emulator's sensor service crashed during boot; no Nimbo crash appeared in the inspected buffer. No paired Wear Data Layer delivery is claimed.

Physical inventory found SamsungSM-S908E/API36, a paired iPad mini with developer-built1.1.0(13), an unavailable iPhone and a paired Apple Watch. Samsung was occupied by another QA session and later locked; the compatible test-package signature was checked, but its app was not updated or foregrounded. iPad launch timed out, screen sharing requires iOS27 while it runs26.7.1, and libimobiledevice exposed no usable connection. Remaining checks require a free unlocked source-proven physical test build: speech/focus gestures, long idle and energy behavior, natural widget/background scheduling and paired watch recovery. Current home-screen widget installation/tap-through was not completed with the available UI controls; contract, freshness and callback tests passed but do not replace that host scenario. These gaps keep release/device acceptance open.

## Local premium-quality validation — October 6, 2026

`scripts/local-ci.sh full` passed on the final product source `9d09fb0`: 368 Python checks, 172 Android-host/shared tests, 158 shared iOS Simulator tests, 13 phone and 10 Wear unit tests, 37 Swift surface/widget tests, Kotlin lint, migration verification, release lint, Android/Wear bundles and unsigned iOS/watchOS builds. All three Android UI targets passed 24/24 without skips; all 28 visual goldens matched exactly. Full log: `/tmp/nimbo-premium-final-full.log`.

Runtime screenshots are in `build/premium-quality/runtime`; deterministic phone/tablet baselines are in `qa/visual`. Final Android, iPhone and iPad builds were launched and visually inspected. iPhone Dynamic Type at Device Hub level8 (applied after restart), Reduce Motion/Transparency and vertical scrolling were checked, then the simulator settings restored to level3/off. Live Android checks covered denied location, manual Samarkand search, a Tashkent city switch, retained offline data, a visible failed refresh and network recovery. iPhone/iPad simulators were inspected with RU/UZ, light/dark, night symbols, selected-hour/settings return and reduced effects. The fixed UI matrix additionally covers Arabic RTL, 200% text, a long city name, first launch/loading/error, all-day rain, negative/equal temperatures and an hour gap.

Physical Samsung debug instrumentation measured rendering and refresh without changing settings; TalkBack was disabled. A later ordinary-app measurement was stopped when another foreground app appeared, so no real-time physical scroll result is claimed. The temporary `.premiumqa` package was removed. Its initial build configuration also updated the pre-existing `.debug` binary; no data reset or main-package update occurred. Physical iPhone was unavailable; the paired iPad cannot use these unsigned simulator binaries. Real VoiceOver/TalkBack speech, natural background/widget scheduling, battery drain, and distribution-build physical performance remain separate device checks. See [PERFORMANCE.md](PERFORMANCE.md) for comparable measurements and limits.
