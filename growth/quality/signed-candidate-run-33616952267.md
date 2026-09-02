# Signed candidate run 33616952267 — 2026-09-02

Status: **PASS for protected hosted signing and candidate-byte verification;
BLOCKED for durable materialization, manifest promotion, physical distribution
QA, store delivery, review, rollout, and publication**.

The exact product/build-input authority is
`052d12c7dfa6411428d85205d9568462d20ff87d`: Android phone `1.1.0 (11)`,
Wear OS `1.1.0 (1000011)`, and Apple app/widget/watch `1.1.0 (9)`. It contains
the iPad share-sheet popover-anchor fix.

## Pre-signing authority

The synchronized evidence head
`0b7104aa69430306fb06af40d504400bd17fb320` passed all five hosted CI jobs in
[run `33615065268`](https://github.com/4810092/Weather/actions/runs/33615065268):
Android/shared, iOS, API 24 phone UI, API 36 phone UI, and API 36 tablet UI.
The iOS job included the 122 shared iOS tests, 18 glanceable-surface tests, and
an unsigned application build.

## Hosted provenance

GitHub Actions
[run `33616952267`](https://github.com/4810092/Weather/actions/runs/33616952267),
attempt 1, was manually dispatched from `refs/heads/master` at evidence head
`0b7104aa69430306fb06af40d504400bd17fb320`. It completed successfully from
`2026-09-02T09:57:49Z` through `2026-09-02T10:19:16Z`.

| Job | Job ID | Result | Window |
| --- | ---: | --- | --- |
| `build-unsigned` | `100204885515` | success | `09:57:53Z`–`10:18:00Z` |
| `sign-verify` | `100210577103` | success | `10:18:04Z`–`10:19:15Z` |

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

GitHub artifact `9842047484`,
`nimbo-signed-candidate-052d12c7dfa6411428d85205d9568462d20ff87d`, is
57,940,467 bytes with API SHA-256
`2dfe19c9d2e1ab06d161e35cb4aa579659444ef745dde9ea91de8984d7e9f1a0`.
Transient Actions retention expires at `2026-09-09T10:19:08Z`.

| Retained item | Bytes | SHA-256 |
| --- | ---: | --- |
| `signed-candidate-bytes.tar.gz` | 58,208,833 | `5b8186e0aaa1d1ba74d475ba462d545fe2f3da1a321f77fbab3f7663df021d64` |
| `signed-candidate-receipt.json` | 11,716 | `51fc10894dc9c0ff99c528a9778b01e4f78cf8354a13ca300d449c9b8fca4072` |

The exact hosted receipt is committed as
[`receipts/signed-candidate-33616952267.json`](receipts/signed-candidate-33616952267.json).
The closed candidate tree SHA-256 is
`b69d7d124c8160ee2af68667ecbd74d2f90bf72cec77b06c4a80b7ad31e55f12`.

| Surface | Exact file | Signed SHA-256 | Verified identity |
| --- | --- | --- | --- |
| Android phone | `nimbo-phone-1.1.0-vc11.aab` | `034aa0a732e0a671c341e6714162a2d22c95d06435aa327bd17b1d7b3da2f9ac` | package/version/source, upload certificate, Bundletool, and mapping |
| Wear OS | `nimbo-wear-1.1.0-vc1000011.aab` | `48a713d298be12552f08995b7cff3166df0f4ab173c62612854598eb93dcab7a` | package/version/source, Wear contract, upload certificate, and Bundletool |
| Apple | `Nimbo.ipa` | `a57674d7d467474a0697fb39c834a9829f53e68ddb9d4480168bf2dcf3f7ac29` | distribution signer, app/widget/watch profiles and topology, archive/export parity, Mach-O/dSYM UUIDs, and deep code signing |

The downloaded package and receipt independently matched the receipt hashes.
This local read does not replace durable materialization or the protected
trusted macOS verifier.

## Fail-closed boundary

The receipt state is
`candidate-bytes-verified-not-manifest-promoted`. All three committed current
manifest entries therefore remain blocked with null hashes until the exact
artifact is materialized and independently trusted-byte-verified.

No build-9 file has been uploaded to App Store Connect/TestFlight or a Play
track. No physical distribution-signed Share result, review, rollout, public
availability, quality-window pass, or ranking result is claimed here.
