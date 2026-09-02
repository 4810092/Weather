# Release artifact source sync — 2026-09-02 — 052d12c

Status: **SIGNED CANDIDATE VERIFIED; BLOCKED pending durable materialization and
trusted hosted byte verification**.

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
The upload manifest still keeps all three current artifact hashes and signing
evidence null with `source_sync=blocked`, because transient Actions storage and
the signing job alone do not satisfy durable materialization plus independent
trusted-hosted verification. The prior vc10/vc1000010/build-8 set remains
historical evidence only.

Required next action: materialize only run `33616952267` artifact `9842047484`
using its exact API digest, package, receipt, tree, and artifact hashes, then run
the independent trusted-byte chain before any internal delivery or later
release decision.

This record proves the protected signing checkpoint only. It does not prove
durable retention, manifest promotion, upload, internal delivery, physical QA,
review, publication, or public availability.
