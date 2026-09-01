# Google Play UZ public-listing propagation — 2026-09-01

Status: **NOT VERIFIED AS PROPAGATED**. The fixed logged-out Uzbekistan product
pages still expose the pre-review public listing, so review request `14` must
not be treated as approved, published, propagated, or rank-impacting.

Observed at `2026-09-01 00:27–00:29` Asia/Tashkent for package
`uz.ganikhodjaev.weather`. Both Google responses used the public product URL
with `gl=UZ`, no authenticated session, and locale-specific `hl` and
`Accept-Language` values. The raw HTML was retained only in a system temporary
directory; this repository records its aggregate fields, byte size, and SHA-256
without storing Google page markup or user data.

| Surface | Public title | Public description | Bytes | Response SHA-256 |
| --- | --- | --- | ---: | --- |
| `hl=uz&gl=UZ` | `Nimbo – Google Play ilovalari` | `Understand the hours ahead through weather you have recently felt.` | 1,189,169 | `9096475dd464bbb189f0d55b3cda43aba309f8e4f13e0b241de9acd731106e78` |
| `hl=ru&gl=UZ` | `Приложения в Google Play – Nimbo` | `Поймите погоду на ближайшие часы через знакомые недавние ощущения.` | 1,187,957 | `ec21c3258fe32d6ce593af9b78086248cba5397729918b9dbd5f04278e782355` |

The reviewed Uzbekistan Custom Store Listing is expected to expose
`Nimbo: Ob-havo va prognoz` for its en-US store data and
`Nimbo: Погода и прогноз` for ru-RU. Neither submitted title appears on the
corresponding fixed public UZ page. The Uzbek surface also continues to expose
the old English short description rather than
`Toshkent va O‘zbekiston ob-havosi: chiqish uchun eng yaxshi vaqtni toping.`,
which the authenticated review form exposes as the submitted en-US short
description for this Uzbekistan-only listing.

## 05:56 follow-up

A second logged-out request kept the same publication conclusion. The raw
responses were inspected in a temporary owner-local directory and removed
after the aggregate fields below were recorded.

| Surface | Public description still observed | Bytes | Response SHA-256 |
| --- | --- | ---: | --- |
| `hl=uz&gl=UZ` | `Understand the hours ahead through weather you have recently felt.` | 1,154,916 | `fe9942934799c28c11ddd3e144ea55731d72b0ac994e3000f729df862effc695` |
| `hl=ru&gl=UZ` | `Поймите погоду на ближайшие часы через знакомые недавние ощущения.` | 1,153,705 | `ae4fade130358eafd15072503c5695874de589faddc76c9426065782e9d95523` |

Neither reviewed title nor the exact reviewed Uzbek short description occurred
in the corresponding response. The fixed public App Store UZ response remained
254,400 bytes with title `Nimbo Weather` and SHA-256
`d9a7eae203000e1aaa450112aad5435cdd0c21b2d53db438d8aead8137b7764d`.
This follow-up is still public propagation evidence only.

For comparison, the fixed public App Store UZ page still exposes the intended
global name `Nimbo Weather`; its 254,400-byte response had SHA-256
`23935ffe454af1243e831a6c118860a177c083bb73f60c2e70f57014e2a60005`.
That comparison does not prove any Apple metadata submission or release.

## Boundary

This is a point-in-time, logged-out public propagation check. It proves that
the submitted Play titles were not observed on these two fixed UZ product-page
surfaces. It does not prove the current authenticated review state, every
Google experiment or compatible-device view, approval, rejection, future
propagation, installs, conversion, retention, or rank. The last authenticated
Console observation remains request `14` as `На рассмотрении`, with managed
publishing off and latest verified publication dated `2026-08-27`.
