# Build 11 hosted byte verification

Status: **PASS — signed artifact identity only**.

The trusted verification workflow run `34048714127` completed successfully at
workflow head `277f829f6003154541324941beffffba4c9df565`. It verified the
materialized draft `383662265`, produced from product source
`fcffe13be1cc15e83a0609751f696e48c9301444`, against protected signing run
`34047427535` and materialization run `34048604324`.

The independently checked bytes are:

| Artifact | Version | SHA-256 |
| --- | --- | --- |
| Phone AAB | `1.1.0 (11)` | `da179a64cc17786684b605d7a1341dd34a8aa4c17df3384bcf0b5aeec8a5df78` |
| Wear AAB | `1.1.0 (1000011)` | `ac592ced0768efcd750efd2e443fc752b023df5aa7901313538870f1f4f6d019` |
| Apple IPA | `1.1.0 (11)` | `4811f81bc0bc0baa70843061cbb03d0ff0d27e7181b7a2019ea23942d9fe6eb1` |

The machine-readable receipt is
[`trusted-release-verification-34048714127.json`](receipts/trusted-release-verification-34048714127.json).
This evidence does not establish App Store Connect processing, TestFlight
availability, review, production delivery, public availability, or runtime
behavior.
