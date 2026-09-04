# Release materialization run 33855931653 — 2026-09-04

Status: **PASS for durable unpublished candidate storage; BLOCKED for
independent trusted verification, manifest promotion, store upload, TestFlight
runtime QA, review replacement, rollout, and publication**.

Manual GitHub Actions
[run `33855931653`](https://github.com/4810092/Weather/actions/runs/33855931653)
executed the reviewed `release-materialization.yml` from exact master
`ebe60d1b43c687fcb08c5c762cdcc9e772e6c1ce`. Its single job
`100969124308` passed from `2026-09-04T08:57:18Z` through
`2026-09-04T08:57:31Z`.

The workflow first revalidated protected signing run `33852229166`, attempt 1,
source head `9b785e19b52f09e3eca37cf0c00ef961a03bd73b`, source revision
`fc4b6de9e28fd8956eb64462294b8bcdf405ce7e`, signed-candidate artifact
`9929313750`, and the pinned signing-workflow bytes. It then checked the exact
GitHub artifact ZIP, both ZIP entries and their order, the safe 192-member
candidate tar inventory, its receipt, and all three signed artifact hashes.

## Exact unpublished storage identity

- Draft release ID: `382592451`.
- Name: `[DRAFT STORAGE] Nimbo 1.1.0 signed candidate fc4b6de`.
- Logical tag name: `nimbo-candidate-v1.1.0-fc4b6de-run-33852229166`.
- Target commit: `ebe60d1b43c687fcb08c5c762cdcc9e772e6c1ce`.
- State: `draft=true`, `prerelease=true`, `published_at=null`,
  `immutable=false`.
- The logical tag does not resolve as a Git ref before or after
  materialization.

| Asset | ID | Bytes | API SHA-256 |
| --- | ---: | ---: | --- |
| `signed-candidate-bytes.tar.gz` | `544061853` | 58,216,629 | `76883f1cef5838b3ad8c9509f8098821bb1c6665a649cbfddb563f25f0ecb254` |
| `signed-candidate-receipt.json` | `544061890` | 11,723 | `f0f65eed8d4fd502e2d1bcc71836e8d3bb8f737dadf6764824b1575e03965b32` |

The final draft inventory contains exactly those two uploaded assets. The
workflow downloaded them again through their fixed asset IDs and rechecked
both sizes and SHA-256 values after upload. The candidate tree remains
`d2aaf8caca3e087fb6acc46eb35c9506cc51b1b52be814f1b9a14b5a6aeef9d0`;
exact phone, Wear, and Apple artifact hashes remain those recorded in
[`signed-candidate-run-33852229166.md`](signed-candidate-run-33852229166.md).

## Boundary

This is durable private GitHub storage, not an immutable published release.
Every later use must re-read the fixed release and asset endpoints, check the
draft and no-tag state before and after download, and independently verify the
complete signed bytes. No asset was sent to App Store Connect, TestFlight, or
Google Play, and no review, release, rollout, Pages deployment, or public
availability state changed.
