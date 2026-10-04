# UI completion candidate 13 — local source boundary

Source: `e9b043ee1097a95ddea6b0c01d3751928235c9b5`. Prepared October 4, 2026.

Current candidates remain phone `1.1.0 (13)`, Wear `1.1.0 (1000013)`, Apple `1.1.0 (13)`. The changes cover shared Android/iOS UI, search cancellation, cached-data timestamps, date/detail presentation, library notices, and widget/watch update labels. The user authorized local implementation and verification only. No push, store upload, submission, or publication was performed.

Before the simulator recovery fix, `scripts/local-ci.sh full` passed for source `7ce879a3dc395dbe5546b723e7e9e5adfe07d5bf` on October4 (exit0, `/tmp/nimbo-ui-full2.log`): 367 Python/repository tests; 308 Kotlin tests (149 Android shared, 136 iOS shared, 13 phone, 10 Wear); 42 instrumented UI tests (14 each on API24 phone, API36 phone and API36 tablet); and 37 Swift surface tests. SQL migration verification, localization checks, Android/Wear release lint and bundles, and unsigned iOS/watchOS simulator Release builds passed. Regression coverage includes non-cooperative/out-of-order search, cache success timestamps, regions, missing values, timezone/midnight/DST dates, settings/licenses/back, selected-hour/scroll restoration, 200% Russian text, RTL, and error recovery in a240dp window. Fresh Android light/dark, settings200%, and daily-detail screenshots were inspected. These deterministic fixture tests are separate from a live-data end-to-end walkthrough.

The final local development iPhone build succeeded (`/tmp/nimbo-ui-iphone-final.log`), embeds the previous `7ce879a3dc395dbe5546b723e7e9e5adfe07d5bf` source revision, and was installed successfully on the connected iPhone14Pro. Launch was denied by iOS because the device is locked (`/tmp/nimbo-ui-iphone-final-launch.json`). This is development signing only. Current distribution artifact hashes, signing evidence, and signed-runtime evidence remain null; earlier tests/signing/store records are historical. No hosted CI was dispatched.

Xcode emitted minimum-simulator-version warnings for XCTest/ICU. Available-simulator success does not establish runtime compatibility on the oldest supported iOS release.

Simulator follow-up: the Mac became accessible for iOS Device Hub. Live UI exposed an uncached saved-city startup stuck in Loading when the unsigned simulator cannot claim the shared automatic-refresh budget. Source e9b043e now exposes a recoverable error without bypassing the budget. A new regression covers StoreUnavailable, Cooldown and RetryDeferred plus successful manual recovery; targeted Android host tests and ktlint passed. Updated full validation and simulator walkthrough are in progress. Android Studio currently rejects coordinate input with noWindowsAvailable.

Physical runtime blocker: the connected iPhone remains locked. The user has been asked to unlock the Mac and keep iPhone Mirroring connected. A limited pass on the earlier working build observed live Tashkent weather, Russian settings, manual units, and both themes; it does not establish the complete requested scenario or final source acceptance. The final cold launch also requires unlocking the iPhone. Remaining manual coverage: first launch/search/city change/removal, keyboard/geolocation, hourly/day details, AQI/history/licenses/web return, Share without sending, offline/stale-cache states, landscape, native screen readers/reduced motion/transparency, and widget/watch runtime. No user data was deleted. The test changed iPhone preferences to imperial/light; restoring the original Automatic/System preferences was blocked by the Mac lock and is the first action after access returns.

Historical build12 SHA-256 identities remain only in each manifest artifact's `historical_candidate`. They cannot satisfy the blocked source/runtime gates for this source. Existing store submissions are unchanged.

Representative local screenshots (automated UI fixtures, not live weather):
- `build/android-ui-diagnostics/phone-api36-glass/dark.png`
- `build/android-ui-diagnostics/phone-api24-glass/ru-settings-font-200.png`
- `build/android-ui-diagnostics/phone-api36-glass/daily-details.png`
