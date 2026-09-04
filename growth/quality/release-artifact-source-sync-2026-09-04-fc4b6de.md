# Release artifact source transition — 2026-09-04 (`fc4b6de`)

Status: **PASS — atomically 3/3 signed, source-current, and independently
byte-verified**.

Product/build-input authority
`fc4b6de9e28fd8956eb64462294b8bcdf405ce7e` contains the Swift 6
background-refresh actor-isolation correction and advances Apple to
`1.1.0 (10)`. Android source identities remain phone `1.1.0 (11)` and Wear OS
`1.1.0 (1000011)`; no Android product code changed in this transition.

Protected GitHub Actions
[run `33852229166`](https://github.com/4810092/Weather/actions/runs/33852229166)
successfully signed and candidate-byte-verified the exact source-current set.
Its schema-v3 receipt binds phone SHA-256
`52e924d4ce5dba7370007632b9e421aa548af79b6395ba4b6b0ee1645daf6862`,
Wear SHA-256
`0bb295d2898a0cfcaff018ec43bc0d70663d1529771087cb48a0d7dd1b3c77a8`,
and Apple build-10 IPA SHA-256
`20e8e4ac61c55d856aedcdf88a27a2f11ac4cb036aa2dfa002e729ace1986061`.

Materialization
[run `33855931653`](https://github.com/4810092/Weather/actions/runs/33855931653)
then retained the exact package and receipt in unpublished draft release
`382592451`. Fixed assets `544061853` and `544061890` match package SHA-256
`76883f1cef5838b3ad8c9509f8098821bb1c6665a649cbfddb563f25f0ecb254`
and receipt SHA-256
`f0f65eed8d4fd502e2d1bcc71836e8d3bb8f737dadf6764824b1575e03965b32`.
The draft remains unpublished and its logical tag does not resolve as a Git
ref.

Manual-only trusted GitHub Actions
[run `33857134803`](https://github.com/4810092/Weather/actions/runs/33857134803),
attempt 1, independently reopened those fixed draft endpoints, safely extracted
the closed package, ran pinned Bundletool `1.18.3`, and passed the full verifier
for all three signed artifacts. The non-secret receipt is artifact `9930661493`
and is retained at
[`receipts/trusted-release-verification-33857134803.json`](receipts/trusted-release-verification-33857134803.json).

The upload manifest is now atomically source/byte current:

- all three current artifact entries are `verified-current`, carry the exact
  build-10 signing hashes above, and cite the same source-bound signing record;
- no historical candidate occupies a current slot;
- physical-QA evidence remains null for all three because the independent byte
  pass is not a runtime result;
- Apple build 9 is additionally runtime-failed by two UUID-matched TestFlight
  background-refresh crash reports and must remain unreleased;
- no prior delivery, simulator, review, or runtime result is transferred to
  corrected source, and build 10 is not yet uploaded to TestFlight.

The three entries move together because the repository's release contract
forbids a mixed `verified-current`/`blocked` manifest. This signing checkpoint
does not withdraw Apple build 9, edit either Google Play Internal release,
submit production, or publish. Apple has approved build 9 into `Pending
Developer Release`; manual release has kept the crashed build unavailable.

The related Pages run `33857253805` was skipped and no deployment exists for
the trusted workflow SHA. This promotion therefore proves only exact signed
bytes and source identity; it does not upload, submit, publish, or close any
runtime gate. Every later use must repeat the protected draft recheck. Apple
next requires build-10 TestFlight background/widget validation before its
runtime and crash gates can be reconsidered.
