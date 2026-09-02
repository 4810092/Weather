# Trusted hosted build-9 release verification — 2026-09-02

Status: **PASS for the protected hosted byte-verification boundary**.

This record authorizes the atomic manifest promotion of the coordinated Nimbo
`1.1.0` successor set. It does not close physical-device, internal-store
delivery, crash, review, production, publication, or ranking gates.

## Trusted invocation

- Repository: `4810092/Weather`, repository ID `1329018769`.
- Source CI: run
  [`33628011906`](https://github.com/4810092/Weather/actions/runs/33628011906),
  successful `push` to `master` at
  `cffb55ae6f52bb91893b398d3a9bfdad92a9d7ac`.
- Trusted workflow: run
  [`33629490609`](https://github.com/4810092/Weather/actions/runs/33629490609),
  attempt 1, completed successfully at `2026-09-02T12:22:59Z`.
- The no-checkout Ubuntu `stage` job completed successfully. The separate
  read-only macOS `verify` job checked the workflow-run binding and live
  master, checked out the exact authority, downloaded only the same-run staged
  assets, validated the committed blocked manifest contract, created a
  mode-`0600` exact ephemeral verification manifest, safely extracted the
  closed package, fetched pinned Bundletool, ran the complete signed-byte
  verifier, and revalidated master plus staged-file identities before
  publishing a non-secret receipt.

## Mutable draft rechecked

The workflow checked draft release `381212810` before and after download. It
remained unpublished, mutable, and contained exactly these two assets:

| Asset | ID | Size | SHA-256 |
| --- | ---: | ---: | --- |
| `signed-candidate-bytes.tar.gz` | `541102822` | 58,208,833 | `5b8186e0aaa1d1ba74d475ba462d545fe2f3da1a321f77fbab3f7663df021d64` |
| `signed-candidate-receipt.json` | `541102876` | 11,716 | `51fc10894dc9c0ff99c528a9778b01e4f78cf8354a13ca300d449c9b8fca4072` |

The draft remained `draft=true`, `prerelease=true`, and `published_at=null`.
Its target remained materialization authority
`de80135f8c89a79fc2432498fd7c2863a2bf318c`; the draft tag did not resolve to a
Git ref. Live `master` did not change during staging or verification.

## Exact artifact result

The full verifier returned `source_sync=verified-current` and
`byte_verified=true` for all three coordinated artifacts from product source
revision `052d12c7dfa6411428d85205d9568462d20ff87d`:

| Surface | Identity | SHA-256 | Verified identity |
| --- | --- | --- | --- |
| Android phone | `1.1.0 (11)` | `034aa0a732e0a671c341e6714162a2d22c95d06435aa327bd17b1d7b3da2f9ac` | package `uz.ganikhodjaev.weather`, upload certificate `431548a4871c9c090eee808ac3a34898f5d78602d9e747dfe81e228415aac252` |
| Wear OS | `1.1.0 (1000011)` | `48a713d298be12552f08995b7cff3166df0f4ab173c62612854598eb93dcab7a` | package `uz.ganikhodjaev.weather`, same upload certificate |
| Apple app/widget/watch | `1.1.0 (9)` | `a57674d7d467474a0697fb39c834a9829f53e68ddb9d4480168bf2dcf3f7ac29` | team `5SWEZ7HTYP`, distribution certificate `fd4d8668a7e0f4eb9f64a12b5f0ddec0075ccde31dad50a96e978926e0e743f1`, matching profiles, source revisions, architectures, and dSYM UUIDs |

Bundletool `1.18.3` was pinned by SHA-256
`a099cfa1543f55593bc2ed16a70a7c67fe54b1747bb7301f37fdfd6d91028e29`.

The non-secret workflow receipt is GitHub artifact `9846211373`, named
`trusted-release-verification-cffb55ae6f52bb91893b398d3a9bfdad92a9d7ac`,
with GitHub artifact digest
`9d6d2828ccca8ac78433fadb530642e6ad7b0d5806922c869347c52da5f8280b`.
Its contained `trusted-release-verification.json` is 8,212 bytes and has
SHA-256 `4a0d2723a4c086b2917774cdc4a3106e6244a2b1a380f8198b904142e5fe5470`.

## Retention and boundary

The same-run staged candidate artifact is `9846176479`, named
`trusted-candidate-stage-cffb55ae6f52bb91893b398d3a9bfdad92a9d7ac`, and
has one-day retention. It is not committed to Git. The durable source package
remains the unpublished draft asset above.

The protected hosted repeat is complete. The draft remains mutable, so every
later reuse must still pass the protected chain against live release and asset
identities. The trusted workflow accepts only the exact atomic `0/3 blocked`
pre-promotion state or the exact atomic `3/3 verified-current` post-promotion
state; partial or drifted states fail closed.

The upload manifest remains `draft-blocked`. This pass does not claim a
physical install, Play Internal or TestFlight delivery, production review or
rollout, public availability, crash resolution, or Top-10 rank.
