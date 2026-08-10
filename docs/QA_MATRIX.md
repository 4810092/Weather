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
| Release/R8 | Minify, resource shrink, lint vital, package and local install | Pass |
| Real production upgrade | Exact Play production version is 2 (1.0.1), but the accepted upload private key is unavailable locally | Blocked externally |
| Play internal delivery | Cannot upload until the accepted upload key is recovered or reset | Blocked externally |

## iOS

| Area | Evidence | Status |
| --- | --- | --- |
| Clean simulator install | iPhone 16 Pro, iOS 18.1 | Pass |
| Arabic RTL | iPhone simulator; app RTL with chronological timeline LTR | Pass |
| Dynamic Type | `accessibility-extra-large`; stacked actions/details prevent horizontal collapse | Pass |
| Increase Contrast | Simulator setting enabled during large-text pass | Pass |
| Accessibility tree | Hourly items exposed as buttons with full localized summaries and selected state | Pass |
| iPad portrait/landscape | iPad Pro 11-inch (M4); portrait hierarchy and two-column landscape | Pass |
| VoiceOver gestures/audio | VoiceOver is not exposed by this iOS Simulator runtime | Pending physical/TestFlight |
| Distribution archive/TestFlight | Distribution certificate exists; matching App ID provisioning profile and authenticated portal session are absent | Blocked externally |

## Release blockers

- Android accepted upload private key or a completed Google Play upload-key reset.
- Authenticated Apple Developer/App Store Connect session and a profile for `uz.ganikhodjaev.weather`.
- Play-delivered legacy update test and Play internal smoke test.
- Distribution-signed archive upload, TestFlight processing, and physical-device VoiceOver smoke test.
- Final store declarations, screenshots, metadata, and moderation.
