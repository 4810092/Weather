# Release artifact source sync — 2026-08-31 signed candidate checkpoint

Status: **3/3 source-current candidate artifacts signed, byte-verified, and
durably draft-materialized; committed upload manifest remains BLOCKED**.

The product/build-input authority remains
`2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652`, resolving to Android phone
`1.1.0 (8)`, Wear OS `1.1.0 (1000008)`, and Apple app/widget/watch
`1.1.0 (6)`. Evidence-only changes after that commit do not alter the release
source paths enforced by `scripts/release_artifact_verifier.py`.

Exact-source ordinary GitHub-hosted CI
[`33300967788`](https://github.com/4810092/Weather/actions/runs/33300967788)
passed the Android/shared and Apple jobs plus the API 24 phone, API 36 phone,
and API 36 tablet Compose UI matrix. The more recent protected signing run
[`33381050098`](https://github.com/4810092/Weather/actions/runs/33381050098)
then passed both jobs and produced the schema-v3 receipt committed at
[`receipts/signed-candidate-33381050098.json`](receipts/signed-candidate-33381050098.json).
Full signing, profile, archive, package, independent-verification, and retention
evidence is in
[`signed-candidate-run-33381050098.md`](signed-candidate-run-33381050098.md).

| Surface | Candidate SHA-256 | Candidate verifier result | Manifest state |
| --- | --- | --- | --- |
| Android phone `1.1.0 (8)` | `d4a90676f32745ea314b50ced2c9955e86923589534a1a7654ac6f1207e88a62` | `candidate-verified`, byte verified | `blocked` |
| Wear OS `1.1.0 (1000008)` | `e76d685b20e86f8878be7c9a1a59ac6edb5781ec8e61d5ecd36feb52ddc1cccf` | `candidate-verified`, byte verified | `blocked` |
| Apple `1.1.0 (6)` | `7466afb1a06f3000ad5d095734082d57cf58e992bdd7a8bed326e90d26ba39d0` | `candidate-verified`, byte verified | `blocked` |

The complete hosted candidate package SHA-256 is
`60c827ef9f5d2cdc51add5344bd33ab780ab1be3154a3f3da8c22074ddb518d9`;
the closed candidate tree SHA-256 is
`c91ea40ae12fd59aacfee77f03ba75240951b5797c16b23487ce334eb85502fa`.
The exact package and receipt were downloaded against GitHub artifact digest
`f1754ff767d908cd6be5ce5652e05e6f3dc8721ffa1b0db303d72a5d27cf5478`,
independently re-verified, and retained in a private checksum-verified release
namespace outside the repository.

Subsequent hosted materialization
[`33392732428`](https://github.com/4810092/Weather/actions/runs/33392732428)
validated the exact source artifact/package/receipt bindings and stored those
two files as assets `537966386` and `537966414` in unpublished draft release
`379745439`. The exact locator, sizes, hashes, mutable-draft boundary, and
remaining verifier split are recorded in
[`release-materialization-2026-08-31-run-33392732428.md`](release-materialization-2026-08-31-run-33392732428.md).

## Why the manifest is still blocked

`candidate-verified` is intentionally a pre-manifest state. A
`verified-current` manifest entry causes the ordinary verifier to require the
real external artifact bytes and pinned Bundletool; Apple verification also
requires macOS signing tools. The durable draft locator now exists, but the
materialization ran in a single write-capable Ubuntu job. A separate read-only
hosted macOS job has not downloaded the draft assets and rerun the complete
pinned verifier. Promotion or a skip before that trusted split passes would
weaken the fail-closed contract, so neither is used.

The schema-v2 upload manifest therefore remains `draft-blocked`; all three
current SHA-256, signing-evidence, and physical-QA fields remain null, as its
blocked schema requires. The materializer checked locator, size, package SHA,
archive safety, exact inventory, and receipt bindings. Promotion now requires
the remaining read-only macOS full-verifier stage. Only after that stage passes
may all three entries move atomically to `verified-current`.

## Remaining release boundaries

- The upload-key-signed Android AABs have not been uploaded to Google Play or
  exercised as store-delivered splits; the exact candidate still needs the
  phone/tablet/widget and paired Wear OS physical matrix.
- The Apple IPA uses App Store profiles and is not directly installable. The
  exact retained IPA must be uploaded unchanged, processed as build
  `1.1.0 (6)`, and exercised through TestFlight on iPhone, iPad, widget, and
  paired watch.
- The production iOS crash diagnostic/symbolication and post-rollout evidence
  remain missing.

No store upload, build association, TestFlight/internal-track distribution,
review submission, rollout, publication, or rank claim is made here.
