# Release QA matrix

Status date: August 31, 2026.

<!-- release-authority-current:start -->
<!-- source_revision:ba824beae5e72653e42af2b8b78286f61415e3ab -->
<!-- artifact:android_phone;source_sync=blocked;byte_verified=false;physical_qa_evidence=none -->
<!-- artifact:wear_os;source_sync=blocked;byte_verified=false;physical_qa_evidence=none -->
<!-- artifact:apple;source_sync=blocked;byte_verified=false;physical_qa_evidence=none -->
<!-- physical_gate:android_physical_smoke=blocked;reason_sha256=d3d6c5d64cc259d3fabff9c9cdb2df8678f54f946e027adadbc6f258adc29b27 -->
<!-- physical_gate:ios_physical_smoke=blocked;reason_sha256=770422408d39ff77e1915f418b62ed90b7f609b687a0a0474a0012bdd25237f7 -->
<!-- release-authority-current:end -->

The machine-validated block is fail-closed for replacement source
`ba824beae5e72653e42af2b8b78286f61415e3ab`: all three artifacts are blocked
and `byte_verified=false` until protected signing and independent verification
produce a complete current set. The former vc8/vc1000008/build-6 bytes and their
store/device observations remain historical evidence only.

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
| Surface | Exact candidate | Manifest source sync | Manifest entry reverified/current | Release/source gate | Required physical QA | Fail-closed status |
| --- | --- | --- | --- | --- | --- | --- |
| Android phone/tablet | `1.1.0 (9)` | `blocked` | `false` | `release_artifact_source_sync: blocked` | `android_physical_smoke: blocked` | **BLOCKED** |
| Wear OS | `1.1.0 (1000009)` | `blocked` | `false` | `release_artifact_source_sync: blocked` | `android_physical_smoke: blocked` | **BLOCKED** |
| Apple app/widget/watch | `1.1.0 (7)` | `blocked` | `false` | `release_artifact_source_sync: blocked` | `ios_physical_smoke: blocked` | **BLOCKED** |
<!-- release-qa-current:end -->

`READY` is permitted only when the corresponding artifact is
`verified-current`, the shared release/source gate is `pass`, and the required
physical gate is `pass`. In that state the validator must reopen the external
AAB/IPA, recompute its SHA-256, and verify package/bundle identity, version,
signature, pinned signer, and source revision. Signing and physical-QA evidence
must both contain that recomputed digest. The artifact directory is supplied at
action time through `NIMBO_RELEASE_ARTIFACT_ROOT`; Android verification also
requires the pinned Bundletool JAR through `NIMBO_BUNDLETOOL_JAR`. Missing bytes,
tools, or an unrecognized state fail closed. A successful build, an editable
JSON/Markdown receipt, or an older artifact cannot establish readiness. Apple
also requires `NimboSourceRevision` in the signed app, widget, and watch
Info.plists, a matching retained archive app plus UUID-matching archive dSYMs,
and the exact App Store Connect `ExportOptions.plist`; build 6 now has a
retained, `verified-current` distribution archive and IPA. A fresh local macOS
run reopened the exact materialized assets and completed the atomic promotion.
The protected staged hosted chain is mandatory for every current master. The
single staged directory layout and action-time command are documented in
[`store/README.md`](../store/README.md). The verifier
and its explicit external-build provenance boundary are recorded in
[`growth/quality/release-artifact-byte-verifier-2026-08-30.md`](../growth/quality/release-artifact-byte-verifier-2026-08-30.md).

### Current evidence boundary

- Current product/build source `2cdd438` passed ordinary hosted CI
  [run #117](https://github.com/4810092/Weather/actions/runs/33300967788),
  including the complete API 24/API 36 Compose matrix and Apple surface tests.
  Protected [run `33381050098`](https://github.com/4810092/Weather/actions/runs/33381050098)
  then consumed all 8/8 signing inputs and produced retained, independently
  byte-verified phone AAB, Wear AAB, IPA, xcarchive, dSYMs, mapping, and exact
  ExportOptions. The schema-v3 receipt and hashes are recorded in
  [`signed-candidate-run-33381050098.md`](../growth/quality/signed-candidate-run-33381050098.md).
  Hosted materialization
  [run `33392732428`](https://github.com/4810092/Weather/actions/runs/33392732428)
  then validated the exact source artifact/package/receipt bindings and stored
  the package and receipt as hash-bound assets in unpublished draft release
  `379745439`. A fresh local macOS run then downloaded those exact assets,
  safely extracted the closed tree, verified pinned Bundletool 1.18.3, and
  returned `byte_verified=true` for all three outputs. The manifest is now
  atomically `3/3 verified-current` and remains `draft-blocked`; the mutable
  draft must pass staged hosted revalidation before later use. Hosted
  signing/materialization is not physical accessibility, Play/TestFlight
  delivery, or crash-gate closure. A
  clean isolated exact-source debug
  APK and its pulled installed bytes share SHA-256
  `d66c8f0f9b05232cf484bd95223328a44f2a0bddf1d2f76817ef9504f87fe047`
  and passed a bounded physical General Mobile API 25 run: denied location,
  ordinary Bukhara search, live forecast, cached offline fallback and explicit
  retry, recovery, populated home widget render/tap, process health, and
  cleanup. This exact-current physical result uses the debug certificate and
  is not upload signing, Play delivery, physical-tablet, or Wear proof; the
  gate stays blocked. Predecessor artifact/device evidence remains
  non-transferable. See the
  [physical record](../growth/quality/android-current-product-physical-smoke-2026-08-30-2cdd438.md).
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
  [`growth/quality/release-artifact-source-sync-2026-08-31-2cdd438.md`](../growth/quality/release-artifact-source-sync-2026-08-31-2cdd438.md),
  with the current blocked manifest source-sync locator in
  [`growth/quality/release-materialization-2026-08-31-run-33392732428.md`](../growth/quality/release-materialization-2026-08-31-run-33392732428.md).
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
| Android phone | Source-synced upload-signed install/update, cold start, live and cached forecast, denied location/search, share, review policy, large text, TalkBack, background retry, and crash/ANR inspection on the required API range | **Blocked** — replacement vc9 removes the legacy template assets and renders the Nimbo mark on an API-24 emulator, but no upload-signed, independently verified, or Play-delivered vc9 exists. The broad Play-delivered vc8 phone evidence is historical and cannot transfer |
| Android tablet and widget | Phone/tablet layouts, widget population/open path, refresh, offline cache, rotation, large text, and TalkBack on the source-synced signed candidate | **Blocked** — the historical Play-delivered vc8 widget pass and predecessor emulator coverage do not satisfy replacement vc9; no current signed physical-tablet result exists |
| Wear OS | Play-compatible signed install, cold start, black launch surface, forecast render, phone handoff, and paired-device behavior | **Blocked** — replacement vc1000009 is unsigned and absent from Play; historical vc1000008 remains on Internal without a physical paired-watch pass |
| Apple app and widget | Distribution-signed build 7 on iPhone and iPad, cold/live/cache/search/share/background/widget paths, Dynamic Type, RTL, VoiceOver, and bounded crash inspection | **Blocked** — replacement build 7 is unsigned and absent from TestFlight. Historical build 6 is `VALID` / `APP_STORE_ELIGIBLE` but has no TestFlight physical pass and cannot transfer |
| Apple Watch | Build-7 signed companion install, launch, current forecast, localization, and paired handoff | **Blocked** — replacement build 7 has no signed companion or physical-watch result |

## Historical evidence — non-transferable

The rows below are retained as regression and compatibility evidence only. They
cannot be promoted to the exact-current section, even when the marketing version
or Wear version code happens to match.

| Surface | Historical candidate | Evidence retained | Non-transferable boundary |
| --- | --- | --- | --- |
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
