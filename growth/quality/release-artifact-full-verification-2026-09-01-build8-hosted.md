# Trusted hosted build-8 release verification — 2026-09-01

Status: **PASS for the protected hosted byte-verification boundary**.

This record authorizes the atomic manifest promotion of the coordinated Nimbo
`1.1.0` successor set. It does not close physical-device, internal-store
delivery, crash, review, production, publication, or ranking gates.

## Trusted invocation

- Repository: `4810092/Weather`, repository ID `1329018769`.
- Source CI: run
  [`33505490040`](https://github.com/4810092/Weather/actions/runs/33505490040),
  successful `push` to `master` at
  `96ea869d332f4dd9689321ac6935ebe313d0e6c0`.
- Trusted workflow: run
  [`33508130379`](https://github.com/4810092/Weather/actions/runs/33508130379),
  attempt 1, completed successfully at `2026-09-01T12:32:16Z`.
- The no-checkout Ubuntu `stage` job completed successfully. The separate
  read-only macOS `verify` job checked the workflow-run binding and live
  master, checked out the exact authority, downloaded only the same-run staged
  assets, validated the committed blocked manifest contract, created a
  mode-`0600` exact ephemeral verification manifest, safely extracted the
  closed package, fetched pinned Bundletool, ran the complete signed-byte
  verifier, and revalidated master plus staged-file identities before
  publishing a non-secret receipt.

## Mutable draft rechecked

The workflow checked draft release `380406897` before and after download. It
remained unpublished, mutable, and contained exactly these two assets:

| Asset | ID | Size | SHA-256 |
| --- | ---: | ---: | --- |
| `signed-candidate-bytes.tar.gz` | `539393445` | 58,205,143 | `cb26a7d69fd35676957a6bfa6984f148fbe874959c133c95029e0688132ee023` |
| `signed-candidate-receipt.json` | `539393546` | 11,716 | `090ece08e9ede31502532a9622875854f7936fdb0b84036055090d3c93c27d87` |

The draft remained `draft=true`, `prerelease=true`, `published_at=null`, and
`immutable=false`. Its target remained materialization merge
`e9dd7d1e0678e51412b3bc691fb1c1fc1851e7a8`; the draft tag did not resolve to
a Git ref. Live `master` did not change during staging or verification.

## Exact artifact result

The full verifier returned `source_sync=verified-current` and
`byte_verified=true` for all three coordinated artifacts from product source
revision `8fc43b48b65d17b3339663549cd86208f62f6bb7`:

| Surface | Identity | SHA-256 | Verified identity |
| --- | --- | --- | --- |
| Android phone | `1.1.0 (10)` | `c11bc62221c11a16b1d6614aae2060af60ca7b98ad989e68dc5f87c224bbcd89` | package `uz.ganikhodjaev.weather`, upload certificate `431548a4871c9c090eee808ac3a34898f5d78602d9e747dfe81e228415aac252` |
| Wear OS | `1.1.0 (1000010)` | `e66a9891f70c3d532de23430d176d8c77f2bf49de55a343a7541cf0b0f99f676` | package `uz.ganikhodjaev.weather`, same upload certificate |
| Apple app/widget/watch | `1.1.0 (8)` | `6aff05fc50a0e1546a196cc8f7f9139bfb87f8e89c0dcda7c91dc1ddb1defac4` | team `5SWEZ7HTYP`, distribution certificate `fd4d8668a7e0f4eb9f64a12b5f0ddec0075ccde31dad50a96e978926e0e743f1`, matching profiles, source revisions, architectures, and dSYM UUIDs |

Bundletool `1.18.3` was pinned by SHA-256
`a099cfa1543f55593bc2ed16a70a7c67fe54b1747bb7301f37fdfd6d91028e29`.

The non-secret workflow receipt is GitHub artifact `9800474843`, named
`trusted-release-verification-96ea869d332f4dd9689321ac6935ebe313d0e6c0`,
with GitHub artifact digest
`270bc029b5f83f5df4733dea713dda0e51a320c0c3869be1c5a351b524f4a7c1`.
Its contained `trusted-release-verification.json` is 8,212 bytes and has
SHA-256 `f0e8abb8261870e1ba95b504d88a6fcd5ea718a07a57455d6cc65167f0200319`.

## Retention and boundary

The same-run staged candidate artifact is `9800443626`, named
`trusted-candidate-stage-96ea869d332f4dd9689321ac6935ebe313d0e6c0`, and
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
