# Trusted hosted release verification — 2026-08-31

Status: **PASS for the protected hosted byte-verification boundary**.

This record closes the previously pending hosted repeat of the local full
verification. It does not close physical-device, store-delivery, crash, review,
publication, or ranking gates.

## Trusted invocation

- Repository: `4810092/Weather`, repository ID `1329018769`.
- Source CI: run
  [`33404028777`](https://github.com/4810092/Weather/actions/runs/33404028777),
  successful `push` to `master` at
  `b07192e91ae7f0f56ac3db7240383d7c53b94a2c`.
- Trusted workflow: run
  [`33405849102`](https://github.com/4810092/Weather/actions/runs/33405849102),
  attempt 1, completed successfully at `2026-08-31T15:00:51Z`.
- The Ubuntu `stage` job completed without checking out repository code. The
  separate read-only macOS `verify` job validated the workflow-run binding,
  checked out the exact successful `master` SHA, revalidated verifier authority,
  safely extracted the staged closed package, fetched pinned Bundletool, and ran
  the full signed-byte verifier.

## Mutable draft rechecked

The workflow checked draft release `379745439` before and after download. It
remained unpublished, mutable, and contained exactly these two uploaded assets:

| Asset | ID | Size | SHA-256 |
| --- | ---: | ---: | --- |
| `signed-candidate-bytes.tar.gz` | `537966386` | 58,073,521 | `60c827ef9f5d2cdc51add5344bd33ab780ab1be3154a3f3da8c22074ddb518d9` |
| `signed-candidate-receipt.json` | `537966414` | 11,711 | `c852c61e07289d2a7a8f211efc91d7f30fab2c3475465ba000625780a21de19c` |

The draft tag remained unresolved, and live `master` did not change during the
staging or verification boundary.

## Exact artifact result

The full verifier returned `source_sync=verified-current` and
`byte_verified=true` for all three coordinated 1.1.0 artifacts from product
source revision `2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652`:

| Surface | Identity | SHA-256 | Verified identity |
| --- | --- | --- | --- |
| Android phone | `1.1.0 (8)` | `d4a90676f32745ea314b50ced2c9955e86923589534a1a7654ac6f1207e88a62` | package `uz.ganikhodjaev.weather`, upload certificate `431548a4871c9c090eee808ac3a34898f5d78602d9e747dfe81e228415aac252` |
| Wear OS | `1.1.0 (1000008)` | `e76d685b20e86f8878be7c9a1a59ac6edb5781ec8e61d5ecd36feb52ddc1cccf` | package `uz.ganikhodjaev.weather`, same upload certificate |
| Apple app/widget/watch | `1.1.0 (6)` | `7466afb1a06f3000ad5d095734082d57cf58e992bdd7a8bed326e90d26ba39d0` | team `5SWEZ7HTYP`, distribution certificate `fd4d8668a7e0f4eb9f64a12b5f0ddec0075ccde31dad50a96e978926e0e743f1`, matching profiles and dSYM UUIDs |

Bundletool `1.18.3` was pinned by SHA-256
`a099cfa1543f55593bc2ed16a70a7c67fe54b1747bb7301f37fdfd6d91028e29`.

The non-secret workflow receipt is artifact `9763131726`, named
`trusted-release-verification-b07192e91ae7f0f56ac3db7240383d7c53b94a2c`,
with GitHub artifact digest
`41e81e8c9f464dc2a0fe13c49697ae445285c77ef8e580f701fa29ad1ff74b3e`.
Its contained JSON has SHA-256
`3f95d48ae48c839bae602a184b972a2817a51e0c5abc7458d3ebb36aead0c5ac`.

## Boundary

The protected hosted repeat is complete. The exact draft remains mutable, so
every later use must still pass the protected chain against the live release and
asset identities. Standard GitHub-hosted runners remain the canonical CI path;
no self-hosted Mac runner is required.

The upload manifest remains `draft-blocked`. This pass does not claim a
TestFlight or Play upload, processing, internal installation, review,
publication, public availability, crash resolution, physical-device result, or
Top-10 rank.
