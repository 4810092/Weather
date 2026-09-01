# Current internal store delivery — 2026-09-01

Status: **PASS for the exact internal-store delivery boundary**. The coordinated
Nimbo `1.1.0` successor set reached its intended Google Play Internal and Apple
TestFlight internal channels. Production was not changed, and no public
availability or ranking effect is claimed.

All times below are `Asia/Tashkent` (`UTC+05:00`). Artifact identity is bound to
[release-artifact-full-verification-2026-09-01-build8-hosted.md](release-artifact-full-verification-2026-09-01-build8-hosted.md)
and product source revision
`8fc43b48b65d17b3339663549cd86208f62f6bb7`.

## Google Play / phone Internal

- Package: `uz.ganikhodjaev.weather`.
- Candidate: `1.1.0 (10)`, exact phone AAB SHA-256
  `c11bc62221c11a16b1d6614aae2060af60ca7b98ad989e68dc5f87c224bbcd89`.
- Internal track ID: `4700083514281298386`; release sequence `5`, titled
  `Nimbo 1.1.0 (10) — UZ growth QA`.
- Google Play accepted `10 (1.1.0)`, `minSdk=24`, `targetSdk=36`, retained every
  previously supported device population with zero unsupported devices, and
  reported `Доступен внутренним тестировщикам` at `2026-09-01 18:52`.
- English and Russian internal release notes accurately describe the
  duplicate-percent share fix. The previous vc9 bundle is excluded.

## Google Play / Wear OS Internal

- Package: `uz.ganikhodjaev.weather`.
- Candidate: `1.1.0 (1000010)`, exact Wear AAB SHA-256
  `e66a9891f70c3d532de23430d176d8c77f2bf49de55a343a7541cf0b0f99f676`.
- Wear OS Internal track ID: `4699242452771231163`; release sequence `5`,
  titled `Nimbo Wear 1.1.0 (1000010) — UZ growth QA`.
- Google Play accepted `1000010 (1.1.0)`, `minSdk=30`, `targetSdk=36`, retained
  all `81` supported wearable devices with zero unsupported devices, and
  reported `Доступен внутренним тестировщикам` at `2026-09-01 18:54`.
- The previous vc1000009 bundle is excluded.

## Apple / Transporter and TestFlight

- App: `Nimbo Weather`, Apple ID `6799886897`.
- Candidate: `1.1.0 (8)`, exact IPA SHA-256
  `6aff05fc50a0e1546a196cc8f7f9139bfb87f8e89c0dcda7c91dc1ddb1defac4`.
- Transporter reported `Delivered` at `2026-09-01 18:57`, then App Store
  Connect finished processing without an upload error.
- App Store Connect build ID:
  `9696b8c2-d076-4596-af20-b8a5214aaf01`. The upload status is `Завершено`;
  the TestFlight status is `Готово к отправке`.
- Build 8 is attached to the internal group `internal testers group`, which has
  two owner-controlled internal testers. The TestFlight client exposed an
  `Обновить` action for exact `1.1.0 (8)`, and the update was installed on the
  physical iPhone 14 Pro.

## Protected reuse check

Before these store uploads, post-promotion trusted workflow run
[`33514410839`](https://github.com/4810092/Weather/actions/runs/33514410839)
rechecked live master, the unpublished draft, both draft assets, and all three
exact artifacts. Its non-secret receipt is GitHub artifact `9803211883`; the
verifier returned `source_sync=verified-current` and `byte_verified=true` for
all three candidates.

## Boundary

The phone candidate received the bounded Play-delivered API-25 pass recorded in
[play-delivered-android-vc10-smoke-2026-09-01.md](play-delivered-android-vc10-smoke-2026-09-01.md).
The Apple candidate received the bounded TestFlight iPhone pass recorded in
[testflight-ios-build8-smoke-2026-09-01.md](testflight-ios-build8-smoke-2026-09-01.md).
No current physical Wear OS result, current iPad install, visible iOS widget
render/open, physical watch launch, post-delivery vitals, production submission,
review, public propagation, or Top-10 rank is proved.
