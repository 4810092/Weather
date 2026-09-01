# Trusted hosted release verification — 2026-09-01

Status: **PASS for the protected hosted byte-verification boundary**.

This record closes the hosted repeat for the replacement `1.1.0` candidate.
It does not close physical-device, store-processing, crash, review,
publication, or ranking gates.

## Trusted invocation

- Repository: `4810092/Weather`, repository ID `1329018769`.
- Source CI: run
  [`33481183010`](https://github.com/4810092/Weather/actions/runs/33481183010),
  successful `push` to `master` at
  `18ebcf4b807c9ac226af16c3eba47284aa6583b7`.
- Trusted workflow: run
  [`33482814222`](https://github.com/4810092/Weather/actions/runs/33482814222),
  attempt 1, completed successfully at `2026-09-01T07:36:10Z`.
- The no-checkout Ubuntu `stage` job completed successfully. The separate
  read-only macOS `verify` job validated the workflow-run binding and current
  master, checked out the exact source authority, safely extracted the closed
  package, fetched pinned Bundletool, ran the complete verifier, and
  revalidated master plus staged-file identities before publishing a
  non-secret receipt.

## Mutable draft rechecked

The workflow checked draft release `380257470` before and after download. It
remained unpublished, mutable, and contained exactly these uploaded assets:

| Asset | ID | Size | SHA-256 |
| --- | ---: | ---: | --- |
| `signed-candidate-bytes.tar.gz` | `539108193` | 58,200,250 | `448f2682c3fb2c2c186e0eebe794183d7cbd60e75312448dc9bae7ef608b8af3` |
| `signed-candidate-receipt.json` | `539108272` | 11,711 | `27bebc799d936268ebd1669f732284318fb538019612305dfbaab7347b3902f1` |

The draft remained `draft=true`, `prerelease=true`, `published_at=null`, and
`immutable=false`. Its target remained materialization merge
`594394736a2bc517e00a183cd30160c56199cff2`; the draft tag did not resolve to a
Git ref. Live `master` did not change during staging or verification.

## Exact artifact result

The full verifier returned `source_sync=verified-current` and
`byte_verified=true` for all three coordinated artifacts from product source
revision `ba824beae5e72653e42af2b8b78286f61415e3ab`:

| Surface | Identity | SHA-256 | Verified identity |
| --- | --- | --- | --- |
| Android phone | `1.1.0 (9)` | `0fd5ae542a71f8cccb1cbbd043ffef09df9f29a2c1c6642010cfcce579f00681` | package `uz.ganikhodjaev.weather`, upload certificate `431548a4871c9c090eee808ac3a34898f5d78602d9e747dfe81e228415aac252` |
| Wear OS | `1.1.0 (1000009)` | `9ce725e755a09d783adacc1691d5e20a0773b88aa63e9365c00af50f51e6542c` | package `uz.ganikhodjaev.weather`, same upload certificate |
| Apple app/widget/watch | `1.1.0 (7)` | `b918a8d7fa66d1755ca05486ee02ffac6a73b96ddd72f681bd3f6bfb3108709d` | team `5SWEZ7HTYP`, distribution certificate `fd4d8668a7e0f4eb9f64a12b5f0ddec0075ccde31dad50a96e978926e0e743f1`, matching profiles and dSYM UUIDs |

Bundletool `1.18.3` was pinned by SHA-256
`a099cfa1543f55593bc2ed16a70a7c67fe54b1747bb7301f37fdfd6d91028e29`.

The non-secret workflow receipt is artifact `9790610607`, named
`trusted-release-verification-18ebcf4b807c9ac226af16c3eba47284aa6583b7`,
with GitHub artifact digest
`303366e1f5d35413cf3fdd1c6cda1f7cb3c375be1552f5253a0e0416d82df74d`.
Its contained JSON has SHA-256
`bc3c3be0518613cb7e9b2521918ffc7c2fe972a45c471c8f57a253ac01d8e215`.

## Retention and boundary

The exact hosted stage, receipt, verifier receipt, extracted byte tree,
pinned Bundletool, GitHub metadata, and complete checksums are retained outside
Git under the private candidate directory for signing run `33473684554`.

The protected hosted repeat is complete. The draft remains mutable, so every
later reuse must still pass the protected chain against live release and asset
identities. Standard GitHub-hosted runners remain the canonical CI path; no
self-hosted Mac runner is required.

The upload manifest remains `draft-blocked`. This pass does not claim a
physical install, TestFlight readiness, production review or rollout, public
availability, crash resolution, or Top-10 rank.
