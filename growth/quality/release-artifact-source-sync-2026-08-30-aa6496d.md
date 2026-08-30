# Release artifact source sync — 2026-08-30 signing correction

Status: **HISTORICAL PREDECESSOR CHECKPOINT; it recorded 0/3 byte-verified
artifacts and has been superseded by `5b98f23`**.

The product/build-input commit at this checkpoint was
`aa6496d0ac9011ff818d2c0dd2ec5c565317400c`. It resolves to Android phone
`1.1.0 (8)`, Wear OS `1.1.0 (1000008)`, and Apple app/widget/watch
`1.1.0 (6)`.

## Change boundary

The revision preserves the previously verified `NimboSourceRevision` build
plumbing and corrects Apple release signing configuration. Release builds now
select one explicit App Store provisioning profile per bundle:

- `uz.ganikhodjaev.weather` uses
  `iOS Team Store Provisioning Profile: uz.ganikhodjaev.weather`;
- `uz.ganikhodjaev.weather.widget` uses
  `iOS Team Store Provisioning Profile: uz.ganikhodjaev.weather.widget`;
- `uz.ganikhodjaev.weather.watchkitapp` uses
  `iOS Team Store Provisioning Profile: uz.ganikhodjaev.weather.watchkitapp`.

`iosApp/ExportOptions.plist` repeats that exact mapping, selects manual App
Store Connect export, team `5SWEZ7HTYP`, and the Apple Distribution identity.
Read-only `xcodebuild -showBuildSettings` output confirmed that each Release
target resolves its own bundle identifier, manual signing style, distribution
identity, and bundle-compatible profile. The earlier command-line override
`Nimbo App Store 1.0` was removed because a single global profile was inherited
by the widget and watch targets and could not authorize their bundle IDs or
entitlements.

This configuration proof is not a private-key operation, archive, IPA,
signature, physical-device result, upload, review, publication, or public
availability result.

## Current artifact authority

| Surface | Exact identity | Current signed bytes | Decision |
| --- | --- | --- | --- |
| Android phone/tablet | `1.1.0 (8)` | none bound to this revision | **BLOCKED** |
| Wear OS | `1.1.0 (1000008)` | none bound to this revision | **BLOCKED** |
| Apple app/widget/watch | `1.1.0 (6)` | no distribution-signed archive or IPA bound to this revision | **BLOCKED** |

The schema-v2 upload manifest deliberately keeps every current SHA-256,
signing-evidence path, and physical-QA path null. Historical candidates and
all device results from predecessor revisions remain non-transferable.

## Remaining unblock

1. Authorize the existing login Keychain without resetting or replacing the
   accepted Android upload key or Apple identities.
2. Build, sign, and verify all three artifacts from an exact clean checkout of
   this revision in the protected release path.
3. Retain the artifacts, archive/dSYMs/export options, hashes, signer and
   provisioning checks, and workflow provenance.
4. Run the exact signed physical phone/tablet/widget/watch matrix and bind its
   evidence to the recomputed artifact SHA-256 values.
5. Promote a manifest entry to `verified-current` only when the byte verifier
   accepts those retained bytes and the matching physical gate passes.

No artifact was signed, uploaded, submitted, or published by this source-sync
update.
