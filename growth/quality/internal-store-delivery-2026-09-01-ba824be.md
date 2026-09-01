# Replacement internal store delivery — 2026-09-01

Status: **HISTORICAL / PRODUCTION-INELIGIBLE**. The exact Apple, Android phone,
and Wear OS candidates reached their intended internal store channels. Both
Google Play Internal releases are active and tester-addressable. Apple build 7
completed processing, entered the internal TestFlight group as `Testing`, and
was installed from TestFlight on a physical iPhone 14 Pro. Its copied share
payload contained `0%%`, so the entire set was superseded by source `8fc43b4`.
No production change is claimed.

All times below are `Asia/Tashkent` (`UTC+05:00`). The observations come from
the authenticated Transporter and Google Play Console interfaces. Artifact
identity is bound to the protected hosted verification in
[release-artifact-full-verification-2026-09-01-hosted.md](release-artifact-full-verification-2026-09-01-hosted.md)
for product source revision
`ba824beae5e72653e42af2b8b78286f61415e3ab`.

## Apple / Transporter

- App: `Nimbo Weather`, Apple ID `6799886897`.
- Candidate: `1.1.0 (7)`, exact `Nimbo.ipa` SHA-256
  `b918a8d7fa66d1755ca05486ee02ffac6a73b96ddd72f681bd3f6bfb3108709d`.
- Transporter reported `Delivered` on `2026-09-01 12:49`.
- Transporter later reported `THE APP HAS FINISHED PROCESSING`. Authenticated
  App Store Connect then listed exact build ID
  `baf82ec3-33bc-4df5-898f-b95a5b85ad37` with upload status `Завершено`,
  TestFlight status `Готово к отправке`, and creation time
  `2026-09-01 12:49`.
- Build 7 is attached to the internal group. Two owner-controlled internal
  accounts were added; one invitation was accepted and build 7 reported
  `Testing`. No external group or Beta App Review submission was used.
- TestFlight installed exact `1.1.0 (7)` on the connected iPhone 14 Pro. Cold
  launch, live Tashkent forecast, Best Time, first-success tip, refresh, and the
  share sheet ran without a visible crash. Copied share content failed with
  `0%%`; see
  [testflight-ios-build7-smoke-2026-09-01.md](testflight-ios-build7-smoke-2026-09-01.md).

## Google Play / phone Internal

- Package: `uz.ganikhodjaev.weather`.
- Candidate: `1.1.0 (9)`, exact phone AAB SHA-256
  `0fd5ae542a71f8cccb1cbbd043ffef09df9f29a2c1c6642010cfcce579f00681`.
- Internal track ID: `4700083514281298386`; release sequence `4`.
- Play accepted the AAB as `9 (1.1.0)`, retained all previously supported
  device populations with zero unsupported devices, and reported the release
  `Доступен внутренним тестировщикам` at `2026-09-01 12:53`.
- Twelve localized release-note blocks were supplied from the validated store
  metadata. Play emitted only the non-blocking recommendation to provide
  native debug symbols; the verified ReTrace mapping remains embedded in the
  AAB.

## Google Play / Wear OS Internal

- Package: `uz.ganikhodjaev.weather`.
- Candidate: `1.1.0 (1000009)`, exact Wear AAB SHA-256
  `9ce725e755a09d783adacc1691d5e20a0773b88aa63e9365c00af50f51e6542c`.
- Wear OS Internal track ID: `4699242452771231163`; release sequence `4`.
- Play accepted the AAB as `1000009 (1.1.0)`, retained all `81` supported
  wearable devices with zero unsupported devices, and reported the release
  `Доступен внутренним тестировщикам` at `2026-09-01 12:55`.
- Twelve localized release-note blocks were supplied from the validated store
  metadata. Play emitted only the non-blocking deobfuscation-file
  recommendation; the Wear module does not enable R8/minification and has no
  mapping output.

## Boundary

Google Play production remains unchanged at the previously public versions.
Phone vc9 subsequently received the bounded Play-delivered physical API-25
launcher/runtime/widget pass recorded in
[play-delivered-android-vc9-smoke-2026-09-01.md](play-delivered-android-vc9-smoke-2026-09-01.md).
No physical tablet, paired Wear handoff, or post-delivery vitals exist. Apple
production was not submitted or changed. The build-7 iPhone result does not
prove iPad/widget/watch QA, crash resolution, production review, or public
availability, and its share defect makes it production-ineligible. None of
these internal states proves a Top-10 rank.
