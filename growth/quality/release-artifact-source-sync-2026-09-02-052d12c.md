# Release artifact source sync — 2026-09-02 — 052d12c

Status: **BLOCKED**.

The exact product/build-input authority is
`052d12c7dfa6411428d85205d9568462d20ff87d`. It contains the iPad share-sheet
popover-anchor fix and resolves monotonically to Android phone `1.1.0 (11)`,
Wear OS `1.1.0 (1000011)`, and Apple app/widget/watch `1.1.0 (9)`.

No protected-signed or independently byte-verified artifacts are yet bound to
this source revision. The upload manifest therefore keeps all three current
artifact hashes and signing evidence null with `source_sync=blocked`. The prior
vc10/vc1000010/build-8 set remains historical evidence only and must not be
promoted or represented as source-current.

Required next action: complete the protected signed-candidate workflow for the
exact authority above, import its immutable receipt without weakening any
gate, and re-run the independent materialization and trusted-byte chain before
any internal delivery or later release decision.

This record proves a fail-closed source transition only. It does not prove
signing, upload, internal delivery, physical QA, review, publication, or public
availability.
