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
| Store screenshots | Five 1080 × 1920 phone and four 2560 × 1440 tablet images from the locally signed R8 build; dimensions checked in CI | Pass |
| Release/R8 | Minify, resource shrink, lint vital, package and local install | Pass |
| Production legacy install | Play App Bundle Explorer universal APK, artifact `4859919545693253619`, version 2 (1.0.1), Play certificate verified; clean install, network render, foreground/background, and offline cold launch passed | Pass |
| Real production upgrade | Google Play production 1.0.1 (2) updated in place to Internal Nimbo 1.0.0 (3); first-install time, Play installer, signing certificate, state, online/offline launch, locale/theme/units, timeline, history, and Best Time Outside were preserved | Pass |
| Play internal delivery | Upload key recovered and certificate matched; version code 4 RC2 is active for three internal testers. Preserved Play-installed vc3 updated to vc4 without uninstall; first-install time, installer, online render, cached airplane-mode cold launch, semantics, and crash check passed | Pass |
| Optional location hardware | Play review of version code 3 exposed 1 phone and 5 tablets excluded by implicit `android.hardware.location`; RC2 explicitly marks it optional and Play reports all six restored | Pass |

## iOS

| Area | Evidence | Status |
| --- | --- | --- |
| Clean simulator install | iPhone 16 Pro, iOS 18.1 | Pass |
| Arabic RTL | iPhone simulator; app RTL with chronological timeline LTR | Pass |
| Dynamic Type | `accessibility-extra-large`; stacked actions/details prevent horizontal collapse | Pass |
| Increase Contrast | Simulator setting enabled during large-text pass | Pass |
| Accessibility tree | Hourly items exposed as buttons with full localized summaries and selected state | Pass |
| iPad portrait/landscape | iPad Pro 11-inch (M4); portrait hierarchy and two-column landscape | Pass |
| Store screenshots | iPhone 16 Pro Max at 1320 × 2868 and iPad Pro 13-inch at 2064 × 2752; production UI and cached provider data | Pass |
| System permission localization | All 13 `InfoPlist.strings` permission descriptions packaged in the device archive | Pass |
| VoiceOver gestures/audio | VoiceOver is not exposed by this iOS Simulator runtime | Pending physical/TestFlight |
| Device archive | Xcode 26.6/iOS 26.5 SDK archive succeeds for arm64 with bundle ID and team verified | Pass |
| Apple App ID | Explicit `uz.ganikhodjaev.weather` registered as Nimbo in team `5SWEZ7HTYP`; no optional capabilities enabled | Pass |
| App Store record | Record `6799886897` created for exact Bundle ID under store-only name `Nimbo Weather`; binary name remains Nimbo | Pass |
| App Store export | Profile `Nimbo App Store 1.0`; iOS 1.0 (1) IPA deep-codesign valid, `beta-reports-active=true`, `get-task-allow=false`, SHA-256 recorded in release journal | Pass |
| App Store upload | Xcode upload succeeded; Apple processed build 1, export compliance completed, and build is attached to version 1.0 | Pass |
| Store metadata | English metadata, review information, manual release, and production-UI iPhone/iPad screenshots saved | Pass |
| App Privacy | Published: Coarse Location and Search History for App Functionality only; not linked, not tracking; public privacy-policy URL saved | Pass |
| TestFlight | Build 1 is processed and `Ready to Submit`; connected physical `iPhone (Khasan)` on iOS 26.6 is available; tester assignment and device smoke remain | Pending device smoke |

## Release blockers

- Promote the verified Internal RC2 version code 4 to Production.
- Assign the internal TestFlight tester and perform the physical-device/VoiceOver
  smoke test.
- App Review submission and external moderation.
