# Release QA matrix

Status date: September 4, 2026.

<!-- release-authority-current:start -->
<!-- source_revision:fc4b6de9e28fd8956eb64462294b8bcdf405ce7e -->
<!-- artifact:android_phone;source_sync=verified-current;byte_verified=true;physical_qa_evidence=none -->
<!-- artifact:wear_os;source_sync=verified-current;byte_verified=true;physical_qa_evidence=none -->
<!-- artifact:apple;source_sync=verified-current;byte_verified=true;physical_qa_evidence=none -->
<!-- physical_gate:android_physical_smoke=blocked;reason_sha256=89e62052d4c6b33524bdc48065e6bd67215e0b33f76e5fd1ad87dfbc92e6b756 -->
<!-- physical_gate:ios_physical_smoke=blocked;reason_sha256=08c6bc72471fa419add30834bca51e64079e9d07a472c65e70ed5c121840fb4f -->
<!-- release-authority-current:end -->

The machine-validated block binds replacement source
`fc4b6de9e28fd8956eb64462294b8bcdf405ce7e` to vc11, vc1000011, and corrected
Apple build 10. Protected run `33852229166` signed and
candidate-byte-verified the exact set, and run `33855931653` durably retained
it in unpublished draft `382592451`. Final manual-only trusted run
`33859392482` independently verified all three complete signed artifacts on
exact upload authority `d7dbdc3e`, so all current entries are atomically
`verified-current`. Apple build 10 is processed, attached to internal
TestFlight testers, and installed on the connected iPhone and iPad. Bounded
physical smoke and a visible iPad widget render are recorded separately; the
manifest physical-QA field remains null until a natural OS-scheduled refresh
and fresh post-completion crash-log observation are complete. The prior
vc11/vc1000011/build-9 bytes are
historical-superseded; build 9 is explicitly failed after exact TestFlight
background-refresh crashes in the main Nimbo process.

This document separates the exact `1.1.0` release candidate from historical
store and device evidence. The current block below is checked against
[`store/upload-manifest-1.1.0.json`](../store/upload-manifest-1.1.0.json),
[`growth/quality/gates.json`](../growth/quality/gates.json), and the platform
build files by `python3 scripts/check_release_qa_matrix.py`. A historical pass
must never satisfy a current artifact, signing, physical-device, store-review,
or public-availability gate. The same validator checks the hidden current-
authority block in this file, `growth/README.md`, `docs/GROWTH_RELEASE.md`, and
`docs/RELEASE.md`: full source revision, per-artifact source/physical-evidence
state from the upload manifest, and physical-gate status plus reason digest must
remain exact.

## Exact-current 1.1.0 candidate

<!-- release-qa-current:start -->
| Surface | Exact candidate | Manifest source sync | Manifest entry reverified/current | Release/source gate | Required runtime QA (legacy gate ID) | Fail-closed status |
| --- | --- | --- | --- | --- | --- | --- |
| Android phone/tablet | `1.1.0 (11)` | `verified-current` | `true` | `release_artifact_source_sync: pass` | `android_physical_smoke: blocked` | **BLOCKED** |
| Wear OS | `1.1.0 (1000011)` | `verified-current` | `true` | `release_artifact_source_sync: pass` | `android_physical_smoke: blocked` | **BLOCKED** |
| Apple app/widget/watch | `1.1.0 (10)` | `verified-current` | `true` | `release_artifact_source_sync: pass` | `ios_physical_smoke: blocked` | **BLOCKED** |
<!-- release-qa-current:end -->

`READY` is permitted only when the corresponding artifact is
`verified-current`, the shared release/source gate is `pass`, and the required
runtime gate is `pass`. The legacy gate and manifest field names remain stable
for schema compatibility; the 2026-09-03 owner policy permits source-bound
emulator/simulator evidence. In that state the validator must reopen the external
AAB/IPA, recompute its SHA-256, and verify package/bundle identity, version,
signature, pinned signer, and source revision. Signing and runtime-QA evidence
must both contain that recomputed digest. The artifact directory is supplied at
action time through `NIMBO_RELEASE_ARTIFACT_ROOT`; Android verification also
requires the pinned Bundletool JAR through `NIMBO_BUNDLETOOL_JAR`. Missing bytes,
tools, or an unrecognized state fail closed. A successful build, an editable
JSON/Markdown receipt, or an older artifact cannot establish readiness. Apple
also requires `NimboSourceRevision` in the signed app, widget, and watch
Info.plists, a matching retained archive app plus UUID-matching archive dSYMs,
and the exact App Store Connect `ExportOptions.plist`. Current build 10 has an
exact externally retained distribution archive and IPA that passed trusted
verification. The exact binary has since been installed through TestFlight on
the connected iPhone and iPad, and the iPad widget render is visually
confirmed, but the natural OS-scheduled background completion and its fresh
crash-log window are not yet proved. Historical build 9 remains byte-verifiable but is
runtime-failed by two exact TestFlight background-refresh crash reports.
The protected staged hosted chain is mandatory before every later use. The
single staged directory layout and action-time command are documented in
[`store/README.md`](../store/README.md). The verifier
and its explicit external-build provenance boundary are recorded in
[`growth/quality/release-artifact-byte-verifier-2026-08-30.md`](../growth/quality/release-artifact-byte-verifier-2026-08-30.md).

### Current evidence boundary

- Current product/build source `fc4b6de9` fixes the Swift actor-isolation trap
  reached when Kotlin completes an OS-scheduled background refresh and advances
  Apple to build 10 while retaining vc11/vc1000011. Swift 6 Debug/Release,
  shared iOS, and native surface tests pass locally. Protected run
  `33852229166` signed and candidate-byte-verified the exact set, and run
  `33855931653` durably materialized it. Final manual-only trusted run
  `33859392482` independently verified every current signed byte, so the
  manifest is atomically `3/3 verified-current`. App Store Connect then
  processed build 10 and attached it to internal testers. Bounded iPhone/iPad
  smoke and a visible iPad widget render are recorded; the manifest
  physical-QA field remains null because natural OS-scheduled background
  completion and its post-completion crash-log window remain unproved.
- Historical source `052d12c7` produced the protected-signed, materialized, and
  trusted-byte-verified vc11/vc1000011/build-9 set. Its Android artifacts remain
  available only to Internal testers. Its Apple build 9 is failed after two
  UUID-matched TestFlight background-refresh crashes; none of those bytes or
  observations is exact-current evidence for `fc4b6de9`.
- Historical source `ba824be` passed hosted CI, protected signing, independent
  byte verification, and internal delivery for vc9, vc1000009, and build 7.
  Play-delivered vc9 has a bounded API-25 phone/widget pass. TestFlight build 7
  has a bounded iPhone cold/live/refresh/share-sheet pass, but the copied share
  payload contains `0%%`; those exact bytes are production-ineligible and
  cannot transfer to the successor authority.
- Android phone and Wear bundles compiled from predecessor commit `9c2dce4` and
  embed that full revision, but both exact outputs have zero signature entries.
  The exact debug phone APK passed fresh-install physical API 25 Russian
  onboarding, Tashkent without location, live forecast, truthful late-day Best
  Time, durable first-tip acknowledgement/cold-start suppression, cached offline
  fallback, recovery, and the product-scoped fatal/ANR/TLS filter. A separate
  exact-product, no-snapshot API 24 debug rerun passed clean live weather, tip
  persistence, offline cache, recovery, and the TLS/fatal/ANR filter. Both are
  unsigned/debug regression evidence, not upload-candidate evidence. The
  byte-identical debug APK also passed predecessor API 36 tablet layout,
  Uzbek live forecast, Best Time, durable-tip, home-screen widget render/tap,
  large-text, rotation, and process-health checks on an emulator. It is not a
  physical-tablet result. Exact `2cdd438` now also has an API 37 round-Wear
  debug-emulator pass: EN/RU/UZ render the honestly stale cached Mountain View
  Data Layer item and the restored-English cold loop passes `10/10` with no
  PID-scoped fatal match. No fresh paired-phone refresh occurred; current
  physical tablet and paired Wear OS coverage is absent. The Play-delivered
  phone now passes natural background-network and widget render/update/open,
  but its API-25 legacy launcher icon is the Android template.
- Exact `2cdd438` Apple app/widget Release Simulator bytes embed the full source
  revision. On iPhone 16 Pro Max / iOS 18.1, EN/RU/UZ each passed the real
  Tashkent quick-city and live-provider flow, twelve localized states were
  inspected, and `40/40` cold launches produced no product-scoped fatal match
  or new Nimbo crash report. The exact-current unsigned watchOS build 6 also
  rendered EN/RU/UZ and passed `30/30` cold launches, but it used an explicitly
  stale retained `UserDefaults` snapshot matching the preview-like fixture, not
  a live provider response or fresh phone transfer. Exact build 6 now has a
  verified App Store distribution archive/IPA and completed App Store Connect
  processing as `VALID` and `APP_STORE_ELIGIBLE`, but TestFlight beta-group
  distribution/install remains unverified and there is no iOS 15/16 runtime
  widget render, physical iPhone/iPad/watch result, or fresh paired-watch
  evidence.
- Unit, host, simulator, repository, localization, migration, R8, and unsigned
  release-build checks are useful regression evidence. They are not signing,
  install-over-production, TestFlight/Play delivery, physical-device, review,
  rollout, or end-user-availability proof.
- The current gate decisions remain in
  [`growth/quality/release-artifact-source-sync-2026-09-04-fc4b6de.md`](../growth/quality/release-artifact-source-sync-2026-09-04-fc4b6de.md),
  with the current durable draft locator in
  [`growth/quality/release-materialization-2026-09-04-run-33855931653.md`](../growth/quality/release-materialization-2026-09-04-run-33855931653.md).
  The bounded exact-current iPhone/watchOS Simulator and Wear OS emulator
  evidence is recorded in
  [`growth/quality/apple-wear-current-product-simulator-smoke-2026-08-30-2cdd438.md`](../growth/quality/apple-wear-current-product-simulator-smoke-2026-08-30-2cdd438.md).
  The exact product-commit Android emulator matrix and Apple simulator/test
  boundary are recorded separately in
  [`growth/quality/surface-freshness-2026-08-29.md`](../growth/quality/surface-freshness-2026-08-29.md).
  The predecessor debug tablet/widget emulator boundary is recorded in
  [`growth/quality/android-current-product-tablet-widget-smoke-2026-08-29.md`](../growth/quality/android-current-product-tablet-widget-smoke-2026-08-29.md).
  Earlier iOS 15 compatibility investigation remains in
  [`growth/quality/ios-widget-compatibility-2026-08-29.md`](../growth/quality/ios-widget-compatibility-2026-08-29.md)
  and is not exact-current runtime proof.

### Required current physical matrix

| Surface | Required current checks | Current result |
| --- | --- | --- |
| Android phone | Source-synced upload-signed install/update, cold start, live and cached forecast, denied location/search, share, review policy, large text, TalkBack, background retry, and crash/ANR inspection on the required API range | **Blocked** — current-source vc11 is signed and independently byte-verified by final run `33859392482`, but its manifest physical evidence remains null; post-delivery UZ Vitals and production/public proof are also missing |
| Android tablet and widget | Phone/tablet layouts, widget population/open path, refresh, offline cache, rotation, large text, and TalkBack on the source-synced signed candidate | **Blocked** — current-source vc11 is independently byte-verified, but retained vc11 runtime evidence belongs to the historical atomic source set and cannot fill the current physical-evidence field |
| Wear OS | Play-compatible signed install, cold start, black launch surface, forecast render, phone handoff, and paired-device behavior | **Blocked** — current-source vc1000011 is independently byte-verified, but current-source runtime evidence, paired behavior, and post-delivery UZ Vitals remain missing |
| Apple app and widget | Distribution-signed build 10 on iPhone and iPad, cold/live/cache/search/share/background/widget paths, Dynamic Type, RTL, VoiceOver, and bounded crash inspection | **Blocked** — corrected build 10 is processed and installed through TestFlight on the connected iPhone and iPad; bounded smoke is clean and the iPad widget render is visually confirmed. Remaining matrix paths include cache/search/share, Dynamic Type, RTL, and VoiceOver; critically, the natural OS-scheduled refresh and its fresh crash-log window are unproved. Historical build 9 crashes on that completion and cannot transfer |
| Apple Watch | Build-10 signed companion install, launch, current forecast, localization, and paired handoff | **Blocked** — the build-10 signed companion is independently byte-verified but not installed or exercised; historical build-9 evidence cannot transfer |

## Historical evidence — non-transferable

The rows below are retained as regression and compatibility evidence only. They
cannot be promoted to the exact-current section, even when the marketing version
or Wear version code happens to match.

| Surface | Historical candidate | Evidence retained | Non-transferable boundary |
| --- | --- | --- | --- |
| Android phone/tablet | `1.1.0 (11)` | Independently verified AAB, Play Internal delivery, and bounded runtime QA | Built from superseded source `052d12c7`; it cannot validate the current atomic source set |
| Wear OS | `1.1.0 (1000011)` | Independently verified AAB and Play Internal delivery | Built from superseded source `052d12c7`; it cannot validate the current atomic source set |
| Apple app/widget/watch | `1.1.0 (9)` | Independently verified IPA, TestFlight delivery, and App Review submission | Two exact device reports prove the main app crashes during background-refresh completion; these bytes cannot validate build 10 |
| Android phone/tablet | `1.1.0 (10)` | Independently verified AAB, Play Internal delivery, and bounded physical phone QA | Superseded by source `052d12c7` and cannot validate current vc11 |
| Wear OS | `1.1.0 (1000010)` | Independently verified AAB on the Wear Internal track | Superseded by source `052d12c7`; no physical paired-watch pass exists and it cannot validate vc1000011 |
| Apple app/widget/watch | `1.1.0 (8)` | Independently verified IPA, TestFlight delivery, iPhone QA, and iPad runtime evidence | The iPad Share path crashes in `UIPopoverPresentationController`; these bytes cannot validate build 9 |
| Android phone/tablet | `1.1.0 (9)` | Independently verified AAB, active Internal release, and Play-delivered API-25 branded-launcher/live/share/widget evidence | Source predates the share fix and cannot validate current vc10 |
| Wear OS | `1.1.0 (1000009)` | Independently verified AAB active on the Wear Internal track | Source predates the share fix and there is no physical paired-watch pass; it cannot validate vc1000010 |
| Apple app/widget/watch | `1.1.0 (7)` | Independently verified IPA, internal TestFlight Testing status, and bounded iPhone cold/live/refresh/share-sheet evidence | The copied share payload contains `0%%`; build 7 is production-ineligible and cannot validate build 8 |
| Android phone/tablet | `1.1.0 (8)` | Independently verified Play-delivered package plus API-25 functional, accessibility, offline, background, and widget evidence | The launcher icon is the Android template; these bytes cannot validate replacement vc9 |
| Wear OS | `1.1.0 (1000008)` | Independently verified AAB accepted on the active Internal track | The artifact embeds the predecessor revision and has no physical paired-watch pass; it cannot validate vc1000009 |
| Apple app/widget/watch | `1.1.0 (6)` | Independently verified IPA delivered through Transporter and processed as `VALID` / `APP_STORE_ELIGIBLE` | The artifact embeds the predecessor revision and has no TestFlight physical pass; it cannot validate build 7 |
| Android phone/tablet | `1.1.0 (7)` | Upload-signed artifact and a broad physical API 25 matrix covering onboarding, search, live/cached forecast, share, large text, TalkBack, recovery, and review-prompt behavior | Version code and source predate current phone `1.1.0 (9)`; this historical artifact closes neither the current manifest nor the physical gate |
| Wear OS | `1.1.0 (1000008)` at revision `4d9492a` | Signed AAB and emulator build/policy evidence | Embedded revision is not the exact product commit and there is no physical paired-watch pass |
| Apple app/widget/watch | `1.1.0 (5)` | Distribution-signed archive/IPA and matching dSYMs | Build 5 predates current build 7; its iPad launch was not completed and it cannot satisfy current Apple QA |
| Apple public release | `1.0.1 (4)` | Bounded physical iPad app/cache/widget-process evidence and the public App Store build | Older public bytes cannot diagnose the suppressed production crash or validate build 7 |
| Google Play public release | Phone `1.0.2 (6)`; Wear `1.0.2 (1000007)` | Public production availability and historical Play delivery evidence | Public availability does not validate the unpublished `1.1.0` source or its listing/release changes |

## Operating rule

Run the validator whenever release identity, artifact state, device evidence, or
gate status changes:

```sh
python3 scripts/check_release_qa_matrix.py
```

After a real gate changes, update the authoritative JSON first and then update
this document to the exact block expected by the validator. Store console state
and public availability must still be recorded from direct dated evidence; this
matrix cannot infer either one.
