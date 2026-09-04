# Trusted hosted build-10 release verification — 2026-09-04

Status: **PASS for the protected hosted byte-verification boundary**.

This record authorizes the atomic manifest promotion of the coordinated Nimbo
`1.1.0` successor set. It does not close TestFlight/device runtime, crash,
review, production, publication, or ranking gates.

## Trusted invocation

The final pre-upload verification was
[run `33859392482`](https://github.com/4810092/Weather/actions/runs/33859392482),
attempt 1, `workflow_dispatch` on exact master
`d7dbdc3e42d93d2fe1a15219cfb51aba1ba7dd6e`; it completed successfully from
`2026-09-04T09:39:05Z` through `2026-09-04T09:40:21Z`. The no-checkout
`stage` job `100980097865` and separate read-only macOS `verify` job
`100980159491` both passed, including full signed-byte verification and the
final live-master/staged-file revalidation. Its retained receipt is GitHub
artifact `9931523244`; the staged candidate is artifact `9931493836`.

The earlier successful run below was the promotion-authorizing verification;
the final run repeated the complete boundary after the manifest and gate
correction was committed:

- Repository: `4810092/Weather`, repository ID `1329018769`.
- Manual-only trusted workflow:
  [run `33857134803`](https://github.com/4810092/Weather/actions/runs/33857134803),
  attempt 1, `workflow_dispatch` on `master` at workflow authority
  `d34a0a8027fa2689cf0c0cd1cf8927d3809ac707`; completed successfully from
  `2026-09-04T09:11:51Z` through `2026-09-04T09:13:14Z`.
- The no-checkout Ubuntu `stage` job `100972940025` passed. The separate
  read-only macOS `verify` job `100973009660` rechecked live `master`, the
  fixed unpublished release and asset endpoints, safe extraction, pinned
  Bundletool, the exact ephemeral manifest, all three complete signed-byte
  identities, and final source/staged-file integrity before emitting a
  non-secret receipt.

## Mutable draft rechecked

The workflow checked unpublished draft release `382592451` before and after
download. It remained `draft=true`, `prerelease=true`, `published_at=null`,
and targeted materialization commit
`ebe60d1b43c687fcb08c5c762cdcc9e772e6c1ce`. Its logical tag
`nimbo-candidate-v1.1.0-fc4b6de-run-33852229166` did not resolve to a Git ref.
The release contained exactly these two uploaded assets:

| Asset | ID | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `signed-candidate-bytes.tar.gz` | `544061853` | 58,216,629 | `76883f1cef5838b3ad8c9509f8098821bb1c6665a649cbfddb563f25f0ecb254` |
| `signed-candidate-receipt.json` | `544061890` | 11,723 | `f0f65eed8d4fd502e2d1bcc71836e8d3bb8f737dadf6764824b1575e03965b32` |

## Exact artifact result

The complete verifier returned `source_sync=verified-current` and
`byte_verified=true` for all three coordinated artifacts from product source
revision `fc4b6de9e28fd8956eb64462294b8bcdf405ce7e`:

| Surface | Identity | SHA-256 | Verified identity |
| --- | --- | --- | --- |
| Android phone | `1.1.0 (11)` | `52e924d4ce5dba7370007632b9e421aa548af79b6395ba4b6b0ee1645daf6862` | package `uz.ganikhodjaev.weather`, upload certificate `431548a4871c9c090eee808ac3a34898f5d78602d9e747dfe81e228415aac252` |
| Wear OS | `1.1.0 (1000011)` | `0bb295d2898a0cfcaff018ec43bc0d70663d1529771087cb48a0d7dd1b3c77a8` | package `uz.ganikhodjaev.weather`, same upload certificate |
| Apple app/widget/watch | `1.1.0 (10)` | `20e8e4ac61c55d856aedcdf88a27a2f11ac4cb036aa2dfa002e729ace1986061` | team `5SWEZ7HTYP`, distribution certificate `fd4d8668a7e0f4eb9f64a12b5f0ddec0075ccde31dad50a96e978926e0e743f1`, matching profiles/source revisions and UUIDs; app UUID `64AFA35C-03B1-3981-87E8-0D9B8881BB9E` |

Bundletool `1.18.3` was pinned by SHA-256
`a099cfa1543f55593bc2ed16a70a7c67fe54b1747bb7301f37fdfd6d91028e29`.

The non-secret receipt is GitHub artifact `9930661493`, named
`trusted-release-verification-d34a0a8027fa2689cf0c0cd1cf8927d3809ac707`,
1,747 bytes, with GitHub artifact digest
`3cc03c8d32d6497edbe8eb7c7d1d8d4d42b3c25a96bf13ed1d0fc63f1017a50c`.
Its sole file, `trusted-release-verification.json`, is 8,285 bytes with SHA-256
`1bc189aa2eb93f58a82723ebe1d4cb7cde1cb16ac4bea5418bea36f4a8a04e11`;
a checked-in copy is retained under
[`receipts/trusted-release-verification-33857134803.json`](receipts/trusted-release-verification-33857134803.json).

The one-day staged-candidate artifact is `9930629026`, named
`trusted-candidate-stage-d34a0a8027fa2689cf0c0cd1cf8927d3809ac707`,
58,228,674 bytes, with digest
`387fefe99e22fab2d87f2457b990e334c58c7d00235e7cb4491b9fedea9e61a1`.
The durable source remains the unpublished draft asset above.

The final run's non-secret receipt artifact is named
`trusted-release-verification-d7dbdc3e42d93d2fe1a15219cfb51aba1ba7dd6e`,
is 1,746 bytes, and has GitHub artifact digest
`9e1bd6b6a0879a955755699b58bee966457933bc122c1a131884f8a8d2563ec6`.
Its sole JSON file has SHA-256
`c6a62a36c3164397134b44cb512a1780567700396df978294452055bd91a9046`;
a checked-in copy is retained under
[`receipts/trusted-release-verification-33859392482.json`](receipts/trusted-release-verification-33859392482.json).
The final staged candidate artifact is 58,228,674 bytes with GitHub artifact
digest `276070d0bd44ee497c95e0cbc7739a9ddfdaa3c80231e759a4ca39acad08ccc6`.

## No-deployment and runtime boundary

The final related Pages run `33859495781` completed `skipped`; both `build`
and `deploy` jobs had zero executed steps. The Deployments API returned no
deployment for exact workflow SHA `d7dbdc3e`. The earlier related Pages run
`33857253805` also completed `skipped`; both `build`
(`100973310215`) and `deploy` (`100973310454`) had zero executed steps. The
Deployments API returned no deployment for workflow SHA `d34a0a8`. Trusted
verification therefore did not publish the website or a store release.

The upload manifest remains top-level `draft-blocked`. The exact bytes are now
atomically `3/3 verified-current`. Apple build 10 was subsequently uploaded,
processed by App Store Connect, and attached to the internal TestFlight group;
that later provider state is recorded separately and is not a consequence of
this verifier. Bounded build-10 smoke and an iPad widget render are recorded
separately; the natural OS-scheduled background completion and its fresh
crash-log window remain incomplete. Build 9 remains runtime-failed and must not
be released. Every
later use must repeat the protected recheck because the draft storage is
mutable.
