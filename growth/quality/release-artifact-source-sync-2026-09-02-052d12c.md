# Release artifact source sync — 2026-09-02 — 052d12c

Status: **PASS for exact source and signed-byte identity; the manifest is
atomically 3/3 current. Store delivery and physical QA remain blocked**.

The exact product/build-input authority is
`052d12c7dfa6411428d85205d9568462d20ff87d`. It contains the iPad share-sheet
popover-anchor fix and resolves monotonically to Android phone `1.1.0 (11)`,
Wear OS `1.1.0 (1000011)`, and Apple app/widget/watch `1.1.0 (9)`.

Protected GitHub Actions run
[`33616952267`](https://github.com/4810092/Weather/actions/runs/33616952267)
successfully produced and candidate-byte-verified the exact source-current set.
Its schema-v3 receipt binds phone SHA-256
`034aa0a732e0a671c341e6714162a2d22c95d06435aa327bd17b1d7b3da2f9ac`,
Wear SHA-256
`48a713d298be12552f08995b7cff3166df0f4ab173c62612854598eb93dcab7a`,
and Apple IPA SHA-256
`a57674d7d467474a0697fb39c834a9829f53e68ddb9d4480168bf2dcf3f7ac29`.
Hosted materialization run
[`33626711140`](https://github.com/4810092/Weather/actions/runs/33626711140)
then created unpublished draft release `381212810` and durably stored only the
exact package and receipt.

Exact-source master CI run
[`33628011906`](https://github.com/4810092/Weather/actions/runs/33628011906)
passed all five jobs at evidence head
`cffb55ae6f52bb91893b398d3a9bfdad92a9d7ac`. Protected trusted run
[`33629490609`](https://github.com/4810092/Weather/actions/runs/33629490609)
then reopened the exact mutable draft, validated the committed blocked
contract, safely extracted the closed candidate tree, and returned
`source_sync=verified-current` plus `byte_verified=true` for phone vc11, Wear
vc1000011, and Apple build 9. It revalidated live master and the staged asset
identities after verification. The complete boundary is recorded in
[`release-artifact-full-verification-2026-09-02-build9-hosted.md`](release-artifact-full-verification-2026-09-02-build9-hosted.md).

The upload manifest is therefore promoted atomically to
`source_sync=verified-current` with the exact three SHA-256 values and current
signing evidence. Every `physical_qa_evidence` field remains null and the
manifest remains `draft-blocked`. Exact vc10/vc1000010/build-8 artifacts remain
historical evidence and cannot be relabeled current.

Production remains unchanged. No upload, review, rollout, public availability,
crash-gate closure, physical QA, or rank effect is claimed. Because the draft
is mutable, its protected hosted chain must pass again before every later use.
