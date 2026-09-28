# Build 12 durable materialization — September 28, 2026

Status: **PASS for retaining the exact signed package in unpublished storage**.

[Materialization run 36363383305](https://github.com/4810092/Weather/actions/runs/36363383305)
passed on `16658ec4d3aa9e45003d1a66e1cafeef8a657a1c`. It reopened protected signing run
`36361077488`, artifact `10946307432`, and the pinned signer workflow; checked
ZIP/tar inventory, sizes, hashes, source and receipt provenance; and retained
the two exact files. The 15 materializer security mutation tests and all 367
release/growth Python tests passed before dispatch. Independent review found
only exact identity-pin changes, with no safety-logic changes.

- Product source: `0faf1105cc5da072e4e9ee043c46e2e9de4f4ada`.
- Unpublished draft: `397876280`; logical tag `nimbo-candidate-v1.1.0-0faf110-run-36361077488`.
- Draft target: `16658ec4d3aa9e45003d1a66e1cafeef8a657a1c`.
- Package asset `594106923`: 59,062,873 bytes,
  SHA-256 `b42ab34cb0a332268d45a16dbb7ebc253c782995dd1ffc0bba27ce128d755fed`.
- Receipt asset `594106988`: 11,723 bytes,
  SHA-256 `3f1ff98e565e46d65c7f47b01dbbded8b499e78515acc01e7dc80a0ebb7c133e`.

The job checked tag absence before and after, draft/prerelease status,
exact asset inventory, post-upload API metadata, and reopened asset bytes.
A separate authenticated read-only API check confirmed the fixed release and
asset IDs, sizes/hashes, target commit, `draft=true`, `prerelease=true`, and
`published_at=null`.

This is internal artifact retention for the authorized store release. It is not
GitHub publication, a store upload, runtime proof, review, rollout, or public
availability. The draft remains mutable and must be reopened through independent
trusted byte verification before use. Current manifest entries remain blocked.
