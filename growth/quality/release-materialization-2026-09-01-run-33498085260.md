# Release candidate hosted materialization — 2026-09-01 — build 8

Status: **PASS for exact durable draft materialization; no store upload or
publication is claimed**.

Manual GitHub-hosted workflow
[`33498085260`](https://github.com/4810092/Weather/actions/runs/33498085260)
ran from `master` at
`e9dd7d1e0678e51412b3bc691fb1c1fc1851e7a8`. It started at
`2026-09-01T10:34:12Z`; the materialize job ran from `10:34:17Z` through
`10:34:36Z` and completed successfully.

The run admitted protected signing run `33493356066`, source revision
`8fc43b48b65d17b3339663549cd86208f62f6bb7`, and the exact candidate ZIP,
package, receipt, tree, and three signed artifact identities recorded in
[`signed-candidate-run-33493356066.md`](signed-candidate-run-33493356066.md).
It created one unpublished storage draft and uploaded only the expected package
and receipt.

## Durable draft locator

| Field | Verified value |
| --- | --- |
| Repository | `4810092/Weather` (`1329018769`) |
| Draft release ID | `380406897` |
| Draft storage name | `[DRAFT STORAGE] Nimbo 1.1.0 signed candidate 8fc43b4` |
| Storage tag name | `nimbo-candidate-v1.1.0-8fc43b4-run-33493356066` |
| Target commit | `e9dd7d1e0678e51412b3bc691fb1c1fc1851e7a8` |
| Release state | `draft=true`, `prerelease=true`, `published_at=null`, `immutable=false` |
| Git tag/ref | absent |
| Package asset | ID `539393445`, 58,205,143 bytes, `signed-candidate-bytes.tar.gz` |
| Package SHA-256 | `cb26a7d69fd35676957a6bfa6984f148fbe874959c133c95029e0688132ee023` |
| Receipt asset | ID `539393546`, 11,716 bytes, `signed-candidate-receipt.json` |
| Receipt SHA-256 | `090ece08e9ede31502532a9622875854f7936fdb0b84036055090d3c93c27d87` |
| Candidate tree SHA-256 | `98523eb7846aa96b27c72c641bb075c7070d8ccfa52d27f153b8641d7f788300` |

The package binds these exact store artifacts:

- Android phone `1.1.0 (10)`:
  `c11bc62221c11a16b1d6614aae2060af60ca7b98ad989e68dc5f87c224bbcd89`;
- Wear OS `1.1.0 (1000010)`:
  `e66a9891f70c3d532de23430d176d8c77f2bf49de55a343a7541cf0b0f99f676`;
- Apple app/widget/watch `1.1.0 (8)`:
  `6aff05fc50a0e1546a196cc8f7f9139bfb87f8e89c0dcda7c91dc1ddb1defac4`.

The draft is durable but mutable. Every later use must revalidate the exact
release ID, asset IDs, sizes, hashes, tag absence, and live `master` binding.
The separate read-only protected macOS verifier remains the manifest-promotion
gate and is being rebound to these exact identifiers.

No TestFlight or Play upload, processing, installation, review, release,
publication, public availability, physical-device result, or Top-10 rank is
claimed by this materialization record.
