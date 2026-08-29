# Release QA matrix

Status date: August 29, 2026.

This document separates the exact `1.1.0` release candidate from historical
store and device evidence. The current block below is checked against
[`store/upload-manifest-1.1.0.json`](../store/upload-manifest-1.1.0.json),
[`growth/quality/gates.json`](../growth/quality/gates.json), and the platform
build files by `python3 scripts/check_release_qa_matrix.py`. A historical pass
must never satisfy a current artifact, signing, physical-device, store-review,
or public-availability gate.

## Exact-current 1.1.0 candidate

<!-- release-qa-current:start -->
| Surface | Exact candidate | Manifest source sync | Release/source gate | Required physical QA | Fail-closed status |
| --- | --- | --- | --- | --- | --- |
| Android phone/tablet | `1.1.0 (8)` | `blocked` | `release_artifact_source_sync: blocked` | `android_physical_smoke: blocked` | **BLOCKED** |
| Wear OS | `1.1.0 (1000008)` | `blocked` | `release_artifact_source_sync: blocked` | `android_physical_smoke: blocked` | **BLOCKED** |
| Apple app/widget/watch | `1.1.0 (6)` | `blocked` | `release_artifact_source_sync: blocked` | `ios_physical_smoke: blocked` | **BLOCKED** |
<!-- release-qa-current:end -->

`READY` is permitted only when the corresponding artifact is
`verified-current`, the shared release/source gate is `pass`, and the required
physical gate is `pass`. The manifest must also contain a 64-hex SHA-256 and
existing repository evidence files for signing and physical QA. The validator
treats a missing or unrecognized state as a failure; it does not infer readiness
from a successful build or an older artifact.

### Current evidence boundary

- Android phone and Wear bundles compile from the exact product commit, but the
  current outputs are not upload-signed. The exact-current phone debug bytes
  have bounded physical API 25/API 36 evidence; current signed-release tablet,
  widget, and paired Wear OS coverage is absent.
- Apple app, widget, and watch compile for the simulator and have matching dSYM
  evidence. Build 6 has no distribution-signed archive or IPA and no physical
  iPhone, iPad, widget, or paired-watch result.
- Unit, host, simulator, repository, localization, migration, R8, and unsigned
  release-build checks are useful regression evidence. They are not signing,
  install-over-production, TestFlight/Play delivery, physical-device, review,
  rollout, or end-user-availability proof.
- The current gate decisions and exact hashes remain in
  [`growth/quality/release-artifact-source-sync-2026-08-29.md`](../growth/quality/release-artifact-source-sync-2026-08-29.md).

### Required current physical matrix

| Surface | Required current checks | Current result |
| --- | --- | --- |
| Android phone | Source-synced upload-signed install/update, cold start, live and cached forecast, denied location/search, share, review policy, large text, TalkBack, background retry, and crash/ANR inspection on the required API range | **Blocked** — only bounded exact-current debug evidence exists |
| Android tablet and widget | Phone/tablet layouts, widget population/open path, refresh, offline cache, rotation, large text, and TalkBack on the source-synced signed candidate | **Blocked** — no exact-current signed physical result |
| Wear OS | Play-compatible signed install, cold start, black launch surface, forecast render, phone handoff, and paired-device behavior | **Blocked** — no exact-current signed physical-watch result |
| Apple app and widget | Distribution-signed build 6 on iPhone and iPad, cold/live/cache/search/share/background/widget paths, Dynamic Type, RTL, VoiceOver, and bounded crash inspection | **Blocked** — simulator-only current evidence |
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
