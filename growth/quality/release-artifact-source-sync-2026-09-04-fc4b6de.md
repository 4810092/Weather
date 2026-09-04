# Release artifact source transition — 2026-09-04 (`fc4b6de`)

Status: **BLOCKED — corrected source has no signed current artifact set**.

Product/build-input authority
`fc4b6de9e28fd8956eb64462294b8bcdf405ce7e` contains the Swift 6
background-refresh actor-isolation correction and advances Apple to
`1.1.0 (10)`. Android source identities remain phone `1.1.0 (11)` and Wear OS
`1.1.0 (1000011)`; no Android product code changed in this transition.

The upload manifest is intentionally fail-closed:

- all three current artifact entries are `blocked` with no current SHA-256,
  signing evidence, or runtime evidence;
- the previously verified vc11, vc1000011, and Apple build-9 bytes are retained
  only as exact `historical-superseded` provenance;
- Apple build 9 is additionally runtime-failed by two UUID-matched TestFlight
  background-refresh crash reports and must remain unreleased;
- no prior signing, byte verification, delivery, simulator, review, or runtime
  result is transferred to corrected source.

The three entries move together because the repository's release contract
forbids a mixed `verified-current`/`blocked` manifest. This local transition
does not withdraw Apple build 9, change its review state, edit either Google
Play Internal release, submit production, publish, or dispatch hosted signing.

A later candidate may become current only after protected signing and
independent full-byte verification against exact source
`fc4b6de9e28fd8956eb64462294b8bcdf405ce7e`. Apple additionally requires a
monotonically newer build and TestFlight background/widget validation before
its runtime and crash gates can be reconsidered.
