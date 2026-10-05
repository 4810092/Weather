# Candidate 13 source boundary

Source: `44d3f7862b61ef95bf2b686820cfba3fc05a7b25`. Updated October 5, 2026.

The current source also aligns the Wear debug package with the phone debug companion and adds a repository invariant for both identities. Release application IDs are unchanged. Current acceptance is recorded in [October 5 runtime evidence](release13-runtime-acceptance-2026-10-05.md); distribution signing remains blocked.

## Historical recent-days verification

The observations below were made against `32c8f315bb84286424d4a62b6e88064dba55f720` on October 4; they do not claim a new build of the current source.

Recent days now run from the oldest of the preceding seven calendar days through the current snapshot day. The current day includes available history plus the current hour, with duplicate timestamps and future hours excluded. Missing days remain absent. Saved forecasts retain their actual local dates and end at the last available date, without inventing today’s data. Initial scrolling reveals the last card; a new city or calendar day returns to the end, while same-day refresh and a round trip through Settings preserve manual browsing. Cards keep uniform height.

Targeted formatting, shared Android host tests and Android instrumented-test compilation passed (`/tmp/nimbo-recent-days-targeted.log`). New pure tests cover ascending dates, the partial current day, duplicate/future exclusion, city midnight/DST, missing days, stale snapshots and invalid timezones. The instrumented suite now requires 20 tests per device, including initial position, chronological placement, refresh/Settings restoration and city/day changes.

Fresh `scripts/local-ci.sh full` passed (exit0, `/tmp/nimbo-recent-days-full.log`): 367 Python tests, Kotlin/shared/phone/Wear tests, 60 Android UI tests (20 each on API24 phone, API36 phone and API36 tablet), 37 Swift tests, lint, migrations, localizations, release manifests, Android bundles and unsigned iOS/watchOS Release builds. The initial full run detected inconsistent generated release-authority markers in three documents; those were synchronized before the passing run. Product assertions and checks were not weakened. The Russian Android screenshot `build/simulator-ui-evidence/recent-days-chronological-at-today.png` shows the end position with October3 then October4; this is an instrumented fixture.

The fresh simulator app reports the source revision above. Generated iOS app/widget artifacts were locally ad-hoc signed with existing App Group entitlements and passed strict signature verification. Data-preserving installation and launch succeeded on iPhone18Pro/iOS27 and iPadPro13M5/iPadOS27. On iPhone, CUA confirmed the saved Fergana forecast, initial history end position with October3/4, and horizontal browsing back to September27/28/29 and forward to October4 with real weather data. Initial CUA scrolling failed with `noWindowsAvailable`; after reinstallation, drag gestures worked. Native screenshots are `build/simulator-ui-evidence/recent-days-iphone-{oldest,today}.png`. The iPad history row was not separately inspected in this pass. No physical-iPhone settings or saved city data were changed.

Fresh `:app:assembleDebug` passed (`/tmp/nimbo-recent-days-samsung-build.log`). `adb install -r` succeeded on SamsungSM-S908E, `am start -W` returned `Status: ok`, and the debug MainActivity was confirmed top-resumed. Existing release installation and debug data were preserved. Samsung manual gestures and actual VoiceOver/TalkBack speech are not claimed by these checks.

The canonical registry atomically marks Apple, phone, and Wear artifacts blocked until new signing and independent byte/runtime verification. Candidates remain phone1.1.0(13), Wear1.1.0(1000013) and Apple1.1.0(13); distribution hashes remain null and build12 records remain historical. Earlier forecast-feedback source59a0ad3 evidence does not validate this change. Simulator ad-hoc signing is not distribution signing. No push, hosted CI, upload or publication was performed.
