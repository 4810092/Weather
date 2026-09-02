# Release candidate hosted materialization — 2026-09-02 — build 9

Status: **PASS for exact durable draft materialization; no store upload or
publication is claimed**.

Manual GitHub-hosted workflow
[`33626711140`](https://github.com/4810092/Weather/actions/runs/33626711140)
ran from `master` at
`de80135f8c89a79fc2432498fd7c2863a2bf318c`. The materialize job
`100236062688` ran from `2026-09-02T11:50:43Z` through `11:51:03Z` and
completed successfully.

The run admitted protected signing run `33616952267`, source revision
`052d12c7dfa6411428d85205d9568462d20ff87d`, and the exact candidate ZIP,
package, receipt, tree, and three signed artifact identities recorded in
[`signed-candidate-run-33616952267.md`](signed-candidate-run-33616952267.md).
It created one unpublished storage draft and uploaded only the expected package
and receipt.

## Durable draft locator

| Field | Verified value |
| --- | --- |
| Repository | `4810092/Weather` (`1329018769`) |
| Draft release ID | `381212810` |
| Draft storage name | `[DRAFT STORAGE] Nimbo 1.1.0 signed candidate 052d12c` |
| Storage tag name | `nimbo-candidate-v1.1.0-052d12c-run-33616952267` |
| Target commit | `de80135f8c89a79fc2432498fd7c2863a2bf318c` |
| Release state | `draft=true`, `prerelease=true`, `published_at=null`, `immutable=false` |
| Git tag/ref | absent |
| Package asset | ID `541102822`, 58,208,833 bytes, `signed-candidate-bytes.tar.gz` |
| Package SHA-256 | `5b8186e0aaa1d1ba74d475ba462d545fe2f3da1a321f77fbab3f7663df021d64` |
| Receipt asset | ID `541102876`, 11,716 bytes, `signed-candidate-receipt.json` |
| Receipt SHA-256 | `51fc10894dc9c0ff99c528a9778b01e4f78cf8354a13ca300d449c9b8fca4072` |
| Candidate tree SHA-256 | `b69d7d124c8160ee2af68667ecbd74d2f90bf72cec77b06c4a80b7ad31e55f12` |

The package binds these exact store artifacts:

- Android phone `1.1.0 (11)`:
  `034aa0a732e0a671c341e6714162a2d22c95d06435aa327bd17b1d7b3da2f9ac`;
- Wear OS `1.1.0 (1000011)`:
  `48a713d298be12552f08995b7cff3166df0f4ab173c62612854598eb93dcab7a`;
- Apple app/widget/watch `1.1.0 (9)`:
  `a57674d7d467474a0697fb39c834a9829f53e68ddb9d4480168bf2dcf3f7ac29`.

The draft is durable but mutable. Every later use must revalidate the exact
release ID, asset IDs, sizes, hashes, tag absence, and live `master` binding.
The separate read-only protected macOS verifier remains the manifest-promotion
gate and is being rebound to these exact identifiers.

No TestFlight or Play upload, processing, installation, review, release,
publication, public availability, physical-device result, or Top-10 rank is
claimed by this materialization record.
