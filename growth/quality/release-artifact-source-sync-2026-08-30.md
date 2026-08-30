# Release artifact source sync — 2026-08-30

Status: **HISTORICAL PREDECESSOR CHECKPOINT; it recorded 0/3 byte-verified
artifacts and has been superseded by `5b98f23`**.

The product/build-input commit at this checkpoint was
`44c189209c793cf097fcc293faf8db88033e6902`. It resolves to Android phone
`1.1.0 (8)`, Wear OS `1.1.0 (1000008)`, and Apple app/widget/watch
`1.1.0 (6)`.

## Change boundary

This commit adds the `NimboSourceRevision` build setting to the Apple app,
widget, simulator app, and watch app. Release invocations must override the
checked-in `UNVERIFIED_SOURCE` sentinel with the full revision returned by the
release verifier. A one-time unsigned Release simulator smoke confirmed that
all produced Apple Info.plists receive the supplied full 40-character value.
That smoke is build-plumbing evidence only; it is not signing, archive, IPA,
physical-device, upload, review, publication, or availability evidence.

The prior Android bundles, debug APK/device results, Apple simulator binaries,
screenshots, archive, IPA, and physical results were produced from earlier
revisions. They remain useful historical regression evidence but cannot satisfy
the exact-current artifact or physical-QA gates for this commit.

## Current artifact authority

| Surface | Exact identity | Current signed bytes | Decision |
| --- | --- | --- | --- |
| Android phone/tablet | `1.1.0 (8)` | none bound to this revision | **BLOCKED** |
| Wear OS | `1.1.0 (1000008)` | none bound to this revision | **BLOCKED** |
| Apple app/widget/watch | `1.1.0 (6)` | no distribution-signed archive or IPA bound to this revision | **BLOCKED** |

The schema-v2 upload manifest intentionally keeps every current SHA-256,
signing-evidence path, and physical-QA path null. Historical candidates remain
separately identified and cannot be promoted as current evidence.

## Unblock requirements

1. Build, sign, and verify all three current artifacts from the exact clean
   revision in one protected GitHub-hosted release workflow.
2. Retain the immutable artifacts, matching archive/dSYMs/export options,
   hashes, signer/provisioning checks, and workflow provenance.
3. Run the source-synced signed physical phone/tablet/widget/watch matrix and
   bind each evidence record to the recomputed artifact SHA-256.
4. Promote a manifest entry to `verified-current` only when the byte verifier
   accepts the same retained bytes and all publication gates pass.

No artifact was signed, uploaded, submitted, or published by this source-sync
update.
