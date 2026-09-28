# Signed candidate run 36361077488 — September 28, 2026

Status: **PASS for protected signing and candidate-byte verification**.
Independent trusted verification, delivery, runtime QA, and publication remain separate.

Product authority `0faf1105cc5da072e4e9ee043c46e2e9de4f4ada` retains the latest autonomous widget refresh,
actor-isolation, and iPad Share fixes. Candidates are phone `1.1.0 (12)`,
Wear `1.1.0 (1000012)`, and Apple app/widget/watch `1.1.0 (12)`.

[Protected signing run 36361077488](https://github.com/4810092/Weather/actions/runs/36361077488)
attempt 1 completed successfully at `2026-09-28T00:38:22Z` from workflow head
`9d96056de4a3f62f6a33e3528bdd965590a39ad8`. Both unsigned-build and protected signing/verification jobs
passed. The signer workflow remains SHA-256
`877ffa2656f160b4699de88020bb4952e0ffaa3ae00febdf4c1d6e85acf116d7`.
All three canonical local CI modes also passed; see the
[local validation record](release12-local-validation-2026-09-28.md).

The exact schema-v3 [receipt](receipts/signed-candidate-36361077488.json) binds:

| Artifact | SHA-256 |
| --- | --- |
| Phone AAB vc12 | `5fdc866094226d7cde09696e6fd2de27683af0ee6955674b3a1d29a7c203a2cd` |
| Wear AAB vc1000012 | `51a1d4f0a8e5b8cfa6cb6d752e1a3aad56de36749eaa6fb551039a1f429b23e4` |
| Apple IPA build12 | `b42d0bf6a218ba1b5ed3d607a18611fbf700fadef856b02861f618411585474d` |

Actions artifact `10946307432` has 58,795,513 bytes and ZIP SHA-256
`a170d6a31aad57360ffea1f0b7263b4228bc639b87e8708c9bc0e37912707eb3`. The authenticated local download matched both.
The two regular ZIP entries, receipt provenance, safe tar paths/types/modes,
all artifact digests, and canonical extracted tree were checked independently.

| Package file | Bytes | SHA-256 |
| --- | ---: | --- |
| signed-candidate-bytes.tar.gz | 59,062,873 | `b42ab34cb0a332268d45a16dbb7ebc253c782995dd1ffc0bba27ce128d755fed` |
| signed-candidate-receipt.json | 11,723 | `3f1ff98e565e46d65c7f47b01dbbded8b499e78515acc01e7dc80a0ebb7c133e` |

The package has 192 members (104 regular files and
88 directories), 154,585,546 expanded bytes, and
canonical tree SHA-256 `5316328a69699e03acb9d149b7b9e77a0480630f0e26c10259de9f3501fa0564`.
The signer verified package IDs, version codes/builds, embedded source revision,
upload/distribution certificates, Apple profiles and App Groups, archive/export
parity, matching dSYMs, and watch topology.

The current manifest stays blocked until durable materialization and independent
trusted full-byte verification pass. This note does not claim store upload,
natural background completion, review, rollout, or public availability.
