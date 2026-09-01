# Release candidate hosted materialization — 2026-09-01

Status: **PASS for exact durable draft materialization; no store upload or
publication is claimed**.

Manual GitHub-hosted workflow
[`33477785531`](https://github.com/4810092/Weather/actions/runs/33477785531)
ran from `master` at
`594394736a2bc517e00a183cd30160c56199cff2`. It started at
`2026-09-01T06:29:01Z` and completed successfully at
`2026-09-01T06:29:25Z`.

The run admitted protected signing run `33473684554`, source revision
`ba824beae5e72653e42af2b8b78286f61415e3ab`, and the exact candidate ZIP,
package, receipt, tree, and three signed artifact identities recorded in
[`signed-candidate-run-33473684554.md`](signed-candidate-run-33473684554.md).
It created one unpublished storage draft and uploaded only the expected package
and receipt.

## Durable draft locator

| Field | Verified value |
| --- | --- |
| Repository | `4810092/Weather` (`1329018769`) |
| Draft release ID | `380257470` |
| Draft storage name | `[DRAFT STORAGE] Nimbo 1.1.0 signed candidate ba824be` |
| Storage tag name | `nimbo-candidate-v1.1.0-ba824be-run-33473684554` |
| Target commit | `594394736a2bc517e00a183cd30160c56199cff2` |
| Release state | `draft=true`, `prerelease=true`, `published_at=null`, `immutable=false` |
| Git tag/ref | absent |
| Package asset | ID `539108193`, 58,200,250 bytes, `signed-candidate-bytes.tar.gz` |
| Package SHA-256 | `448f2682c3fb2c2c186e0eebe794183d7cbd60e75312448dc9bae7ef608b8af3` |
| Receipt asset | ID `539108272`, 11,711 bytes, `signed-candidate-receipt.json` |
| Receipt SHA-256 | `27bebc799d936268ebd1669f732284318fb538019612305dfbaab7347b3902f1` |
| Candidate tree SHA-256 | `bcce519c01859e74b0dda904b817f626ce794ff6788aee2ab9fdcaca7c24f84e` |

The package binds these exact store artifacts:

- Android phone `1.1.0 (9)`:
  `0fd5ae542a71f8cccb1cbbd043ffef09df9f29a2c1c6642010cfcce579f00681`;
- Wear OS `1.1.0 (1000009)`:
  `9ce725e755a09d783adacc1691d5e20a0773b88aa63e9365c00af50f51e6542c`;
- Apple app/widget/watch `1.1.0 (7)`:
  `b918a8d7fa66d1755ca05486ee02ffac6a73b96ddd72f681bd3f6bfb3108709d`.

The draft is durable but mutable. Every later use must revalidate the exact
release ID, asset IDs, sizes, hashes, tag absence, and live `master` binding.
The separate protected macOS verifier remains the hosted promotion gate.

No TestFlight or Play upload, processing, installation, review, release,
publication, public availability, physical-device result, or Top-10 rank is
claimed by this materialization record.
