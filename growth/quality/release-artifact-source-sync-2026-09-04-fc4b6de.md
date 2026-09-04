# Release artifact source transition — 2026-09-04 (`fc4b6de`)

Status: **DURABLY MATERIALIZED; BLOCKED pending independent trusted
verification**.

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

The upload manifest remains intentionally fail-closed:

- all three current artifact entries are `blocked` with no current SHA-256,
  signing evidence, or runtime evidence;
- the previously verified vc11, vc1000011, and Apple build-9 bytes are retained
  only as exact `historical-superseded` provenance;
- Apple build 9 is additionally runtime-failed by two UUID-matched TestFlight
  background-refresh crash reports and must remain unreleased;
- durable draft storage is mutable and has not yet passed the independent
  trusted verifier, so no current hash is promoted;
- no prior delivery, simulator, review, or runtime result is transferred to
  corrected source.

The three entries move together because the repository's release contract
forbids a mixed `verified-current`/`blocked` manifest. This signing checkpoint
does not withdraw Apple build 9, edit either Google Play Internal release,
submit production, or publish. Apple has approved build 9 into `Pending
Developer Release`; manual release has kept the crashed build unavailable.

Required next action: run the manual-only trusted verifier against exact draft
release `382592451` and assets `544061853`/`544061890`, with current-master
checks before and after. Apple additionally requires build-10 TestFlight
background/widget validation before its runtime and crash gates can be
reconsidered.
