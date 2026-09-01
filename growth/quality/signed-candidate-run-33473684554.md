# Signed candidate run 33473684554 — 2026-09-01

Status: **PASS for protected hosted signing and independent byte verification;
BLOCKED for manifest promotion, physical QA, store upload, review, and
publication**.

The candidate is built from product/build-input authority
`ba824beae5e72653e42af2b8b78286f61415e3ab`: Android phone `1.1.0 (9)`,
Wear OS `1.1.0 (1000009)`, and Apple app/widget/watch `1.1.0 (7)`.

## Pre-signing authority

PR [#20](https://github.com/4810092/Weather/pull/20) replaced the macOS Bash
3.2-unsafe bare verifier digest assertions with explicit mismatch branches and
`exit 1`, pinned the current artifact verifier bytes, and added repository and
regression checks for verifier-pin drift. The PR passed all five hosted CI jobs
and merged as `8ef4b0211855126087163883658a2abc2bcd7a7a`.

Post-merge CI
[run `33472603346`](https://github.com/4810092/Weather/actions/runs/33472603346)
then passed the exact same master head in all five jobs: Android/shared, iOS,
and the API 24, API 36 phone, and API 36 tablet emulator profiles.

## Hosted provenance

GitHub Actions
[run `33473684554`](https://github.com/4810092/Weather/actions/runs/33473684554),
attempt 1, was manually dispatched from `refs/heads/master` at evidence head
`8ef4b0211855126087163883658a2abc2bcd7a7a`. It completed successfully from
`2026-09-01T05:27:44Z` through `2026-09-01T05:40:53Z`:

| Job | Job ID | Result | Runtime |
| --- | ---: | --- | ---: |
| `build-unsigned` | `99748409141` | success | 11m44s |
| `sign-verify` | `99750646988` | success | 1m22s |

The receipt pins these verifier inputs:

| Input | SHA-256 |
| --- | --- |
| `.github/workflows/signed-candidate.yml` | `877ffa2656f160b4699de88020bb4952e0ffaa3ae00febdf4c1d6e85acf116d7` |
| `scripts/verify_signed_candidate.py` | `b72c99e5cf5b0fb85e79fdee874cddd26838472dab8eb4669461a567729d45f8` |
| `scripts/release_artifact_verifier.py` | `584c08f0acf308a4362a6f9205495a6b730694d3f6438e1499a82abaa0d2f35b` |
| Bundletool 1.18.3 | `a099cfa1543f55593bc2ed16a70a7c67fe54b1747bb7301f37fdfd6d91028e29` |

## Immutable artifact identities

GitHub artifact `9787670569`,
`nimbo-signed-candidate-ba824beae5e72653e42af2b8b78286f61415e3ab`,
contains exactly the candidate package and schema-v3 receipt. The GitHub ZIP is
57,930,778 bytes with API and independently recomputed SHA-256
`381102d3ac0dbfb4f309b0dd050e681e8be558bcc9c4a4705b6ef9fcad51364d`.
ZIP integrity, entry order, regular-file modes, encryption state, compression
method, and duplicate-name checks passed before extraction.

| Retained item | Bytes | Compressed bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `signed-candidate-bytes.tar.gz` | 58,200,250 | 57,927,962 | `448f2682c3fb2c2c186e0eebe794183d7cbd60e75312448dc9bae7ef608b8af3` |
| `signed-candidate-receipt.json` | 11,711 | 2,494 | `27bebc799d936268ebd1669f732284318fb538019612305dfbaab7347b3902f1` |

The exact hosted receipt is committed as
[`receipts/signed-candidate-33473684554.json`](receipts/signed-candidate-33473684554.json).
The closed package contains 104 regular files and 88 directories, six expected
top-level entries, 152,286,965 payload bytes, and candidate tree SHA-256
`bcce519c01859e74b0dda904b817f626ce794ff6788aee2ab9fdcaca7c24f84e`.
All 192 tar members were path-validated before bounded extraction; no absolute,
parent, link, or special entries were accepted.

| Surface | Exact file | Signed artifact SHA-256 | Verification |
| --- | --- | --- | --- |
| Android phone | `nimbo-phone-1.1.0-vc9.aab` | `0fd5ae542a71f8cccb1cbbd043ffef09df9f29a2c1c6642010cfcce579f00681` | upload certificate, package/version, source revision, Bundletool, and embedded mapping passed |
| Wear OS | `nimbo-wear-1.1.0-vc1000009.aab` | `9ce725e755a09d783adacc1691d5e20a0773b88aa63e9365c00af50f51e6542c` | upload certificate, package/version, Wear contract, source revision, and Bundletool passed |
| Apple | `Nimbo.ipa` | `b918a8d7fa66d1755ca05486ee02ffac6a73b96ddd72f681bd3f6bfb3108709d` | distribution identity, app/widget/watch topology, profiles, entitlements, archive/export parity, Mach-O/dSYM UUIDs, and deep code-sign verification passed |

The phone mapping is 42,366,661 bytes with SHA-256
`878b1050fb71afebdfea037845c85cef60536d475de70dff281cd44478184055`.
The Android upload-certificate SHA-256 is
`431548a4871c9c090eee808ac3a34898f5d78602d9e747dfe81e228415aac252`;
the Apple distribution-certificate SHA-256 is
`fd4d8668a7e0f4eb9f64a12b5f0ddec0075ccde31dad50a96e978926e0e743f1`.

## Independent verification

The exact GitHub ZIP was downloaded to the explicit private temporary release
root `/tmp/nimbo-signing-run-33473684554/` and matched the API size and digest
before inspection. The package was safely extracted, a detached clean worktree
at `ba824beae5e72653e42af2b8b78286f61415e3ab` was created, and the pinned
isolated verifier was run again with Bundletool 1.18.3 and the receipt-bound
Apple profile identities.

The independent run returned success for all three artifacts. Its candidate
tree and every artifact identity equal the hosted receipt. After removing only
the generated tar filename and wrapper SHA fields, the hosted and independent
receipts are structurally identical. The independent tar wrapper has SHA-256
`da9bdfa5e9c159e6ee543bd1f8e53e7fb4c9a7baedc859b1974d61f3394e7c76`;
it is evidence only and is not substituted for the exact hosted package. A
separate `/usr/bin/codesign --verify --deep --strict` check of the retained app
also passed.

## Fail-closed boundary

The receipt state remains
`candidate-bytes-verified-not-manifest-promoted`. The one-shot materialization
workflow is being rebound to this exact run, artifact, ZIP, package, receipt,
workflow, candidate tree, and three signed artifact identities. Until that
workflow succeeds and the subsequent trusted macOS verification promotes the
manifest atomically, all three current manifest entries remain `blocked` with
null current hashes.

No physical phone, tablet, Wear OS, iPhone, iPad, widget, or watch result is
claimed by this record. No file from this candidate has yet been uploaded to a
Play track or App Store Connect/TestFlight, submitted for review, released, or
made publicly available.
