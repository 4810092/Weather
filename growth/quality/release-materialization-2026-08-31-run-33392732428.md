# Release candidate hosted materialization — 2026-08-31

Status: **PASS for durable draft materialization; upload manifest remains
BLOCKED at 0/3 verified-current**.

Product/build-input authority remains
`2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652`. The protected signing source and
candidate identities remain those recorded by run `33381050098`; this
materialization did not rebuild, resign, or alter any candidate byte.

Manual GitHub-hosted workflow
[`33392732428`](https://github.com/4810092/Weather/actions/runs/33392732428)
ran from `master` at evidence head
`30a67edf2968878e22bd05497bcd20c64cba7fc7` and completed successfully at
`2026-08-31T12:38:17Z`. Its single standard `ubuntu-24.04` job performed the
following fail-closed checks:

- bound source Actions run `33381050098`, attempt 1, artifact `9754332100`,
  signing workflow head `dd6e275e840947ec6b22b9485ebeb63d5eaa320c`, and
  reviewed workflow SHA-256
  `fd96eb999047cc033beb211eb09761dbbe68ec341dc9f3cf5902adfadfdebc55`;
- downloaded the exact GitHub artifact ZIP and matched its API/byte SHA-256
  `f1754ff767d908cd6be5ce5652e05e6f3dc8721ffa1b0db303d72a5d27cf5478`;
- admitted only the expected package and receipt ZIP entries, checked their
  sizes and hashes, and rejected unsafe or unexpected archive members;
- checked the package inventory and the schema-v3 receipt bindings for source,
  signing run, workflow, package, candidate tree, and all three artifact
  identities;
- created one unpublished draft/prerelease storage release, uploaded only the
  two expected assets, then re-read the release, asset, and Git-ref APIs and
  rechecked the exact state, sizes, and SHA-256 digests.

## Durable draft locator

| Field | Verified value |
| --- | --- |
| Repository | `4810092/Weather` (`1329018769`) |
| Draft release ID | `379745439` |
| Draft storage name | `[DRAFT STORAGE] Nimbo 1.1.0 signed candidate 2cdd438` |
| Storage tag name | `nimbo-candidate-v1.1.0-2cdd438-run-33381050098` |
| Target commit | `30a67edf2968878e22bd05497bcd20c64cba7fc7` |
| Release state | `draft=true`, `prerelease=true`, `published_at=null` |
| Git tag/ref | absent; the unpublished draft did not create a Git tag |
| Candidate package asset | ID `537966386`, `signed-candidate-bytes.tar.gz`, 58,073,521 bytes |
| Candidate package SHA-256 | `60c827ef9f5d2cdc51add5344bd33ab780ab1be3154a3f3da8c22074ddb518d9` |
| Candidate receipt asset | ID `537966414`, `signed-candidate-receipt.json`, 11,711 bytes |
| Candidate receipt SHA-256 | `c852c61e07289d2a7a8f211efc91d7f30fab2c3475465ba000625780a21de19c` |
| Closed candidate tree SHA-256 | `c91ea40ae12fd59aacfee77f03ba75240951b5797c16b23487ce334eb85502fa` |

The hosted package still binds the candidate artifact hashes:

- Android phone `1.1.0 (8)`:
  `d4a90676f32745ea314b50ced2c9955e86923589534a1a7654ac6f1207e88a62`;
- Wear OS `1.1.0 (1000008)`:
  `e76d685b20e86f8878be7c9a1a59ac6edb5781ec8e61d5ecd36feb52ddc1cccf`;
- Apple app/widget/watch `1.1.0 (6)`:
  `7466afb1a06f3000ad5d095734082d57cf58e992bdd7a8bed326e90d26ba39d0`.

This closes the previous absence of a CI-readable hosted materialization and
removes the expiring Actions artifact as the only hosted copy. It is not WORM:
GitHub reports the draft release as `immutable=false`, and an authorized writer
could still modify, publish, or delete it. The exact IDs, sizes, and hashes
therefore remain mandatory inputs to every later use.

## Why the manifest remains blocked

Run `33392732428` is a storage/materialization check, not the complete trusted
release verifier. It did not use macOS, did not download the draft assets in a
separate read-only job, did not run pinned Bundletool plus the complete
`release_artifact_verifier.py` Apple/Android checks against the materialized
tree, and did not provide physical-device evidence. The current workflow also
performs validation and draft writes in one job; the intended static
write/read permission split remains pending.

Accordingly, all three manifest entries remain `source_sync=blocked`, with
`sha256`, `signing_evidence`, and `physical_qa_evidence` still null and their
historical candidates unchanged. The next release-engineering step is a
separate read-only GitHub-hosted macOS verification path that downloads assets
`537966386` and `537966414` by authenticated API, checks the locator and hashes,
safely materializes the package, and runs the full pinned verifier. Only then
may all three entries be promoted atomically; delivery-linked physical QA
remains a separate gate.

No store upload, processing, TestFlight or Play internal distribution, review,
release, publication, public availability, or ranking evidence is claimed.
