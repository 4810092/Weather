# Android pinned-source device smoke — 2026-08-29

## Verdict

**PASS within the bounded pinned-source/debug scope** for product commit
`f97238beb8d99cea5ed19883b1528dca4923baee`. Debug APK SHA-256
`7b2f2c12d56fdda293f19317ef6eb6da153213f84b1daeef11fd35f8e9e30edb`
was built from a worktree whose only uncommitted changes were growth content,
reporting, and evidence files; no application source differed from `f97238b`.
That APK was installed on the dedicated physical Android 7.1.1 / API 25 phone
and the Android 16 / API 36 `Nimbo_API_36` emulator. Current product source is
`9c2dce4200dbba5487c8c458ade4616005fde6e6`; none of this report's hashes or
device results is relabelled as exact-current evidence.

The pinned bytes passed physical onboarding, city selection, ordinary city
search, live forecast, share-chooser, legacy navigation contrast, and process
stability. On API 36 they also passed a true-offline cached cold start,
failed-refresh fallback, connectivity recovery, IME resize, and dark landscape
layout. No Nimbo crash or ANR was captured in the exercised paths. The pinned
rerun intentionally did not force an in-app Store review request; the
failed-refresh review-eligibility transition remains covered by the automated
test added in `f97238b`.

This is not a release-artifact pass. The APK is debuggable and uses the Android
debug certificate. The upload-signed vc8 artifact, physical tablet and widget
coverage, and paired physical Wear OS coverage are still missing. The
`android_physical_smoke` and `release_artifact_source_sync` gates therefore
remain blocked. This debug rerun closed the stale-source gap only at the
recorded source; it cannot replace exact-current signed-artifact QA.

## Pinned `f97238b` rerun

| Field | Value |
|---|---|
| Source commit | `f97238beb8d99cea5ed19883b1528dca4923baee` |
| Local APK | `app/build/outputs/apk/debug/app-debug.apk` |
| APK SHA-256 | `7b2f2c12d56fdda293f19317ef6eb6da153213f84b1daeef11fd35f8e9e30edb` |
| Package / version | `uz.ganikhodjaev.weather` / `1.1.0 (8)` |
| Build type / certificate | debuggable / Android debug certificate |
| Execution window | `2026-08-29 07:50–07:59 +05:00` |

### Physical API 25 phone

Target: dedicated General Mobile 4G Dual, Android 7.1.1 / API 25, 720 x 1280,
Russian.

| Scenario | Result | Evidence observed |
|---|---|---|
| Clean install and onboarding | PASS | The temporary package was absent before install; launch rendered localized value-first onboarding, Uzbekistan city shortcuts, ordinary search, and optional approximate-location disclosure |
| Tashkent live forecast | PASS | Selecting Tashkent rendered current conditions, yesterday comparison, hour insight, and the `24 часа назад · сейчас · 24 часа вперёд` timeline |
| Ordinary city search | PASS | Searching `Bukhara` without location permission returned a public result; selection rendered live Bukhara International Airport conditions |
| Share path | PASS | The platform chooser opened with `Поделиться с помощью:`; no target was selected |
| Legacy navigation contrast | PASS | Evidence PNG shows light content with a dark compatibility navigation scrim and visible three-button icons |
| Process stability | PASS within exercised paths | Filtered logcat contained no Nimbo fatal exception, process-crash, or ANR entry |
| Cleanup | PASS | The temporary package and its app data were uninstalled; package absence was verified. The Play-signed Samsung installation was queried read-only and remained installed |

Evidence:

- `growth/quality/evidence/android-current-head-2026-08-29/api25-bukhara-live.png`
- `growth/quality/evidence/android-current-head-2026-08-29/api25-bukhara-live.xml`

### API 36 emulator

Target: `Nimbo_API_36`, Android 16 / API 36, English.

| Scenario | Result | Evidence observed |
|---|---|---|
| Cached cold start | PASS | A force-stopped launch retained complete Tashkent forecast content |
| True offline fallback | PASS | Platform airplane mode disabled external connectivity (`ping` exit 2); cached content remained visible and refresh rendered `Couldn’t refresh. Showing saved weather.` |
| Recovery | PASS | Airplane mode was disabled, external connectivity returned, explicit refresh removed the fallback warning, and normal forecast content remained visible |
| IME resize | PASS | City search stayed visible above the keyboard while entering `Samarkand`; the captured hierarchy retained the editable field inside the resized content area |
| Dark landscape | PASS | Current forecast and action controls remained readable in dark 1920 x 1080 landscape with clear system-bar contrast and no edge clipping |
| Process stability | PASS within exercised paths | Filtered logcat contained no Nimbo fatal exception, process-crash, or ANR entry |
| Cleanup | PASS | Airplane mode, light theme, portrait/free rotation, and app state were restored; the temporary package was uninstalled and the no-snapshot emulator was shut down |

Evidence:

- `growth/quality/evidence/android-current-head-2026-08-29/api36-offline-refresh.xml`
- `growth/quality/evidence/android-current-head-2026-08-29/api36-recovered.xml`
- `growth/quality/evidence/android-current-head-2026-08-29/api36-ime.png`
- `growth/quality/evidence/android-current-head-2026-08-29/api36-ime.xml`
- `growth/quality/evidence/android-current-head-2026-08-29/api36-dark-landscape.png`
- `growth/quality/evidence/android-current-head-2026-08-29/api36-dark-landscape.xml`

## Historical commit-80 evidence

The following earlier matrix remains valid only for exact commit
`80cdd608b93056edd05e29873da43834a916cd3a` bytes. It is retained as a bounded
regression reference and is not substituted for the pinned rerun above.

### Historical artifact identity

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

### Historical physical API 25 phone

Target: General Mobile 4G Dual, Android 7.1.1 / API 25, 720 x 1280, Russian.

| Scenario | Result | Evidence observed |
|---|---|---|
| Exact pinned artifact install | PASS | `adb install -r` succeeded over the temporary same-certificate QA install; package state remained `1.1.0 (8)`, minSdk 24, targetSdk 36, and the pulled installed bytes matched the APK hash above |
| Retained-place online cold start | PASS | Force-stop and cold launch rendered the saved Tashkent forecast, comparison insight, timeline, and interactive controls |
| Legacy navigation contrast | PASS | Light-theme API 25 rendered white three-button navigation icons over the new dark compatibility scrim; the prior transparent/light low-contrast state was no longer present |
| Landscape inset path | PASS | Forced landscape retained Tashkent plus visible share and refresh controls inside the 1280 x 720 content area; device rotation settings were restored afterward |
| True offline cold start | PASS | Airplane mode was enabled through system Quick Settings, connectivity was independently absent, and a force-stopped cold launch rendered the saved Tashkent forecast |
| Expected offline refresh fallback | PASS | Explicit refresh logged the expected `UnknownHostException` and rendered `Не удалось обновить. Показана сохранённая погода.` while cached content remained usable |
| Connectivity recovery | PASS | Airplane mode returned to `0`, external connectivity and an Open-Meteo host probe succeeded, and no fallback warning remained after recovery |
| Share path | PASS | The platform chooser opened with `Поделиться с помощью:`; no target was selected, and returning to Nimbo preserved the running process |
| Process stability | PASS within exercised paths | Filtered logcat contained no Nimbo `FATAL EXCEPTION`, process-crash, or ANR entry |
| Cleanup | PASS | Airplane mode is `0`, Wi-Fi is connected, automatic rotation is restored, external network access succeeds, and the temporary Nimbo package was uninstalled; it was absent before this QA session and package absence was verified afterward |

### Historical API 36 emulator

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
- The pinned `f97238b` source contains the commit-80 removal of app-owned deprecated system-bar theme
  attributes. Google Play may still attribute compatibility calls inside
  AndroidX Activity to the app until a new bundle is processed and its expanded
  recommendation origins can be inspected; this report does not pre-claim
  console closure.
- Exact retry windows, single-flight behavior, review policy, share-link
  composition, and localization coverage remain backed by automated tests.
  The pinned device rerun records only the runtime paths directly exercised
  above and did not force or consume a Store review prompt.
