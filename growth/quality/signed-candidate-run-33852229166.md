# Signed candidate run 33852229166 — 2026-09-04

Status: **PASS for protected hosted signing and candidate-byte verification;
BLOCKED for durable materialization, manifest promotion, TestFlight runtime QA,
App Review replacement, rollout, and publication**.

The exact product/build-input authority is
`fc4b6de9e28fd8956eb64462294b8bcdf405ce7e`: Android phone `1.1.0 (11)`,
Wear OS `1.1.0 (1000011)`, and corrected Apple app/widget/watch
`1.1.0 (10)`. The Apple source contains the Swift 6 background-refresh
actor-isolation correction.

## Pre-signing authority

Local canonical verification passed before dispatch: `scripts/local-ci.sh
apple`, the complete 367-test growth suite, the 943-path repository check,
release/QA and artifact contracts, store metadata/previews, dashboard parity,
featuring/ASO checks, and `git diff --check`. Commits `fc4b6de`, `5e5712c`, and
`9b785e1` were pushed to `origin/master` before the protected run.

## Hosted provenance

GitHub Actions
[run `33852229166`](https://github.com/4810092/Weather/actions/runs/33852229166),
attempt 1, was manually dispatched from `refs/heads/master` at evidence head
`9b785e19b52f09e3eca37cf0c00ef961a03bd73b`. It completed successfully from
`2026-09-04T08:11:20Z` through `2026-09-04T08:29:45Z`.

| Job | Job ID | Result | Window |
| --- | ---: | --- | --- |
| `build-unsigned` | `100957396528` | success | `08:11:24Z`–`08:28:16Z` |
| `sign-verify` | `100961673555` | success | `08:28:22Z`–`08:29:44Z` |

The signing material was destroyed before complete candidate-byte verification.
The receipt pins the unchanged signed workflow SHA-256
`877ffa2656f160b4699de88020bb4952e0ffaa3ae00febdf4c1d6e85acf116d7`,
`verify_signed_candidate.py`
`b72c99e5cf5b0fb85e79fdee874cddd26838472dab8eb4669461a567729d45f8`,
`release_artifact_verifier.py`
`584c08f0acf308a4362a6f9205495a6b730694d3f6438e1499a82abaa0d2f35b`,
and Bundletool 1.18.3
`a099cfa1543f55593bc2ed16a70a7c67fe54b1747bb7301f37fdfd6d91028e29`.

## Exact identities

GitHub artifact `9929313750`,
`nimbo-signed-candidate-fc4b6de9e28fd8956eb64462294b8bcdf405ce7e`, is
57,946,768 bytes with API SHA-256
`d7f848c2b1b32546031fbb5a438d985b7d29d313c10e9f03238f7fd82202cf11`.
Transient Actions retention expires at `2026-09-11T08:29:35Z`.

| Retained item | Bytes | SHA-256 |
| --- | ---: | --- |
| `signed-candidate-bytes.tar.gz` | 58,216,629 | `76883f1cef5838b3ad8c9509f8098821bb1c6665a649cbfddb563f25f0ecb254` |
| `signed-candidate-receipt.json` | 11,723 | `f0f65eed8d4fd502e2d1bcc71836e8d3bb8f737dadf6764824b1575e03965b32` |

The exact hosted receipt is committed as
[`receipts/signed-candidate-33852229166.json`](receipts/signed-candidate-33852229166.json).
The closed candidate tree SHA-256 is
`d2aaf8caca3e087fb6acc46eb35c9506cc51b1b52be814f1b9a14b5a6aeef9d0`.

| Surface | Exact file | Signed SHA-256 | Verified identity |
| --- | --- | --- | --- |
| Android phone | `nimbo-phone-1.1.0-vc11.aab` | `52e924d4ce5dba7370007632b9e421aa548af79b6395ba4b6b0ee1645daf6862` | package/version/source, upload certificate, Bundletool, and mapping |
| Wear OS | `nimbo-wear-1.1.0-vc1000011.aab` | `0bb295d2898a0cfcaff018ec43bc0d70663d1529771087cb48a0d7dd1b3c77a8` | package/version/source, Wear contract, upload certificate, and Bundletool |
| Apple | `Nimbo.ipa` | `20e8e4ac61c55d856aedcdf88a27a2f11ac4cb036aa2dfa002e729ace1986061` | build 10, distribution signer, app/widget/watch profiles and topology, archive/export parity, Mach-O/dSYM UUIDs, and deep code signing |

The build-10 app Mach-O/dSYM UUID is
`64AFA35C-03B1-3981-87E8-0D9B8881BB9E`. The widget UUID is
`5AD6AAB9-FB0B-3FBB-A8B1-D7EC41B5A72A`; the watch UUIDs are
`5993CC9B-2BFE-3754-AADC-E234B34F6BA1` (`arm64_32`) and
`70EAEF28-EC27-3C2F-9AC9-B9ABDFC7CC3A` (`arm64`).

The downloaded package and receipt independently matched the receipt hashes.
This local read does not replace durable materialization or the independent
trusted verifier.

## Fail-closed boundary

The receipt state is
`candidate-bytes-verified-not-manifest-promoted`. All three committed current
manifest entries therefore remain blocked with null hashes until the exact
artifact is durably materialized and independently verified.

No build-10 file has been uploaded to App Store Connect/TestFlight or a Play
track. Build 9 remains approved only in `Pending Developer Release` under manual
release and must not be published. No build-10 physical/TestFlight result,
review replacement, rollout, public availability, quality-window pass, or rank
result is claimed here.
