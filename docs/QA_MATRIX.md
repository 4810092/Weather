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
| Play internal delivery | Upload key recovered and certificate matched; version code 3 delivered and smoke-tested. Version code 4 RC2 upload is accepted and restores six hardware-location-filtered devices; activation and scoped smoke remain | Pending RC2 activation |
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
| App Store record | Team App Store Connect is accessible; no Nimbo app exists and the available Bundle ID list does not contain `uz.ganikhodjaev.weather` | Needs App ID |
| App Store export/TestFlight | Automatic export fails with `No Accounts` and no App Store profile; archive remains development-signed (`get-task-allow=true`) | Blocked externally |

## Release blockers

- Account Holder/Admin access to Certificates, Identifiers & Profiles to register
  explicit App ID `uz.ganikhodjaev.weather`, followed by Xcode account sign-in and
  an App Store distribution profile.
- Activate Internal RC2, install Play-delivered version code 4 over the preserved
  version code 3 test installation, and promote version code 4 to Production.
- Distribution-signed archive upload, TestFlight processing, and physical-device VoiceOver smoke test.
- Live store-form entry, upload processing, and moderation.
