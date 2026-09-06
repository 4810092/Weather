# Build 11 durable materialization — 2026-09-06

Status: **PASS for retaining the exact signed package in unpublished storage**.

[Materialization run 34048604324](https://github.com/4810092/Weather/actions/runs/34048604324)
passed on `798f4f418a975ac016dbacbd1c9f153ea5a02fcb`. It reopened signing run
`34047427535`, artifact `9993782037`, and exact signing workflow bytes, then
validated ZIP and tar inventories, sizes, all signed hashes and receipt
provenance before retaining the two files.

- Product source: `fcffe13be1cc15e83a0609751f696e48c9301444`.
- Unpublished draft release: `383662265`.
- Logical storage tag: `nimbo-candidate-v1.1.0-fcffe13-run-34047427535`.
- Draft target commit: `798f4f418a975ac016dbacbd1c9f153ea5a02fcb`.
- Package asset: `547465393`, 59,062,201 bytes, SHA-256
  `1465c62400d2a791ecd82ec14bfc6ff216b7b84ab44382be8161d5d7a05df463`.
- Receipt asset: `547465445`, 11,723 bytes, SHA-256
  `1ceff60fb22b813b86e27ffcc478848a008740e502767461d501edff9df5729b`.

The hosted job checked tag absence, exact draft status, exact asset set,
post-upload metadata and reopened asset bytes. A separate read-only API check
confirmed both asset IDs, sizes and hashes, `draft=true`, `prerelease=true`,
`published_at=null`, and the exact target commit above.

This is private artifact retention for the owner-authorized TestFlight delivery.
It is not GitHub release publication, a store upload, review replacement,
runtime proof or public availability. The draft is mutable: recheck these fixed
endpoints at each later use. Independent trusted byte verification is next.
