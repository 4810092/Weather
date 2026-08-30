# Accessibility evidence matrix — 2026-08-30

Status: **HISTORICAL PREDECESSOR HARNESS; CURRENT SUCCESSOR HOSTED SUITE GREEN
ON ALL THREE PROFILES; PHYSICAL ACCESSIBILITY AND STORE DECLARATIONS BLOCKED**.

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

Current authority `704fd893e59d94d8e9a4971313a773b3fa545ab6` replaces the
generic activity with a dedicated activity that applies locale before
composition, verifies Compose observes the injected language, and derives
layout direction from the same locale. Targeted device-test ktlint,
compilation, and merged-manifest processing pass. Exact-source hosted
[run `33297505825`](https://github.com/4810092/Weather/actions/runs/33297505825)
at evidence commit `163ff034c2b93ec302c4c5bee3c49168e0b33ada` then passed
all five tests on the API 24 phone in 2m24s, API 36 phone in 3m15s, and API 36
tablet in 3m30s. No predecessor result transfers to the current authority.

## Automated source evidence

The new `shared/src/androidDeviceTest` suite contains five discoverable Compose
UI tests for:

- optional-location onboarding and denied-location city search;
- forecast/tip interactions plus share, refresh, and change-place semantics;
- cached refresh failure followed by retry recovery;
- Uzbek LTR and Arabic RTL resources/order;
- Russian onboarding at `200%` font scale.

The API 24 test target uses core-library desugaring for the shared
`kotlinx-datetime` code path. The current harness passed targeted ktlint,
device-test compilation, and merged-manifest processing locally; it was not
executed on a local emulator or device. Standard GitHub-hosted CI executed all
five tests green on the API 24 phone, API 36 phone, and API 36 tablet for exact
authority `704fd893e59d94d8e9a4971313a773b3fa545ab6`. The correct automated
result is now `hosted/passed`; physical TalkBack, large-text, and device-layout
coverage remains `blocked`, not inferred from emulator automation.

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
