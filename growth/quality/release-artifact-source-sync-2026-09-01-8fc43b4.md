# Release artifact/source sync — 2026-09-01 — 8fc43b4

Status: **BLOCKED. Source identity, protected signed candidates, and durable
draft materialization are current; trusted verification and manifest promotion
are still 0/3**.

The authoritative product/build-input revision is
`8fc43b48b65d17b3339663549cd86208f62f6bb7`. It resolves to Android phone
`1.1.0 (10)`, Wear OS `1.1.0 (1000010)`, and Apple app/widget/watch
`1.1.0 (8)`.

This revision succeeds the exact build-7 TestFlight physical result recorded
in
[testflight-ios-build7-smoke-2026-09-01.md](testflight-ios-build7-smoke-2026-09-01.md).
It normalizes an escaped `%%` left in the iOS Compose-resource formatting path
before constructing the share payload and adds a regression test that requires
one literal percent sign, the localized store call to action, and the canonical
platform link. Targeted Android-host execution of
`StoreLinkProviderTest` passed on 2026-09-01. The release identities, including
the generated and source Apple project declarations, were then advanced
monotonically to phone vc10, Wear vc1000010, and Apple build 8.

Exact-source hosted CI passed at merge commit
`004154227112b80f594e2340ffa05e1efdf1fb65`. Protected signing run
[`33493356066`](https://github.com/4810092/Weather/actions/runs/33493356066)
then produced phone vc10, Wear vc1000010, and Apple build 8 from the authoritative
product revision and verified every signed byte after destroying the ephemeral
signing material. The exact Actions ZIP, package, receipt, candidate tree, and
three artifact identities were independently hash/structure checked locally and
are recorded in
[`signed-candidate-run-33493356066.md`](signed-candidate-run-33493356066.md).

Materialization run
[`33498085260`](https://github.com/4810092/Weather/actions/runs/33498085260)
copied the exact package and receipt into unpublished draft release `380406897`
as assets `539393445` and `539393546`, then redownloaded and hash-checked both.
The draft remains mutable, has no Git tag, and is recorded in
[`release-materialization-2026-09-01-run-33498085260.md`](release-materialization-2026-09-01-run-33498085260.md).

The package has not yet passed the separate read-only trusted macOS verifier.
The upload manifest therefore keeps every current SHA-256, signing evidence,
and physical QA field null with `source_sync=blocked`; the exact
vc9/vc1000009/build-7 artifacts remain historical evidence and cannot be
relabeled current.

Production remains unchanged. No upload, review, rollout, public availability,
crash-gate closure, or rank effect is claimed.
