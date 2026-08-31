# Signed candidate run 33381050098 — 2026-08-31

Status: **PASS for protected hosted signing and pre-manifest byte verification;
BLOCKED for manifest promotion, physical QA, store upload, and publication**.

The candidate is built from product/build-input authority
`2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652`: Android phone `1.1.0 (8)`,
Wear OS `1.1.0 (1000008)`, and Apple app/widget/watch `1.1.0 (6)`.

## Hosted provenance

GitHub Actions [run `33381050098`](https://github.com/4810092/Weather/actions/runs/33381050098),
attempt 1, was manually dispatched from `refs/heads/master` at evidence head
`dd6e275e840947ec6b22b9485ebeb63d5eaa320c`. It completed successfully from
`2026-08-31T10:08:41Z` through `2026-08-31T10:29:33Z`:

| Job | Job ID | Result | Runtime |
| --- | ---: | --- | ---: |
| `build-unsigned` | `99453261651` | success | 19m08s |
| `sign-verify` | `99457861700` | success | 1m33s |

The run verified the exact source seal, built the Android phone and Wear
bundles plus Apple archive, consumed all 8/8 protected signing inputs, checked
the Android upload and Apple distribution identities, exported the Apple
candidate with exact ExportOptions, applied the bounded App Group correction,
re-signed nested Apple products before the parent app, destroyed staged signing
material, byte-verified the closed candidate tree, and uploaded only the
receipt-bound result. Every workflow step and both jobs passed.

The receipt pins these verifier inputs:

| Input | SHA-256 |
| --- | --- |
| `.github/workflows/signed-candidate.yml` | `fd96eb999047cc033beb211eb09761dbbe68ec341dc9f3cf5902adfadfdebc55` |
| `scripts/verify_signed_candidate.py` | `b72c99e5cf5b0fb85e79fdee874cddd26838472dab8eb4669461a567729d45f8` |
| `scripts/release_artifact_verifier.py` | `96dadb1691ea5c73da5e127df2dd250148d8338c2df4c588660759b7c50ebf82` |
| Bundletool 1.18.3 | `a099cfa1543f55593bc2ed16a70a7c67fe54b1747bb7301f37fdfd6d91028e29` |

## Immutable artifact identities

GitHub artifact `9754332100`,
`nimbo-signed-candidate-2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652`,
contains exactly the signed-candidate package and schema-v3 receipt. The
GitHub-created ZIP is 57,807,485 bytes with SHA-256
`f1754ff767d908cd6be5ce5652e05e6f3dc8721ffa1b0db303d72a5d27cf5478`.
The downloaded ZIP matched that API-reported digest and passed archive
integrity checks before extraction.

| Retained item | Bytes | SHA-256 |
| --- | ---: | --- |
| `signed-candidate-bytes.tar.gz` | 58,073,521 | `60c827ef9f5d2cdc51add5344bd33ab780ab1be3154a3f3da8c22074ddb518d9` |
| `signed-candidate-receipt.json` | 11,711 | `c852c61e07289d2a7a8f211efc91d7f30fab2c3475465ba000625780a21de19c` |

The committed receipt is
[`receipts/signed-candidate-33381050098.json`](receipts/signed-candidate-33381050098.json).
Its closed tree has 104 regular files, 88 directories, six expected top-level
entries, 152,161,477 payload bytes, and tree SHA-256
`c91ea40ae12fd59aacfee77f03ba75240951b5797c16b23487ce334eb85502fa`.
Archive paths were checked before extraction; there were no absolute or parent
paths, symbolic links, hard links, or special entries.

| Surface | Exact file | Signed artifact SHA-256 | Verification |
| --- | --- | --- | --- |
| Android phone | `nimbo-phone-1.1.0-vc8.aab` | `d4a90676f32745ea314b50ced2c9955e86923589534a1a7654ac6f1207e88a62` | upload certificate, package/version/SDK, embedded source revision, Bundletool, and embedded mapping passed |
| Wear OS | `nimbo-wear-1.1.0-vc1000008.aab` | `e76d685b20e86f8878be7c9a1a59ac6edb5781ec8e61d5ecd36feb52ddc1cccf` | upload certificate, package/version/SDK, Wear manifest, embedded source revision, and Bundletool passed |
| Apple | `Nimbo.ipa` | `7466afb1a06f3000ad5d095734082d57cf58e992bdd7a8bed326e90d26ba39d0` | distribution identity, exact app/widget/watch topology, profiles, entitlements, archive/export parity, Mach-O/dSYM UUIDs, and deep code-sign verification passed |

The phone mapping SHA-256 is
`878b1050fb71afebdfea037845c85cef60536d475de70dff281cd44478184055`.
The Android upload-certificate SHA-256 is
`431548a4871c9c090eee808ac3a34898f5d78602d9e747dfe81e228415aac252`;
the Apple distribution-certificate SHA-256 is
`fd4d8668a7e0f4eb9f64a12b5f0ddec0075ccde31dad50a96e978926e0e743f1`.

The Apple app, widget, and watch profiles embedded in both the IPA and retained
xcarchive matched the protected UUID, name, bundle ID, and raw-profile SHA-256
bindings recorded in the receipt. The archive tree SHA-256 is
`a10aa4d6bef5fe6a5d2c8dd8aadc97342f90fa4c1da62d49edf27941c8b34a7f`.

## Independent retention verification

The exact GitHub ZIP was downloaded once and then retained outside the Git
repository under the private, mode-restricted release namespace
`candidates/1.1.0-2cdd438-run-33381050098/`. That copy contains the original
ZIP, hosted package and receipt, GitHub run/job/artifact metadata, pinned
Bundletool JAR, extracted candidate bytes, an independent receipt/package, and
a checksum manifest over all retained files. The retained set contains 114
files and occupies 359,030,784 bytes; its complete checksum verification
passed after the final move.

On the same evidence-head checkout, the committed verifier was run again over
the extracted bytes with Bundletool 1.18.3 and the receipt's protected Apple
profile bindings. It returned success for all three artifacts. The independent
candidate tree and every artifact identity/hash equal the hosted receipt.
After removing only the derived package filename and gzip SHA fields, the
hosted and independent receipts are byte-for-byte identical when canonically
rendered. The newly generated tar.gz has a different wrapper hash because the
packager does not normalize gzip/tar metadata; it is retained separately and
is not substituted for the exact hosted package.

## Fail-closed boundary

The receipt state is
`candidate-bytes-verified-not-manifest-promoted`. This proves a retained,
source-current, upload-signed candidate set, but it does **not** by itself make
the committed upload manifest `verified-current`. The public CI path requires
the real external bytes for that state, while the retained bytes are private
and the GitHub artifact expires. Therefore the schema-v2 upload manifest stays
`draft-blocked`, its three `source_sync` fields stay `blocked`, and its current
SHA/signing/physical fields stay null until a durable hosted materialization
path can fail-closed re-run the full macOS byte verifier.

No phone, tablet, iPhone, iPad, widget, or watch physical result is claimed by
this record. No artifact was uploaded to App Store Connect or Google Play,
associated with a TestFlight/internal/production track, submitted for review,
released, or made publicly available. The iOS crash gate and both physical QA
gates remain blocked.
