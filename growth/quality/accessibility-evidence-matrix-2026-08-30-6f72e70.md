# Accessibility evidence matrix — 2026-08-30

Status: **EXACT-SOURCE HOSTED SUITE GREEN ON ALL THREE ANDROID UI PROFILES;
PHYSICAL ACCESSIBILITY AND STORE DECLARATIONS BLOCKED**.

This record is bound to release-source authority
`6f72e70fff6eb7566e06dd862e1fad09055343a4`. It distinguishes source
semantics and deterministic emulator automation from screen-reader use on
physical devices. It is not an App Store or Google Play accessibility
declaration.

Hosted run `33295070238` later executed all five tests on both phone API 24 and
API 36, but each phone job failed the Uzbek onboarding-title and Russian 200%
font-scale title visibility assertions; the tablet job stopped before emulator
start at the KVM permission gate. Successor authority `fb591e3` corrected those
viewport and KVM setup defects. Historical run `33296238901` then passed
ordinary Android in 1m55s, ordinary unsigned iOS in 20m38s, and the KVM gate on
all three UI profiles. Every UI job launched exactly five tests and failed the
same two zero-node Uzbek/Russian locale selectors because the generic activity
reset the requested locale before Compose resources were created.

Predecessor authority `704fd893e59d94d8e9a4971313a773b3fa545ab6` replaces the
generic activity with a dedicated activity that applies locale before
composition, verifies Compose observes the injected language, and derives
layout direction from the same locale. Targeted device-test ktlint,
compilation, and merged-manifest processing pass. Its exact-source hosted
[run `33297505825`](https://github.com/4810092/Weather/actions/runs/33297505825)
at evidence commit `163ff034c2b93ec302c4c5bee3c49168e0b33ada` then passed
all five tests on the API 24 phone in 2m24s, API 36 phone in 3m15s, and API 36
tablet in 3m30s. Evidence-head run
[`33299592101`](https://github.com/4810092/Weather/actions/runs/33299592101)
also passed against that same predecessor release-source tree.

Current authority `2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652` changes shared
provider decoding. Fourteen targeted Android-host and twelve targeted iOS
Simulator provider tests pass. Evidence-head commit
`fb877d30b2179a489f5ce18dd06d892461436540` then passed exact-source
[run `33300967788`](https://github.com/4810092/Weather/actions/runs/33300967788),
workflow run #117, in 24m01s overall. All five jobs succeeded, including all
5/5 accessibility UI tests on the API 24 phone in 2m36s, API 36 phone in
3m48s, and API 36 tablet in 4m18s; `android-and-shared` completed in 5m05s and
`ios` completed in 23m59s with 18/18 Apple surface tests green. The two hosted
runs above still remain preserved as non-transferable predecessor history.

The three current UI-result GitHub archives are:

| Archive | Bytes | GitHub archive SHA-256 |
| --- | ---: | --- |
| `android-ui-results-phone-api24` | 52,269 | `0f385db95e55c31fbf1789d9e9e57cbdfc7f02e7b5ab249ab69745a62a9d7517` |
| `android-ui-results-phone-api36` | 302,815 | `f934996c9addce8543df6eecfb5bbd5404c83b8b51182098437d2cf8d27a77f1` |
| `android-ui-results-tablet-api36` | 281,718 | `20d21e0a392b0e03058fe053b08912bdf6f4eb0b9470c5e4b7439f6cb432ee5c` |

These are GitHub archive digests for hosted emulator test results, not signed
candidate hashes or physical TalkBack/VoiceOver evidence.

## Automated source evidence

The new `shared/src/androidDeviceTest` suite contains five discoverable Compose
UI tests for:

- optional-location onboarding and denied-location city search;
- forecast/tip interactions plus share, refresh, and change-place semantics;
- cached refresh failure followed by retry recovery;
- Uzbek LTR and Arabic RTL resources/order;
- Russian onboarding at `200%` font scale.

The API 24 test target uses core-library desugaring for the shared
`kotlinx-datetime` code path. The accessibility harness passed targeted ktlint,
device-test compilation, and merged-manifest processing locally at the
predecessor checkpoint; it was not executed on a local emulator or device.
Standard GitHub-hosted CI executed all five tests green on the API 24 phone,
API 36 phone, and API 36 tablet for exact predecessor authority
`704fd893e59d94d8e9a4971313a773b3fa545ab6`; run #117 now supplies the same
5/5-per-profile hosted result for exact current authority `2cdd438`. The correct
current automated result is `hosted/passed`. Physical TalkBack, VoiceOver,
large-text, and device-layout coverage remains `blocked`, not inferred from
hosted emulator automation. The protected signing environment is still 4/8
secrets, the signed workflow has not run, and 0/3 current signed artifacts are
byte-verified.

## Evidence matrix

| Surface or behavior | Current source/automation evidence | Remaining boundary |
| --- | --- | --- |
| Location/search/header semantics | Production `WeatherScreen` semantics are exercised by deterministic Compose assertions | No TalkBack traversal, spoken output, or physical-device gesture evidence |
| Cached/offline retry | Saved-content error and retry recovery are exercised in the UI harness | No live-provider, process-death, or signed-artifact proof |
| Uzbek LTR / Arabic RTL | Resource rendering, quick-place visual order, and the production locale-direction helper are asserted | Timeline reading order and complete RTL screen traversal still need assistive-technology QA |
| Large text | Russian onboarding remains displayed and operable at `2.0` font scale in the harness | No full-screen clipping audit at platform maximum sizes on phone/tablet/iOS |
| Timeline/theme/unit semantics | Production source exposes localized descriptions, selected state, and radio-button roles | The new suite does not yet traverse every timeline, theme, or unit control |
| WidgetKit and Apple Watch | Source contains grouped and explicit range/stale labels; deterministic Apple data-state suites exist | No physical VoiceOver, paired watch, rotor, focus-order, or audio evidence |
| Store declarations | None | **Blocked; do not mark supported accessibility features from source or emulator evidence alone** |

## Physical close-out

Before any public accessibility declaration, run the exact signed candidate on
physical Android phone/tablet with TalkBack and on iPhone/iPad with VoiceOver;
exercise onboarding, search, timeline, settings, offline/retry, share, widgets,
and large text. Paired Wear OS and Apple Watch paths require their own hardware
pass. Bind every result to retained signed artifact hashes.
