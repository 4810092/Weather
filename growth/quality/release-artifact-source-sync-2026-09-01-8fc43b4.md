# Release artifact/source sync — 2026-09-01 — 8fc43b4

Status: **BLOCKED. Source identity is current; signed bytes are 0/3**.

The authoritative product/build-input revision is
`8fc43b48b65d17b3339663549cd86208f62f6bb7`. It resolves to Android phone
`1.1.0 (10)`, Wear OS `1.1.0 (1000010)`, and Apple app/widget/watch
`1.1.0 (8)`.

This revision succeeds the exact build-7 TestFlight physical result recorded
in
[testflight-ios-build7-smoke-2026-09-01.md](testflight-ios-build7-smoke-2026-09-01.md).
It normalizes an escaped `%%` left in the iOS Compose-resource formatting path
before constructing the share payload and adds a regression test that requires
one literal percent sign, the localized store call to action, and the canonical
platform link. Targeted Android-host execution of
`StoreLinkProviderTest` passed on 2026-09-01. The release identities, including
the generated and source Apple project declarations, were then advanced
monotonically to phone vc10, Wear vc1000010, and Apple build 8.

No hosted CI run, protected signing receipt, signed artifact hash, independent
byte verification, internal-store delivery, or physical runtime result exists
yet for this revision. The exact verified vc9/vc1000009/build-7 artifacts remain
historical evidence and must not be relabeled as current. The upload manifest
therefore keeps every current SHA-256, signing evidence, and physical QA field
null with `source_sync=blocked` until a new protected candidate is produced and
independently verified.

Production remains unchanged. No upload, review, rollout, public availability,
crash-gate closure, or rank effect is claimed.
