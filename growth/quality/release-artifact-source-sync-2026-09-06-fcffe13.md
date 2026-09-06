# Release artifact source transition — 2026-09-06 (`fcffe13`)

Status: **BLOCKED pending protected signing and independent byte verification**.

Product/build-input authority `fcffe13be1cc15e83a0609751f696e48c9301444`
contains the autonomous WidgetKit background URLSession refresh, versioned
App Group coordination, hourly cross-process attempt budget, and host cache
import. The build-10 Swift actor-isolation correction is retained. Apple is
`1.1.0 (11)`; Android phone and Wear source identities remain `1.1.0 (11)`
and `1.1.0 (1000011)`.

All three manifest entries move atomically to `blocked`, with null current
hashes and signing/runtime evidence. Previously signed build-10 source bytes
remain in exact `historical-superseded` records. No earlier device result is
transferred to this source.

Local implementation verification passed 318 test executions (37 Swift,
135 Android shared host, 123 shared iOS, 13 phone, 10 Wear), Kotlin lint,
SQLDelight migration validation, unsigned Release iOS/widget/watch builds,
and a 20-process atomic-claim race probe. The successor build-number change
requires canonical Apple verification before protected signing.

The owner explicitly authorized TestFlight delivery on September 6. A live
App Store Connect read found build 10 as the latest TestFlight upload and
App Store 1.1.0 (10) in `Pending Developer Release`, with manual release
selected. This transition preserves that submission and authorizes no public
release, review replacement, Android delivery, or Pages publication.

Protected signing run `34047427535` has now passed for this exact source.
Candidate hashes are phone `da179a64cc17786684b605d7a1341dd34a8aa4c17df3384bcf0b5aeec8a5df78`,
Wear `ac592ced0768efcd750efd2e443fc752b023df5aa7901313538870f1f4f6d019`,
and Apple `4811f81bc0bc0baa70843061cbb03d0ff0d27e7181b7a2019ea23942d9fe6eb1`.
The signed-candidate record and schema-v3 receipt are retained separately.
The manifest stays blocked until durable materialization and independent
trusted verification are complete.
