# Google Play current-candidate internal delivery — 2026-09-03

Status: **PASS for exact Google Play Internal delivery only**. Production,
public availability, post-delivery Vitals, review, propagation, and ranking
impact are not claimed.

All times below are `Asia/Tashkent` (`UTC+05:00`). The delivered candidates are
bound to source authority `052d12c7dfa6411428d85205d9568462d20ff87d`,
protected signing run `33616952267`, materialization run `33626711140`, draft
release `381212810`, and the current trusted signed-byte verification chain.

## Phone Internal

- Package: `uz.ganikhodjaev.weather`.
- Exact AAB: `1.1.0 (11)`, SHA-256
  `034aa0a732e0a671c341e6714162a2d22c95d06435aa327bd17b1d7b3da2f9ac`.
- Internal track ID: `4700083514281298386`; release sequence `6`, titled
  `Nimbo 1.1.0 (11) — UZ growth QA`.
- Google Play accepted `11 (1.1.0)`, `minSdk=24`, `targetSdk=36`, and retained
  every previously supported device population with zero newly unsupported
  devices: 12,477 phones, 6,690 tablets, 7 TVs, 25 automotive devices, 72
  Chromebooks, and 1 Android XR device.
- The release reported `Доступен внутренним тестировщикам` at
  `2026-09-03 15:06`; prior vc10 was excluded.
- Play Console showed one non-blocking recommendation to attach native debug
  symbols. No artifact substitution or gate waiver was made.

## Wear OS Internal

- Package: `uz.ganikhodjaev.weather`.
- Exact AAB: `1.1.0 (1000011)`, SHA-256
  `48a713d298be12552f08995b7cff3166df0f4ab173c62612854598eb93dcab7a`.
- Wear OS Internal track ID: `4699242452771231163`; release sequence `6`,
  titled `Nimbo Wear 1.1.0 (1000011) — UZ growth QA`.
- Google Play accepted `1000011 (1.1.0)`, `minSdk=30`, `targetSdk=36`, and
  retained all 81 supported wearable devices with zero newly unsupported
  devices.
- The release reported `Доступен внутренним тестировщикам` at
  `2026-09-03 15:08`; prior vc1000010 was excluded.
- Play Console showed one non-blocking recommendation to attach a
  deobfuscation file. No artifact substitution or gate waiver was made.

## Boundary and next evidence

The two exact source-current candidates are available to their existing
internal testers. Phone and Wear production remain on `1.0.2 (6)` and
`1.0.2 (1000007)` respectively; no production track was edited. This closes
only the current-candidate Internal delivery boundary. Google Developer
Reporting needs a complete provider day after this delivery and a complete,
unambiguous UZ phone/Wear cohort before any post-delivery Vitals guardrail can
pass. Missing, suppressed, stale, pre-delivery, or ambiguous rows remain
`unknown` and block public release and acquisition scaling.
