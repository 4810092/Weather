# Signed candidate run 34047427535 — 2026-09-06

Status: **PASS for protected signing and candidate-byte verification**.
Independent trusted verification and TestFlight delivery remain separate.

Product authority `fcffe13be1cc15e83a0609751f696e48c9301444` contains autonomous
WidgetKit refresh and the retained build-10 actor-isolation fix. Apple app,
widget, and watch are `1.1.0 (11)`; Android phone and Wear remain `1.1.0 (11)`
and `1.1.0 (1000011)`.

Protected [signing run 34047427535](https://github.com/4810092/Weather/actions/runs/34047427535),
attempt 1, completed successfully from `2026-09-06T17:04:08Z` to
`2026-09-06T17:21:43Z`. It was dispatched from master evidence head
`8f2e0f970b0a70be091f7608bd6051582a1fc6b2` and built the exact authority above.
Both `build-unsigned` and `sign-verify` passed. Workflow SHA-256 remains
`877ffa2656f160b4699de88020bb4952e0ffaa3ae00febdf4c1d6e85acf116d7`.

Canonical local `scripts/local-ci.sh apple` and `core` passed. The core gate
included all 367 release/growth tests, repository and metadata contracts,
shared/platform tests, lint, SQLDelight migration checks and release bundles.
The Apple gate included 37 Swift tests, shared iOS tests and unsigned builds.

The exact schema-v3 [receipt](receipts/signed-candidate-34047427535.json) binds
these files:

| Surface | SHA-256 |
| --- | --- |
| Android phone | `da179a64cc17786684b605d7a1341dd34a8aa4c17df3384bcf0b5aeec8a5df78` |
| Wear OS | `ac592ced0768efcd750efd2e443fc752b023df5aa7901313538870f1f4f6d019` |
| Apple IPA | `4811f81bc0bc0baa70843061cbb03d0ff0d27e7181b7a2019ea23942d9fe6eb1` |

Signed Actions artifact `9993782037` is 58,793,419 bytes and matches API ZIP
SHA-256 `9b207ba64075953da19cd81c985e7c3ec89acbc1a033911cb0ba702311f68ced`.
Local download independently matched that size and digest; its two regular ZIP
entries were validated before extraction.

| Retained file | Bytes | SHA-256 |
| --- | ---: | --- |
| signed-candidate-bytes.tar.gz | 59,062,201 | `1465c62400d2a791ecd82ec14bfc6ff216b7b84ab44382be8161d5d7a05df463` |
| signed-candidate-receipt.json | 11,723 | `1ceff60fb22b813b86e27ffcc478848a008740e502767461d501edff9df5729b` |

The package has 192 members (104 regular files, 88 directories), 154,585,534
expanded bytes, and closed-tree SHA-256
`15a4e8ebad89be8d8801373d473d287601142da7a3b03991aae8569bf573d207`.
The IPA is 23,007,065 bytes. App Mach-O/dSYM UUID is
`6811305B-6704-3E39-AE9A-0109C8A67F9F`; widget UUID is
`2D6B6F6C-4A3A-3C2E-9B08-8ADE9E6B5731`. Distribution signer, profiles,
App Group entitlements, archive/export parity and watch topology passed.

This receipt proves signed candidate identity. It does not prove TestFlight
upload, processing, natural widget refresh, review replacement or publication.
Current manifest slots remain blocked until independent trusted verification.
