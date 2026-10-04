# UI completion candidate 13 — local source boundary

Source: `c8511e87fba06855f987ce9dabd87fbd21435fe8`. Prepared October 4, 2026.

Current candidates remain phone `1.1.0 (13)`, Wear `1.1.0 (1000013)`, Apple `1.1.0 (13)`. The changes cover shared Android/iOS UI, search cancellation, cached-data timestamps, date/detail presentation, library notices, and widget/watch update labels. The user authorized local implementation and verification only. No push, store upload, submission, or publication was performed.

Before the simulator recovery fix, `scripts/local-ci.sh full` passed for source `7ce879a3dc395dbe5546b723e7e9e5adfe07d5bf` on October4 (exit0, `/tmp/nimbo-ui-full2.log`): 367 Python/repository tests; 308 Kotlin tests (149 Android shared, 136 iOS shared, 13 phone, 10 Wear); 42 instrumented UI tests (14 each on API24 phone, API36 phone and API36 tablet); and 37 Swift surface tests. SQL migration verification, localization checks, Android/Wear release lint and bundles, and unsigned iOS/watchOS simulator Release builds passed. Regression coverage includes non-cooperative/out-of-order search, cache success timestamps, regions, missing values, timezone/midnight/DST dates, settings/licenses/back, selected-hour/scroll restoration, 200% Russian text, RTL, and error recovery in a240dp window. Fresh Android light/dark, settings200%, and daily-detail screenshots were inspected. These deterministic fixture tests are separate from a live-data end-to-end walkthrough.

The final local development iPhone build succeeded (`/tmp/nimbo-ui-iphone-final.log`), embeds the previous `7ce879a3dc395dbe5546b723e7e9e5adfe07d5bf` source revision, and was installed successfully on the connected iPhone14Pro. Launch was denied by iOS because the device is locked (`/tmp/nimbo-ui-iphone-final-launch.json`). This is development signing only. Current distribution artifact hashes, signing evidence, and signed-runtime evidence remain null; earlier tests/signing/store records are historical. No hosted CI was dispatched.

Xcode emitted minimum-simulator-version warnings for XCTest/ICU. Available-simulator success does not establish runtime compatibility on the oldest supported iOS release.

Simulator follow-up on source `e9b043ee1097a95ddea6b0c01d3751928235c9b5`:

- Full local CI passed again (exit0, `/tmp/nimbo-simulator-full.log`):367 Python tests,310 Kotlin tests (150 Android shared,137 iOS shared,13 phone,10 Wear),42 Android instrumented tests (14 each on API24 phone/API36 phone/API36 tablet),37 Swift tests. Release lint, SQL migrations, localization, bundles and unsigned iOS/watchOS Release builds passed. Fresh Android screenshot fixtures were inspected again.
- A real iOS27 iPhone18Pro simulator run exposed endless Loading for an uncached saved city when the unsigned simulator's shared App Group refresh store was unavailable. The fix preserves automatic throttling and offers manual recovery; regression coverage exercises StoreUnavailable, Cooldown and RetryDeferred. The rebuilt app visibly showed the recoverable error, and tapping Try again loaded real Samarkand weather with the successful update time. This is simulator validation, not signed distribution validation.
- Through CUA, verified real forecast, selected hour/date, day expansion and Close details, US AQI/category/time/attribution, recent-day layout/order, both themes, manual-unit description/selected semantics, Settings/Back, bundled licenses/Back, English support/about/privacy pages and native close return. The system Share sheet opened and was dismissed without sending. Original simulator Auto/System settings were restored. Saved cities were preserved.
- Search screen visibly keeps its field above saved cities and marks the current city visually and semantically; clear was exercised. Full text entry/search/cancellation/removal, first launch, geolocation, native large text/RTL/landscape/screen-reader traversal and offline/stale-cache runtime scenarios remain incomplete. CUA reported “The Mac is locked and automatic unlock could not unlock it” at the keyboard step; the user was asked to unlock the Mac. Android Studio did not expose the custom task AVD for manual CUA interaction; the42 instrumented emulator tests are separate evidence.
- Widget/watch natural refresh and background completion remain unverified; the unsigned iOS simulator explicitly logs unavailable shared App Group operations. Physical iPhone remains locked and still needs restoration of Automatic/System preferences from the previous physical QA (imperial/light). No user data was deleted, and no distribution signing/upload/publication was performed.

Live iOS CUA screenshots (saved by Device Hub):
- `build/simulator-ui-evidence/ios-live-aqi-day.png`
- `build/simulator-ui-evidence/ios-settings-dark.png`

Historical build12 SHA-256 identities remain only in each manifest artifact's `historical_candidate`. They cannot satisfy the blocked source/runtime gates for this source. Existing store submissions are unchanged.

Representative local screenshots (automated UI fixtures, not live weather):
- `build/android-ui-diagnostics/phone-api36-glass/dark.png`
- `build/android-ui-diagnostics/phone-api24-glass/ru-settings-font-200.png`
- `build/android-ui-diagnostics/phone-api36-glass/daily-details.png`


October4 resumed simulator check: Springfield and Guliston results include regions; changing a query removes prior results, no-result and clear states work, Search dismisses the software keyboard. A new Guliston was selected, loaded real weather after manual recovery, then removed after testing both Cancel and Remove confirmations. Original saved cities remain. Denied geolocation shows the city-search recovery message. Maximum Dynamic Type (Device Hub11) was verified in English/Russian after process restart, with Reduce Motion/Transparency enabled; Russian landscape settings also render without text truncation. These checks used e9b043e before the hour fix below. CUA coordinate gestures subsequently returned noWindowsAvailable; the user was asked to keep the Device Hub window visible.

The live run also exposed premature current-hour selection after half past. Source `c8511e87fba06855f987ce9dabd87fbd21435fe8` uses the latest available hour whose start is not in the future, with an earliest-row fallback for an entirely future cache. Repository observation and refresh presentation share this rule; refresh uses its injected clock. Regression tests cover minute37, the midnight boundary, repeated DST hours, unsorted/incomplete caches and actual repository observation. Targeted host tests and ktlint passed (`/tmp/nimbo-hour-boundary-tests.log`). Full validation and installation of this final source are in progress; earlier full results do not validate the hour fix.
