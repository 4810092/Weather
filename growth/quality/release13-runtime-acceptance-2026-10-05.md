# Local runtime acceptance — 2026-10-05

Current product source: `44d3f7862b61ef95bf2b686820cfba3fc05a7b25`.
This pass began at HEAD `b6bf0ab`, product source `32c8f315bb84286424d4a62b6e88064dba55f720`.
Phone/iOS runtime observations below used that unchanged phone/iOS source. The only
new product change aligns the Wear debug package with the phone's `.debug` package;
Data Layer requires matching application IDs. Release IDs are unchanged. A repository
regression check now enforces matching production IDs and debug suffixes. The new
Wear debug APK was installed and its empty state observed. Both built debug APKs
were independently checked with aapt2/apksigner: package and signing certificate
match (`/tmp/nimbo-debug-data-layer-identities.txt`). The user's existing
`scripts/local-ci.sh` dev-storage wrapper was preserved.

This is local evidence, not distribution signing, store submission or publication.
Candidate 13 remains draft-blocked; no build-12 signing evidence was transferred.

## Automated verification

The initial `scripts/local-ci.sh full` passed on October 5, exit 0:
`/tmp/nimbo-acceptance-full-2026-10-05.log`. After the Wear identity correction, the
first rerun exposed stale dependent dashboard/featuring source references; those were
synchronized without changing gate status. The full recheck passed, exit 0:
`/tmp/nimbo-acceptance-final-full-recheck-2026-10-05.log`.

Final post-change run: 367 Python tests; Kotlin/shared/native, phone and Wear unit tests;
60 Android instrumented UI tests (20 each on API 24 phone, API 36 phone and
API 36 tablet); 37 Swift surface tests; lint, migrations, localizations,
release contracts, Android bundles and unsigned iOS/watchOS simulator Release builds.

The Android UI matrix covers stale-cache presentation, recovery controls at large
font sizes, stale search-row removal, Russian 200% text, Arabic RTL, Android Back,
day details, chronology and current-hour centering. Fixtures are explicitly test
data; this does not certify manual end-to-end network interruption or spoken output.
Results and screenshots: `build/android-ui-diagnostics/`.

## Observed through CUA

| Surface | Actual result |
| --- | --- |
| iPhone 18 Pro, iOS 27 | Real saved Fergana forecast; Russian and Arabic, simulator Text Size 11, both themes, Reduce Motion/Transparency; wrapping settings, selected units and explanatory copy; scrolling licenses and return navigation. |
| iPhone RTL search | Software keyboard `london` returned London with England/United Kingdom; `londonqqqq` removed prior results and showed empty state; clear restored saved cities; Cancel dismissed keyboard and preserved Fergana. |
| VoiceOver | Enabled, visible focus moved Fergana → Uzbekistan → Settings; accessible activation and Back worked; selected unit/theme semantics exposed. Audio was unavailable: actual speech and announcement repetition are unverified. |
| iPhone network failure | A simulator-only, app-scoped HTTP CONNECT transport fault blocked Open-Meteo without changing Mac networking or TLS. Refresh kept readable Fergana and its successful 16:52 stamp, with an explicit saved-weather error. Recovery fetched real data at 17:02. |
| iPhone uncached city | On the QA simulator, selected previously unsaved Samarkand while transport was blocked: loading → error with Try again/Change place. Landscape retained both actions. Text Size 11 was requested but maximum scaling of this particular error screen was not independently established. Restoring transport and Retry fetched real weather at 17:16, then 17:18. Only that test city was removed through the confirmation dialog; original Tashkent remained. This was an uncached city, not a clean installation. |
| iPhone real old cache | QA simulator retained Tashkent from October 4, 14:10, about 27 hours old. Failure preserved that stamp; returning from Samarkand showed Saved weather/update needed. AQI was marked saved; daily cards used Mon 5 Oct/Tue 6 Oct instead of Today/Tomorrow; recent days increased chronologically. |
| iPad 11 M4, iOS 18.5 | Real Tashkent cache from October 5, 01:14, about 16 hours old, remained readable during failure; Russian saved-AQI warning, US AQI category/time, compact actual dates and separated onboarding actions observed. |
| iPad 13 M5, iPadOS 27 | Landscape, centered current hour, city selection/cancellation and widget deep link worked. Host keyboard injection was unreliable; actual software-keyboard search was tested on iPhone. |
| iPad Home widget | System update after boot at 16:01:44, before any Nimbo host process; visual widget time matched App Group `widget_updated`. Another autonomous update at 17:01:52, 3,608 seconds later, was observed with no forced reload. The host was foreground when returning later, so host absence is established only for the first cycle. |
| Apple Watch Series 12 46 mm, watchOS 27 | Paired with iPhone 18 Pro. Empty “Open Nimbo on your phone” → real Fergana 18°C/AQI 38, updated 16:52 → fresh phone delivery at 17:02 with AQI 40. The full Nimbo scheme embeds the watch companion; the separate NimboSimulator scheme does not. Correct ad-hoc simulator installation resolved the initial WatchAppNotInstalled test setup. |
| Wear API 36 | Corrected debug build 1000013 installed without clearing data; cold launch Status: ok, actual round-screen empty state observed. No paired phone snapshot available. |
| Android API 36 manual | Current debug build 13 city screen and large-font landscape were visible in Android Studio's docked Running Devices. CUA drag/rotation worked, but taps/typing into the embedded Android display did not reliably reach the guest. No successful city selection/offline recovery is claimed from these attempts. |

The scoped network harness used public NSURLSession proxy configuration in an
injected simulator-only helper, plus a localhost CONNECT proxy. TLS/weather payloads
were not modified. This establishes application transport-failure handling, not
physical airplane mode or Wi-Fi handover. All three injected apps were terminated
and relaunched normally; the helper/proxy was removed/stopped after verification.

## Evidence

CUA captures under `build/simulator-ui-evidence/`:

- `acceptance-watch-empty.png`, `acceptance-watch-live.png`, `acceptance-watch-received-update.png`
- `acceptance-iphone-network-failure.png`, `acceptance-iphone-network-recovery.png`
- `acceptance-iphone-uncached-city-error-landscape.png`, `acceptance-iphone-uncached-city-recovery.png`
- `acceptance-iphone-saved-stale-forecast.png`, `acceptance-iphone-stale-aqi-dates.png`
- `acceptance-ipad-stale-cache.png`, `acceptance-ipad-stale-aqi.png`
- `acceptance-ipad-widget-system-refresh.png`, `acceptance-ipad-widget-hourly-update.png`
- `acceptance-iphone-voiceover-focus.png`, `acceptance-iphone-ru-max-font-dark.png`
- `acceptance-iphone-ar-max-font-city.png`, `acceptance-iphone-ar-keyboard-results.png`
- `acceptance-android36-city-landscape-large.png`

Build/diagnostic logs: `/tmp/nimbo-watch-companion-adhoc.log`,
`/tmp/nimbo-wear-debug-identity.log`, `/tmp/nimbo-scoped-proxy.log`.
Ad-hoc simulator signing supplies test entitlements; it is not distribution signing.

## Confirmed limits

- CUA cannot hear VoiceOver/TalkBack. Focus/semantics are not a speech test.
- Android guest taps/keyboard are unreliable through the available CUA/Studio route;
  standalone qemu windows are absent from its app inventory and cannot be bound.
  Manual Android offline, keyboard, TalkBack and widget placement/delivery remain
  unverified. The API 24/36 phone/tablet instrumented matrix is recorded separately.
- The Wear emulator has no paired companion route: the task phone AVD is the
  Google APIs image without Play Store or the Wear companion package. Matching
  debug IDs fixes a prerequisite, but does not prove Data Layer delivery.
- Natural watch/widget staleness and watch background refresh were not observed.
  Real old-cache phone/iPad rendering and unit coverage do not substitute for them.
- Clean-install offline first launch was not manually completed; the simulator named
  First Launch QA already contained real user cache, which was preserved. The
  uncached-city failure/retry and automated no-cache cases are the available evidence.
- Exact store-signed candidate-13 runtime and a distribution crash window remain
  outside this local acceptance. Current binaries were not uploaded or published.
- The Mac locked again near the end, blocking further CUA actions and the final Wear
  screenshot save. Previously saved captures remain available. The Studio run-target
  selector could not be restored from NimboWearApi36 to its prior Samsung selection
  while locked; no unrelated project build/run was issued.

No user data was cleared, no physical iPhone settings were touched, and nothing was
pushed, uploaded or published. Original simulator language/font/effects and app
unit/theme settings were restored; Android test network/font/theme/rotation settings
were restored before stopping task emulators. Temporary AVD discovery symlinks were
removed. The unrelated Android Studio project was not edited.
