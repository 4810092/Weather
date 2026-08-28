# Release artifact source sync — 2026-08-29

Status: **BLOCKED for Android phone and Apple; VERIFIED-CURRENT for Wear OS**.
No artifact was signed, uploaded, submitted, or published by this correction.

## Decision

The signed Android phone `1.1.0 (7)` AAB and Apple `1.1.0 (5)` IPA were built
before the current review-prompt and background-refresh hardening. Their hashes,
signature evidence, and bounded device results remain valid only for those
historical bytes. They cannot be reused as evidence for the current source.

The current source identities are therefore Android phone `1.1.0 (8)` and
Apple app/widget/watch `1.1.0 (6)`. The Wear OS source is unchanged and remains
`1.1.0 (1000008)`. `iosApp/project.yml` is the Apple version source; the
committed Xcode project was regenerated from it with XcodeGen 2.45.3.

| Surface | Current source identity | Source sync | Current SHA-256 | Current signing evidence | Current physical QA |
| --- | --- | --- | --- | --- | --- |
| Android phone/tablet | `1.1.0 (8)` | **BLOCKED** | `null` | `null` | `null` |
| Wear OS | `1.1.0 (1000008)` | **VERIFIED-CURRENT** | `ac19a0eab1a60554db309166f135e754c97205b79c4f5182164a8b21594e7dc6` | retained signed AAB evidence | no physical-watch pass |
| Apple app/widget/watch | `1.1.0 (6)` | **BLOCKED** | `null` | `null` | `null` |

The current phone and Apple rows stay blocked until new artifacts are built
from the current source, signed with the accepted identities, hashed, and
tested on the required physical devices. Signing material was not available to
the non-interactive build session, so no placeholder hash or inherited QA claim
is recorded.

## Local source-identity checks

- `:app:bundleRelease` and `:wearApp:bundleRelease` completed. Bundletool reads
  version codes `8` and `1000008` from the resulting local bundles. Jarsigner
  reports those Gradle outputs as unsigned, so they are not substituted for the
  manifest's required upload-signed artifacts and no current SHA is promoted.
- Xcode build settings report marketing version `1.1.0` and build `6`. An
  arm64-only Release simulator build completed without signing; the app and
  widget Info.plists both expand to build `6`. This proves source/project
  consistency only, not an archive, distribution signature, or device pass.

## Preserved historical candidates

| Surface | Historical identity | SHA-256 | Evidence boundary |
| --- | --- | --- | --- |
| Android phone/tablet | `1.1.0 (7)` | `e476a124c33854873add9061140f68f1720ff098202b52e7758038bb50f5a77c` | Signed artifact and API 25 physical results remain scoped to vc7 only. |
| Apple app/widget/watch | `1.1.0 (5)` | `b36f8fddb225cd616e3833de6037b6434486ec3cbb9ed06f5cc8deb0627ed4dc` | Distribution signature/archive evidence and the bounded iPad install remain scoped to build 5 only. |

The original evidence is retained without alteration:

- `growth/quality/android-release-artifacts-2026-08-28.md`
- `growth/quality/android-physical-smoke-2026-08-28.md`
- `growth/quality/apple-release-artifacts-2026-08-28.md`
- `growth/quality/apple-runtime-smoke-2026-08-28.md`

## Unblock requirements

1. Build and upload-sign `nimbo-phone-1.1.0-vc8.aab` from the current source;
   verify package, version, certificate, Bundletool output, and SHA-256.
2. Archive and distribution-sign Apple `1.1.0 (6)` from the current source;
   verify the app, widget, watch, dSYM, provisioning, and exported IPA identity.
3. Run the source-synced phone and Apple physical matrices. Historical vc7/build5
   device results may inform coverage but cannot satisfy the new artifact gates.
4. Replace `null` values in `store/upload-manifest-1.1.0.json` only after the
   corresponding evidence files exist and the validator accepts the exact
   source identity.

This is a local release-integrity record, not proof of store processing or
public availability.
