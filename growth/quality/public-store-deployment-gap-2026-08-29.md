# Public store deployment gap — 2026-08-29

Status: **candidate ASO package is prepared but not public**.

The public Apple and Google product pages were checked read-only at
`2026-08-29 12:29:59 +05:00`. No console setting, listing, release, experiment,
or asset was changed. Public pages prove only what was visible at that capture;
they do not prove whether an unaddressable private custom page exists.

## App Store UZ

- The public default page reports `Nimbo Weather`, subtitle
  `Weather made familiar`, and public version `1.0.1`. The title still matches
  the repository draft. A later public-store audit refined the unpublished
  English subtitle to `Local forecast, made familiar` and the Russian subtitle
  to `Понятный прогноз погоды`; neither revision is proven public.
- The public model exposes one iPhone image at 1320×2868, one iPad image at
  2064×2752, and one Watch image at 416×496. It does not expose the prepared
  six-story captioned growth set.
- The repository's UZ-oriented Custom Product Page remains `draft`. Its Uzbek
  and Russian copy and localized creatives are not proven public, and keyword
  assignment remains blocked until the base `1.1.0` keywords are approved.

Public evidence:
<https://apps.apple.com/uz/app/nimbo-weather/id6799886897> and
<https://itunes.apple.com/lookup?id=6799886897&country=uz&lang=en_us>.

## Google Play UZ

| Locale slice | Public title | Public short description | Prepared country-listing gap |
| --- | --- | --- | --- |
| `hl=uz&gl=UZ` | `Nimbo` | `Understand the hours ahead through weather you have recently felt.` | `Nimbo: Ob-havo va prognoz`; `Ob-havo prognozi: tashqariga chiqish uchun eng yaxshi vaqtni toping.`; full Uzbek copy |
| `hl=ru&gl=UZ` | `Nimbo` | `Поймите погоду на ближайшие часы через знакомые недавние ощущения.` | `Nimbo: Погода и прогноз`; `Прогноз погоды: найдите лучшее время, чтобы выйти на улицу.`; UZ-targeted Russian copy |

The public page exposes five phone, four unique tablet, and one Wear creative.
The prepared six-story captioned UZ/RU sets and localized UZ/RU feature
graphics are not public. The visible public feature graphic materially differs
from all three versioned candidate graphics.

Public evidence:
<https://play.google.com/store/apps/details?id=uz.ganikhodjaev.weather&hl=uz&gl=UZ>
and
<https://play.google.com/store/apps/details?id=uz.ganikhodjaev.weather&hl=ru&gl=UZ>.

## Decision

The highest-impact unpublished ASO change is the Google UZ country listing,
followed by its localized feature graphics and the six captioned screenshot
stories on both stores. Apple default title/subtitle work is already live, so
re-submitting the same values is not treated as growth progress.

Upload and publication remain blocked by the provider, crash, source-signed
artifact, and remaining physical-device gates. Google Console is currently
authenticated, while App Store Connect is not. The public Apple page still
reports `1.0.1` and Google reports `1.0.2`; neither proves that the repository's
`1.1.0` candidate, revised copy, or creatives are deployed.
