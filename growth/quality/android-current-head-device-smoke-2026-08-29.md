# Android current-HEAD device smoke — 2026-08-29

## Verdict

**PASS within the bounded current-source/debug scope** for commit
`80cdd608b93056edd05e29873da43834a916cd3a`. The exact same debug APK bytes
were installed on a physical Android 7.1.1 / API 25 phone and an Android 16 /
API 36 emulator. The current artifact passed live and cached-weather paths,
true offline fallback and recovery, sharing, light/dark rendering, IME resize,
legacy three-button navigation contrast, and API 36 landscape layout with an
emulated side cutout. No Nimbo crash or ANR was captured.

This is not a release-artifact pass. The APK is debuggable and uses the Android
debug certificate. The upload-signed vc8 artifact, physical tablet and widget
coverage, and paired physical Wear OS coverage are still missing. The
`android_physical_smoke` and `release_artifact_source_sync` gates therefore
remain blocked even though the current source path now has bounded physical
phone evidence.

## Artifact identity

| Field | Value |
|---|---|
| Source commit | `80cdd608b93056edd05e29873da43834a916cd3a` |
| Local APK | `app/build/outputs/apk/debug/app-debug.apk` |
| APK SHA-256 | `e10aa48ffb5ea7ee2e6a9b43031e623731788a936e23dc94a3480386074d32bc` |
| Package / version | `uz.ganikhodjaev.weather` / `1.1.0 (8)` |
| Build type / certificate | debuggable / Android debug certificate |
| Execution window | `2026-08-29 06:52–07:04 +05:00` |

Pulling each installed base APK back from both targets produced the same
SHA-256 as the local APK. This proves the scenarios below exercised those exact
bytes, not merely another build with the same version code.

## Physical API 25 phone

Target: General Mobile 4G Dual, Android 7.1.1 / API 25, 720 x 1280, Russian.

| Scenario | Result | Evidence observed |
|---|---|---|
| Exact current artifact install | PASS | `adb install -r` succeeded over the temporary same-certificate QA install; package state remained `1.1.0 (8)`, minSdk 24, targetSdk 36, and the pulled installed bytes matched the APK hash above |
| Retained-place online cold start | PASS | Force-stop and cold launch rendered the saved Tashkent forecast, comparison insight, timeline, and interactive controls |
| Legacy navigation contrast | PASS | Light-theme API 25 rendered white three-button navigation icons over the new dark compatibility scrim; the prior transparent/light low-contrast state was no longer present |
| Landscape inset path | PASS | Forced landscape retained Tashkent plus visible share and refresh controls inside the 1280 x 720 content area; device rotation settings were restored afterward |
| True offline cold start | PASS | Airplane mode was enabled through system Quick Settings, connectivity was independently absent, and a force-stopped cold launch rendered the saved Tashkent forecast |
| Expected offline refresh fallback | PASS | Explicit refresh logged the expected `UnknownHostException` and rendered `Не удалось обновить. Показана сохранённая погода.` while cached content remained usable |
| Connectivity recovery | PASS | Airplane mode returned to `0`, external connectivity and an Open-Meteo host probe succeeded, and no fallback warning remained after recovery |
| Share path | PASS | The platform chooser opened with `Поделиться с помощью:`; no target was selected, and returning to Nimbo preserved the running process |
| Process stability | PASS within exercised paths | Filtered logcat contained no Nimbo `FATAL EXCEPTION`, process-crash, or ANR entry |
| Cleanup | PASS | Airplane mode is `0`, Wi-Fi is connected, automatic rotation is restored, external network access succeeds, and the temporary Nimbo package was uninstalled; it was absent before this QA session and package absence was verified afterward |

## API 36 emulator

Target: `Nimbo_API_36`, Android 16 / API 36, 1080 x 1920 portrait and
1920 x 1080 landscape, English.

| Scenario | Result | Evidence observed |
|---|---|---|
| Clean install and onboarding | PASS | After clearing temporary app data, the exact APK hash rendered English onboarding, Uzbekistan city shortcuts, ordinary search, and optional approximate-location disclosure without requesting location permission |
| IME / search resize | PASS | Focusing city search and entering `Tashkent` showed the IME; `adjustResize` moved the editable field from y=1171–1392 to y=827–1048, keeping it visible above the keyboard |
| Live forecast | PASS | Selecting Tashkent rendered live conditions, yesterday comparison, hour insight, the 24-hours-before/now/ahead timeline, and the post-forecast tip |
| Light and dark themes | PASS | The populated forecast remained readable with matching system-bar icon contrast in both modes; system night mode was restored to its original light setting |
| Portrait gesture navigation | PASS | The default gestural path rendered content and controls inside safe drawing bounds without system-bar overlap |
| Landscape cutout plus three-button navigation | PASS | With the official corner-cutout emulation and three-button overlay enabled, the root was 1920 x 1080; Tashkent began at x=164 and the action controls remained clear of the side cutout and right navigation bar. The cutout, navigation, and rotation overlays were restored afterward |
| True offline cold start | PASS | Platform airplane mode was enabled, a force-stopped cold launch retained the complete cached forecast, and explicit refresh rendered `Couldn’t refresh. Showing saved weather.` |
| Recovery | PASS | Airplane mode returned to `0`, external network access succeeded, explicit refresh removed the fallback warning, and normal content remained visible |
| Process stability | PASS within exercised paths | Filtered logcat contained no Nimbo `FATAL EXCEPTION`, process-crash, or ANR entry |
| Cleanup | PASS | Airplane mode is off, gestural navigation and free rotation are restored, no cutout overlay remains enabled, night mode is restored, and the temporary emulator was shut down |

The implementation follows Android's current guidance to call
`enableEdgeToEdge()` for backwards compatibility and apply `safeDrawing`
insets on all four sides. Android documents that side cutouts can obscure
landscape content and that `windowInsetsPadding(WindowInsets.safeDrawing)`
applies all-side protection:

- <https://developer.android.com/develop/ui/compose/system/insets-ui>
- <https://developer.android.com/develop/ui/views/layout/edge-to-edge>
- <https://developer.android.com/about/versions/15/behavior-changes-15>

## Boundary

- The Samsung API 36 phone with the Play-signed public build was intentionally
  left untouched because its Play App Signing certificate cannot be replaced
  by a local debug or upload certificate without uninstalling user data.
- This report does not claim physical API 24, tablet, widget, Wear OS, TalkBack,
  large-text, upload-signed, Play-processed, store-review, or production proof.
- Source-current code removes the app-owned deprecated system-bar theme
  attributes. Google Play may still attribute compatibility calls inside
  AndroidX Activity to the app until a new bundle is processed and its expanded
  recommendation origins can be inspected; this report does not pre-claim
  console closure.
- Exact retry windows, single-flight behavior, review policy, share-link
  composition, and localization coverage remain backed by automated tests;
  this smoke records only the runtime paths directly exercised above.
