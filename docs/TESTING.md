# Testing and validation

## Glass optimization acceptance — October 7, 2026

Current product source: `70fc7a89194aeaf3532362d4edc026ee56f2f63a`. This pass implements the glass rendering optimization and live iOS Dynamic Type updates; previous acceptance sections below are historical. Detailed physical methodology and the still-unmet strict smoothness threshold are in [PERFORMANCE.md](PERFORMANCE.md#glass-optimization--october-7-2026). Evidence root: `build/glass-optimization-2026-10-07`; artifact hashes and validation counts: `build-and-validation-receipt.json`.

`scripts/local-ci.sh full` passed with the existing user storage wrapper intact and repository-local AVDs (`ANDROID_AVD_HOME=$PWD/.codex/release12-android/avd`). The final rerun (`local-ci-final.log`, exit0,10:43local) ran371 Python checks,173 Android shared tests,161 shared iOS Simulator tests,13 phone/10 Wear unit tests,37 Swift surface/widget tests, lint/migration/release checks, Android/Wear bundles and unsigned iOS/watchOS builds. All75 instrumented tests passed across API24 phone, API36 phone and tablet, with no skips. All28 existing visual goldens passed without replacement or threshold changes. Reviewed current RU/light, UZ/dark, RTL/stale and200% text outputs retain card geometry, labels and selected states. The suite includes three collector regression tests covering Android header variants, reset cutoffs, rolling-buffer duplicates and retention of long valid stalls. Removing the collector's old10second outlier cap changes no recorded sample; none contained such a valid stall.

The first CI attempts exposed stale current-source references in the blocked release registry/dashboard/featuring drafts. These references were synchronized; historical signing, delivery, metrics and blocked distribution status remain unchanged. No external workflow, store upload or publication occurred.

### Current runtime checks

- **Samsung SM-S908E/Android16, optimized release QA package:** light/dark, Auto/Fahrenheit/mph settings and return; hour selection/current-hour return; Bukhara/Samarkand independent selections; process removal followed by QA-widget launch retaining Bukhara11:00. Original main installation/data preserved. The natural worker and background network activity were observed as detailed below; the new fetch timestamp on the visible widget remains unverified.
- **iPhone18Pro/iOS27 simulator:** current Release output was installed in place with local ad-hoc App Group entitlements and its current Watch app. EN/dark, selection and cards, scrolling, city change, opaque reduced-transparency and reduced-motion settings were exercised. The old implementation reproduced a live Dynamic Type defect: changing the system text size, including Home/resume, required relaunch, whereas native Settings changed immediately. A root density observer now handles content-size notifications and foreground restoration without recreating the controller; two iOS regression tests cover updates and observer disposal. On the final installed build, size3→8→3 immediately changed text in the existing process while11:00 remained selected. `simctl ui content_size` independently confirmed `large→accessibility-large→large`; details remained readable after scrolling. PID35610 remained unchanged across the large-to-standard transition. Size3/standard `large`, effects off and VoiceOver off were restored. Final screens: `iphone-final-standard-selected.png`, `iphone-final-live-large.png`, `iphone-final-live-large-details.png`.
- **iPad11M4/iPadOS18.5 simulator:** RU/light, Tashkent forecast,12:00 selection and portrait→landscape→portrait retained selection and usable two-column cards. The final70fc7a8 build also resumed in the same PID37001 after changing text through native iPad Settings to `accessibility-large`:12:00 remained selected and cards changed to a readable single column. `simctl` verified the category and its restoration to `large`. Device Hub slider positions did not match this older runtime, so those attempts were excluded in favor of native Settings. Screens: `ipad-final-large-selected.png`, `ipad-portrait-selected.png`, `ipad-landscape-selected.png`.
- **Watch Series12/watchOS27 simulator:** the glass-build companion received a foreground city change from Samarkand17°C to Fergana18°C/fetched10:21. WatchConnectivity receive logs and `watch-fergana-delivery.png` agree. The final full-CI binary was subsequently installed and launched, retaining Fergana and the10:21 snapshot; at11:01 it displayed19°C (`watch-final-retained.png`). This is simulator delivery and persistence, not autonomous physical Watch behavior.

VoiceOver exposed descriptive hour labels, NOW and selected-state semantics; three actual swipe gestures moved visible focus through header controls to an hour, with automatic scrolling to reveal it. This is a partial focus check, not a spoken-output or complete gesture journey. No physical iOS, unplugged energy, overnight idle or distribution-runtime claim follows from these simulator/USB checks.

### Natural background observation and remaining acceptance

The Samsung QA app stayed in the background after 09:57:57 local. The 09:59 worker reused the 09:22 snapshot; the widget changed temperature while retaining 09:22, so this was explicitly excluded as fresh-fetch evidence. Without opening or reinstalling the app, forcing jobs or changing the clock, the next natural worker started at 11:00:00 and returned `SUCCESS` at 11:00:07. At the same time it broadcast `WIDGET_DATA_CHANGED` and updated widget ID20. UID11435 network counters increased by 21,893 received and 5,664 sent bytes in DEFAULT/background; FOREGROUND counters did not change. Logs contain no Nimbo activity launch after the cutoff. This establishes natural scheduling with network activity and a widget update request. A new visible fetch timestamp is still required to close the complete fresh-forecast-to-widget check.

Evidence: `natural-background/{samples.jsonl,process-3511.log,activity.log,network-before.txt,network-after.txt,controlled-interventions.txt}`. The network was briefly disabled and restored at 10:35–10:36 during an attempted separate no-cache check; it was available well before the natural interval. The additional `.emptyqa` package was never launched and was removed. No new physical no-cache result is claimed from that attempt.

Samsung was occupied by concurrent Cooksy QA from approximately 10:41. Its UI was not taken over, so the final widget screenshot, another controlled performance pair and the remaining physical acceptance could not be completed. Current automated fixtures cover onboarding, cached errors/retry, UZ, RTL, 200% text and city restoration; the broader earlier physical pass remains historical evidence. Full spoken TalkBack/VoiceOver acceptance, physical iOS, unplugged energy and long-idle delivery remain open.

Task-owned Samsung refresh and brightness overrides were restored and read back (`settings-restored.json`). Network was restored; Android Studio mirroring was closed and its screenshot directory returned to Desktop. Concurrent Cooksy font/night changes were left under that task's control. Apple text size, orientation and effect settings were restored. Final additional screens include `ipad-final-standard-selected.png` and `ipad-final-large-selected.png`. **This is a substantial local improvement with passing CI, not completed premium-quality acceptance: the strict physical smoothness target remains unmet.**


Nimbo combines deterministic tests, repository policy scripts, cross-platform compilation, and manual release evidence. The scopes are intentionally separated so a passing unit suite is not mistaken for completed device or store QA.

## Physical Samsung acceptance — October 7, 2026

The user-authorized pass used Galaxy S22 Ultra SM-S908E/Android16 and a freshly installed release-optimized `.physicalqa` APK from `219dd53`. Its build receipt, hash, diagnostics and screenshots are under `build/samsung-acceptance-2026-10-07`; [PERFORMANCE.md](PERFORMANCE.md#physical-samsung-follow-up--october-7-2026) records the build and measurements. The existing main and `.debug` installations and their data were preserved.

- **Passed:** RU onboarding/manual city choice; hourly selection, return to current hour, daily/details/outdoor cards; Tashkent/Samarkand city-specific hour and scroll restoration; light/dark and metric/imperial settings. Background process termination with PID disappearance followed by reopening retained the chosen city, hour, scroll, theme and units.
- **Passed:** cached offline refresh stopped its spinner and displayed saved-data/error feedback; uncached Bukhara displayed retry/change-city actions; restoring Wi-Fi/data and retrying recovered the forecast. No crash/ANR appeared in the inspected app logs or exit records; deliberate background kills are recorded separately.
- **Passed:** RU/UZ and Arabic RTL on the physical phone; chronological hour axis remained LTR. Font scale2.0 and landscape remained usable without observed overlap; original font0.9 and orientation settings were restored.
- **Passed:** a QA home widget was installed separately from the existing main widget; tapping it opened the correct QA app/city. Natural hourly worker execution and the09:00 cached widget rollover were observed without opening the app. The worker reused a53minute-old snapshot as designed; fresh network retrieval during a natural worker remains unconfirmed.
- **Partial accessibility:** Samsung TalkBack16.0.01.0 was enabled. Keyboard focus reached city/refresh/settings/current-hour/hour actions, visible speech-output captions described the selected hour, and Enter selected09:00 and updated details. Android Studio's mouse/stylus input did not establish full native TalkBack gesture traversal. Samsung's multimedia-only screen recording had a silent audio track; actual speech quality was not assessed. No microphone recording was used.
- **Performance concern:** five cold starts had median292ms, but repeated normal-glass vertical scroll samples showed GPU p95 about19ms and frame p95 about36ms. Opaque-card diagnostics were faster; this needs focused profiling/optimization, not a premium-smoothness sign-off.

Temporary locale, font, orientation, network, TalkBack/caption, TTS, contrast, keyboard and screen-recorder audio changes were restored. Android Studio's screenshot directory and temporary mirroring stay-awake override were restored too. The QA package and its widget remain available for inspection; the temporary silent recording was removed. Screenshots include `samsung-final-ru.png`, `samsung-ar-hour.png`, `samsung-uz-main.png`, `samsung-talkback-hour.png` and `samsung-widget-natural.png`.

This pass closes the previously unavailable Samsung functional/tap-through checks. It does **not** close full screen-reader speech/gesture acceptance, sustained unplugged energy and long-idle behavior, natural fresh-fetch delivery, physical iOS or distribution signing. Product source and goldens were unchanged; the optimized Android build and `git diff --check` passed. The earlier75-UI/28-golden full CI result remains prior evidence, not a rerun in this physical pass.

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


## Simulator follow-up — October 7, 2026

This follow-up checks remaining runtime scenarios on API36 `NimboPhoneApi36`, iPhone18Pro/iOS27 and iPad11M4/iPadOS18.5. HEAD was `219dd53`; the normal runtime binaries remain product-equivalent to `b845cfb`. No product code changed and the previously successful full gate below was not rerun. Evidence is under `build/simulator-acceptance-2026-10-07`; the additional rendering test is recorded in [PERFORMANCE.md](PERFORMANCE.md).

- **Home-screen widgets:** small widgets were installed through Device Hub on iPhone and iPad. They displayed the selected cities and real cached snapshots: Samarkand8°C on iPhone and Tashkent9°C on iPad. Tapping each widget opened Nimbo with that same city. The iPad was updated in place to the existing ad-hoc-signed simulator fixture with App Group entitlements; its city/preferences survived. This is simulator packaging, not distribution signing. Screenshots `ipad-widget.png` and `ipad-widget-open.png` record the iPad transition.
- **Natural WidgetKit refresh:** iPhone stayed on Home from06:25:24; the host process was suspended. The system requested a timeline reload for06:43:23. At06:44:23 the extension committed `lastEvent=widget_updated`, advancing `snapshot.updatedAt` from1791333803 to1791337463. The visible widget timestamp changed from05:43 to06:44 with the same selected city. No host launch, forced task, debugger trigger or clock change occurred during observation. Evidence: `iphone-widget-{before,after}.json`, `iphone-widget-{before,after}.png`, `iphone-widget-scheduler.log`, `iphone-widget-completion.log` and `background-observation.jsonl`. After ending observation, tapping the refreshed widget again opened Samarkand (`iphone-widget-open-after-refresh.png`). This closes one autonomous extension update on this simulator; it does not establish long-term cadence on physical iOS devices.
- **Android background execution:** after the AVD booted, the existing debug package's rescheduled `WeatherRefreshWorker` completed successfully at06:22:56 local time without opening Nimbo. Its surface snapshot advanced to epoch1791336175/06:22:55. WorkManager reported the next hourly job enqueued. This proves the boot-rescheduled fetch, not a complete subsequent hourly interval or physical Doze behavior. See `android-debug-process.log`, `android-jobs-initial.txt` and `background-observation.jsonl`.
- **Accessibility sample:** on iPad, VoiceOver-enabled controls exposed complete hourly weather labels; hour selection and return-to-now updated the selected state. The visible VoiceOver focus advanced from city to refresh to settings. Settings/back actions worked, but complete focus traversal and spoken output were not established. VoiceOver and keyboard capture were restored off; this is not full screen-reader acceptance.
- **Additional rendering test:** `ForecastPerformanceTest` passed1/1 with the host GPU renderer. Its short synthetic debug sample does not establish physical performance or smooth60fps interaction.

The simulator logs report `BGTaskScheduler` scheduling unavailable. Apple explicitly documents that Simulator does not support this background-task mechanism ([BGTaskScheduler.Error.unavailable](https://developer.apple.com/documentation/backgroundtasks/bgtaskscheduler/error/unavailable)); WidgetKit's background URLSession is a separate path. The Android standalone AVD was not exposed as a controllable native window, and Android Studio did not discover this repository-local AVD for embedded UI control. Fresh Android home-widget tap-through and full TalkBack interaction therefore remain unverified in this follow-up. Actual screen-reader speech, prolonged physical background/energy behavior and signed-device acceptance remain separate checks.

The task-created Android emulator and read-only observation process were stopped. The added iPhone/iPad widgets were removed without deleting app data, and accessibility settings were restored. Existing Apple simulators were left running. No fresh Nimbo crash reports appeared in the inspected iPhone/iPad report directories or Android crash buffer. Product code and visual baselines were unchanged; the user's existing `scripts/local-ci.sh` edits were preserved.

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
