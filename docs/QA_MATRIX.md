# Release QA matrix

This is the latest evidence checkpoint, not a declaration that store release QA is complete.

## Android

| Area | Evidence | Status |
| --- | --- | --- |
| Clean install and network render | Locally signed R8 APK on API 36; approximate location; semantic weather UI in 6,178 ms conservative bound | Pass |
| Cached cold/warm launch | Five release runs each; median 218 ms cold and 22 ms warm foreground | Pass |
| Offline cached / empty | Repository/state tests plus prior emulator offline launch | Pass |
| Partial provider response | Mapping/repository tests retain usable primary data | Pass |
| Arabic RTL | API 36 phone, large font, tablet landscape; chronological timeline remains LTR | Pass |
| TalkBack timeline | Real TalkBack service bound; focus moved hourly; 15:00 activated and details updated | Pass |
| Large text | 160% current pass; prior 200% pass; vertical scroll and controls remain usable | Pass |
| Tablet portrait/landscape | Adaptive constrained portrait and two-column landscape composition | Pass |
| Store screenshots | Five English and 24 localized 1080 × 1920 phone images, plus four 2560 × 1440 English tablet images from production UI; dimensions checked in CI | Pass |
| Release/R8 | Minify, resource shrink, lint vital, package and local install | Pass |
| Automatic refresh | Foreground resume/15-minute timer compiled; constrained 30-minute WorkManager job registered on API 36 and visible to JobScheduler | Pass |
| Production legacy install | Play App Bundle Explorer universal APK, artifact `4859919545693253619`, version 2 (1.0.1), Play certificate verified; clean install, network render, foreground/background, and offline cold launch passed | Pass |
| Real production upgrade | Google Play production 1.0.1 (2) updated in place to Internal Nimbo 1.0.0 (3); first-install time, Play installer, signing certificate, state, online/offline launch, locale/theme/units, timeline, history, and Best Time Outside were preserved | Pass |
| Play internal delivery | Upload key recovered and certificate matched; version code 4 RC2 is active for three internal testers. Preserved Play-installed vc3 updated to vc4 without uninstall; first-install time, installer, online render, cached airplane-mode cold launch, semantics, and crash check passed | Pass |
| Optional location hardware | Play review of version code 3 exposed 1 phone and 5 tablets excluded by implicit `android.hardware.location`; RC2 explicitly marks it optional and Play reports all six restored | Pass |
| Production submission | Version code 4 became available in 177 countries; version code 5 was subsequently submitted for review | Production live; update status last recorded as in review |
| 1.0.2 candidate | Phone vc6 and Wear OS vc1000006 pass clean build, bundletool validation, upload-certificate verification, universal-APK install, and cold-launch smoke on API 36/Wear OS emulators | Pass locally; physical paired-device smoke pending |

## iOS

| Area | Evidence | Status |
| --- | --- | --- |
| Clean simulator install | iPhone 16 Pro, iOS 18.1 | Pass |
| Arabic RTL | iPhone simulator; app RTL with chronological timeline LTR | Pass |
| Dynamic Type | `accessibility-extra-large`; stacked actions/details prevent horizontal collapse | Pass |
| Increase Contrast | Simulator setting enabled during large-text pass | Pass |
| Accessibility tree | Hourly items exposed as buttons with full localized summaries and selected state | Pass |
| iPad portrait/landscape | iPad Pro 11-inch (M4); portrait hierarchy and two-column landscape | Pass |
| Store screenshots | One localized production-UI image for each of 13 app languages on iPhone 16 Pro Max at 1320 × 2868 and iPad Pro 13-inch at 2064 × 2752; cached provider data | Pass |
| System permission localization | All 13 `InfoPlist.strings` permission descriptions packaged in the device archive | Pass |
| VoiceOver gestures/audio | VoiceOver is not exposed by this iOS Simulator runtime | Pending physical/TestFlight |
| Device archive | Xcode 26.6/iOS 26.5 SDK archive succeeds for arm64 with bundle ID and team verified | Pass |
| Automatic refresh | Foreground resume/15-minute timer and Background App Refresh handler compile; actual scheduling cadence remains system-controlled | Pass |
| Apple App ID | Explicit `uz.ganikhodjaev.weather` registered as Nimbo in team `5SWEZ7HTYP`; no optional capabilities enabled | Pass |
| App Store record | Record `6799886897` created for exact Bundle ID under store-only name `Nimbo Weather`; binary name remains Nimbo | Pass |
| App Store export | Profile `Nimbo App Store 1.0`; iOS 1.0 (1) IPA deep-codesign valid, `beta-reports-active=true`, `get-task-allow=false`, SHA-256 recorded in release journal | Pass |
| App Store upload | Xcode upload succeeded; Apple processed build 1, export compliance completed, and build is attached to version 1.0 | Pass |
| Store metadata | English metadata, review information, manual release, and production-UI iPhone/iPad screenshots saved | Pass |
| App Privacy | Published: Coarse Location and Search History for App Functionality only; not linked, not tracking; public privacy-policy URL saved | Pass |
| TestFlight | Builds 1 and 2 were processed; no tester was assigned and no physical TestFlight smoke is claimed | Not performed |
| App Review | iOS 1.0 build 2, submission `d44f3a55-ae31-4a17-9195-371ba9efa478`, submitted August 10, 2026 | Last recorded as Waiting for Review |
| 1.0 build 3 candidate | App, WidgetKit, and watchOS compile; automatic signing registered the new IDs/App Group; App Store export and deep codesign validation pass; required Apple Watch screenshot captured | Pass locally; physical paired-device/TestFlight smoke pending |

## External waiting states

- Google Play review and automatic 100% rollout of Production version code 5.
- Apple review of submission `d44f3a55-ae31-4a17-9195-371ba9efa478`, followed
  by the selected manual App Store release after approval.
