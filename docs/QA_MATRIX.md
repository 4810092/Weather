# Release QA matrix

Status date: August 30, 2026.

<!-- release-authority-current:start -->
<!-- source_revision:65b2eb939466c493557a3ddac580e913cd0f58f3 -->
<!-- artifact:android_phone;source_sync=blocked;byte_verified=false;physical_qa_evidence=none -->
<!-- artifact:wear_os;source_sync=blocked;byte_verified=false;physical_qa_evidence=none -->
<!-- artifact:apple;source_sync=blocked;byte_verified=false;physical_qa_evidence=none -->
<!-- physical_gate:android_physical_smoke=blocked;reason_sha256=e0f53d4d50e08daa4c2ea7633d2d3d38a2af2508521d8aae8ce2c05356fd1c5b -->
<!-- physical_gate:ios_physical_smoke=blocked;reason_sha256=0f0f4b4d58e0dec7cd1000377839f4b0c0b67e783f42bcdc2ac6b94904f1876c -->
<!-- release-authority-current:end -->

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
| Surface | Exact candidate | Manifest source sync | Real bytes verified | Release/source gate | Required physical QA | Fail-closed status |
| --- | --- | --- | --- | --- | --- | --- |
| Android phone/tablet | `1.1.0 (8)` | `blocked` | `false` | `release_artifact_source_sync: blocked` | `android_physical_smoke: blocked` | **BLOCKED** |
| Wear OS | `1.1.0 (1000008)` | `blocked` | `false` | `release_artifact_source_sync: blocked` | `android_physical_smoke: blocked` | **BLOCKED** |
| Apple app/widget/watch | `1.1.0 (6)` | `blocked` | `false` | `release_artifact_source_sync: blocked` | `ios_physical_smoke: blocked` | **BLOCKED** |
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
and the exact App Store Connect `ExportOptions.plist`; build 6 has the source
setting but no distribution-signed candidate carrying a verified value and
therefore remains blocked. The single staged directory layout and action-time
command are documented in [`store/README.md`](../store/README.md). The verifier
and its explicit external-build provenance boundary are recorded in
[`growth/quality/release-artifact-byte-verifier-2026-08-30.md`](../growth/quality/release-artifact-byte-verifier-2026-08-30.md).

### Current evidence boundary

- Current product/build source `65b2eb9` has no retained signed Android or
  Apple candidate and no matching physical QA. It keeps the Apple source-
  revision and deterministic per-target profile settings, pins 1,715
  hosted-Linux Android and macOS/`iosArm64` dependency artifacts including the
  Linux AAPT2 runner, and seals actual source bytes in the hosted candidate
  workflow. Exact empty-cache Android and Apple regression builds pass; all
  device evidence below belongs to predecessor revisions.
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
  physical-tablet result. API 37 round-Wear Empty/Fresh/Stale checks remain
  prior regression evidence for `ee7c36f`; current upload-signed physical
  tablet/widget and paired Wear OS coverage is absent.
- Apple app, widget, and watch compiled from predecessor commit `9c2dce4` for the
  simulator and have matching hash/UUID/dSYM evidence. The app and widget emit
  iOS 15 minimum load commands, the watch emits watchOS 10, and 18 deterministic
  surface tests pass. The prior build-6 device archive attempt failed at the
  Widget CodeSign step and produced no archive or IPA; protected signing was not
  retried for `9c2dce4`. Twelve EN/RU/UZ iPhone phone sources come from
  the source-bound `9c2dce4` build-6 simulator app and cover four real states
  per locale, but prove screenshot provenance only. The attempted Apple offline
  transition was not captured and is not claimed. Apple Watch sources remain
  historical build-5 simulator evidence. Build 6 still has no
  distribution-signed archive, no iOS 15/16
  runtime widget render, and no physical iPhone, iPad, widget, or paired-watch
  result.
- Unit, host, simulator, repository, localization, migration, R8, and unsigned
  release-build checks are useful regression evidence. They are not signing,
  install-over-production, TestFlight/Play delivery, physical-device, review,
  rollout, or end-user-availability proof.
- The current gate decisions remain in
  [`growth/quality/release-artifact-source-sync-2026-08-30-65b2eb9.md`](../growth/quality/release-artifact-source-sync-2026-08-30-65b2eb9.md).
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
| Android phone | Source-synced upload-signed install/update, cold start, live and cached forecast, denied location/search, share, review policy, large text, TalkBack, background retry, and crash/ANR inspection on the required API range | **Blocked** — exact-product API 24 emulator and physical API 25 debug evidence exists, but current signed physical phone coverage does not |
| Android tablet and widget | Phone/tablet layouts, widget population/open path, refresh, offline cache, rotation, large text, and TalkBack on the source-synced signed candidate | **Blocked** — predecessor API 36 debug emulator layout/widget/large-text/rotation smoke passes; no current signed physical tablet/widget result |
| Wear OS | Play-compatible signed install, cold start, black launch surface, forecast render, phone handoff, and paired-device behavior | **Blocked** — API 37 round emulator render passes; no exact-current signed physical-watch or paired handoff result |
| Apple app and widget | Distribution-signed build 6 on iPhone and iPad, cold/live/cache/search/share/background/widget paths, Dynamic Type, RTL, VoiceOver, and bounded crash inspection | **Blocked** — exact-source simulator builds and 18 surface tests pass, but older-runtime rendering, signing, and physical evidence are absent |
| Apple Watch | Build-6 signed companion install, launch, current forecast, localization, and paired handoff | **Blocked** — no current physical-watch result |

## Historical evidence — non-transferable

The rows below are retained as regression and compatibility evidence only. They
cannot be promoted to the exact-current section, even when the marketing version
or Wear version code happens to match.

| Surface | Historical candidate | Evidence retained | Non-transferable boundary |
| --- | --- | --- | --- |
| Android phone/tablet | `1.1.0 (7)` | Upload-signed artifact and a broad physical API 25 matrix covering onboarding, search, live/cached forecast, share, large text, TalkBack, recovery, and review-prompt behavior | Version code and source predate current phone `1.1.0 (8)`; no current artifact or gate is closed |
| Wear OS | `1.1.0 (1000008)` at revision `4d9492a` | Signed AAB and emulator build/policy evidence | Embedded revision is not the exact product commit and there is no physical paired-watch pass |
| Apple app/widget/watch | `1.1.0 (5)` | Distribution-signed archive/IPA and matching dSYMs | Build 5 predates current build 6; its iPad launch was not completed and it cannot satisfy current Apple QA |
| Apple public release | `1.0.1 (4)` | Bounded physical iPad app/cache/widget-process evidence and the public App Store build | Older public bytes cannot diagnose the suppressed production crash or validate build 6 |
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
