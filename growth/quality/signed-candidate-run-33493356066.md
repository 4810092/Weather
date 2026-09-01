# Signed candidate run 33493356066 — 2026-09-01

Status: **PASS for protected hosted signing and byte verification; BLOCKED for
durable materialization, manifest promotion, physical QA, store delivery,
review, and publication**.

The candidate is built from product/build-input authority
`8fc43b48b65d17b3339663549cd86208f62f6bb7`: Android phone `1.1.0 (10)`,
Wear OS `1.1.0 (1000010)`, and Apple app/widget/watch `1.1.0 (8)`.

## Pre-signing authority

PR [#24](https://github.com/4810092/Weather/pull/24) fixed the duplicate-percent
share payload found during exact build-7 TestFlight QA, added the regression
test, advanced all successor release identities, and kept the canonical release
manifest fail-closed. The exact PR head
`c799118ea43a62366a3fd793e9dc7693d1d1166a` passed all five hosted CI jobs in
[run `33491998017`](https://github.com/4810092/Weather/actions/runs/33491998017)
and merged to master as `004154227112b80f594e2340ffa05e1efdf1fb65`.

Post-merge CI
[run `33493340428`](https://github.com/4810092/Weather/actions/runs/33493340428)
then passed the exact master head in all five jobs: Android/shared, iOS, and the
API 24, API 36 phone, and API 36 tablet emulator profiles.

## Hosted provenance

GitHub Actions
[run `33493356066`](https://github.com/4810092/Weather/actions/runs/33493356066),
attempt 1, was manually dispatched from `refs/heads/master` at evidence head
`004154227112b80f594e2340ffa05e1efdf1fb65`. It completed successfully from
`2026-09-01T09:39:25Z` through `2026-09-01T10:00:35Z`:

| Job | Job ID | Result | Runtime |
| --- | ---: | --- | ---: |
| `build-unsigned` | `99809785940` | success | 19m48s |
| `sign-verify` | `99815222277` | success | 1m13s |

The signing material was destroyed before the complete candidate-byte
verification step. The receipt pins these verifier inputs:

| Input | SHA-256 |
| --- | --- |
| `.github/workflows/signed-candidate.yml` | `877ffa2656f160b4699de88020bb4952e0ffaa3ae00febdf4c1d6e85acf116d7` |
| `scripts/verify_signed_candidate.py` | `b72c99e5cf5b0fb85e79fdee874cddd26838472dab8eb4669461a567729d45f8` |
| `scripts/release_artifact_verifier.py` | `584c08f0acf308a4362a6f9205495a6b730694d3f6438e1499a82abaa0d2f35b` |
| Bundletool 1.18.3 | `a099cfa1543f55593bc2ed16a70a7c67fe54b1747bb7301f37fdfd6d91028e29` |

## Immutable artifact identities

GitHub artifact `9795391062`,
`nimbo-signed-candidate-8fc43b48b65d17b3339663549cd86208f62f6bb7`,
contains exactly the candidate package and schema-v3 receipt. The artifact is
57,939,205 bytes with API and independently recomputed SHA-256
`8cd4bdae3f9f7087ce6c4b05b35f0406d3801f59799d195ddef06b92a2c9ec11`.
It expires from transient Actions storage on `2026-09-08T10:00:27Z`; it is not
yet the durable candidate authority.

| Retained item | Bytes | Compressed bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `signed-candidate-bytes.tar.gz` | 58,205,143 | 57,936,384 | `cb26a7d69fd35676957a6bfa6984f148fbe874959c133c95029e0688132ee023` |
| `signed-candidate-receipt.json` | 11,716 | 2,499 | `090ece08e9ede31502532a9622875854f7936fdb0b84036055090d3c93c27d87` |

The exact hosted receipt is committed as
[`receipts/signed-candidate-33493356066.json`](receipts/signed-candidate-33493356066.json).
The closed package contains 104 regular files and 88 directories, six expected
top-level entries, 152,287,399 payload bytes, and candidate tree SHA-256
`98523eb7846aa96b27c72c641bb075c7070d8ccfa52d27f153b8641d7f788300`.
All 192 tar members passed bounded path/type checks.

| Surface | Exact file | Signed artifact SHA-256 | Verification |
| --- | --- | --- | --- |
| Android phone | `nimbo-phone-1.1.0-vc10.aab` | `c11bc62221c11a16b1d6614aae2060af60ca7b98ad989e68dc5f87c224bbcd89` | upload certificate, package/version, source revision, Bundletool, and embedded mapping passed |
| Wear OS | `nimbo-wear-1.1.0-vc1000010.aab` | `e66a9891f70c3d532de23430d176d8c77f2bf49de55a343a7541cf0b0f99f676` | upload certificate, package/version, Wear contract, source revision, and Bundletool passed |
| Apple | `Nimbo.ipa` | `6aff05fc50a0e1546a196cc8f7f9139bfb87f8e89c0dcda7c91dc1ddb1defac4` | distribution identity, app/widget/watch topology, profiles, archive/export parity, Mach-O/dSYM UUIDs, and deep code-sign verification passed |

The phone mapping is 42,367,345 bytes with SHA-256
`178ac8d62ddb0ea7359f1c95259add2fec16b9aee561e04ce2481412c230ccae`.
The Android upload-certificate SHA-256 is
`431548a4871c9c090eee808ac3a34898f5d78602d9e747dfe81e228415aac252`;
the Apple distribution-certificate SHA-256 is
`fd4d8668a7e0f4eb9f64a12b5f0ddec0075ccde31dad50a96e978926e0e743f1`.

## Local structural recheck

The exact Actions ZIP was downloaded into the private candidate root and its
full hash matched the GitHub API digest. ZIP inventory/order, sizes,
compression, regular-file modes, encryption state, and entry hashes were
rechecked before reading the package. The tar inventory and every member type
and path were then checked without bulk extraction. Package, receipt, candidate
tree, and three artifact identities equal the hosted receipt.

This local structural recheck does not replace the required protected trusted
macOS verifier. The one-shot materialization workflow is therefore rebound to
this exact run, artifact, workflow head, package, receipt, candidate tree, and
three signed artifact identities.

## Fail-closed boundary

The receipt state remains
`candidate-bytes-verified-not-manifest-promoted`. Until durable draft
materialization succeeds and the subsequent read-only trusted macOS job repeats
the complete verifier, all three committed current manifest entries remain
`blocked` with null current hashes.

No physical phone, tablet, Wear OS, iPhone, iPad, widget, or watch result is
claimed by this record. No candidate file has been delivered to a Play track or
App Store Connect/TestFlight, submitted for review, released, or made publicly
available.
