# Public store deployment gap — 2026-08-29

Status: **candidate ASO package is prepared; the Google UZ listing is saved as
an unpublished draft whose Uzbek short description now trails the repository
candidate**.

The public Apple and Google product pages were checked read-only at
`2026-08-29 12:29:59 +05:00`. No console setting, listing, release, experiment,
or asset was changed. Public pages prove only what was visible at that capture;
they did not prove whether an unaddressable private custom page existed. A later
authenticated Console observation at `2026-08-29 13:59:40 +05:00` confirmed
Google listing `4834799756935529888` exists as `Draft` and remains unpublished.
Its existence is not evidence of review, publication, or end-user availability.

## App Store UZ

- The public default page reports `Nimbo Weather`, subtitle
  `Weather made familiar`, and public version `1.0.1`. The title still matches
  the repository draft. A later public-store audit refined the unpublished
  English subtitle to `Local forecast, made familiar`. The Russian App Store
  draft now overrides the title with `Nimbo: Погода и прогноз` and the subtitle
  with `Лучшее время для прогулки`; none of those revisions is proven public.
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
graphics are not public. They are now persisted in authenticated Console draft
`4834799756935529888`, targeted only to Uzbekistan at `100%`, with `en-US`
carrying the Uzbek fallback and `ru-RU` carrying the Russian payload. That
percentage is listing targeting, not release rollout. The visible public feature
graphic materially differs from all three versioned candidate graphics.

After the authenticated capture, the repository candidate was refined to
`Toshkent va O‘zbekiston ob-havosi: chiqish uchun eng yaxshi vaqtni toping.`
The Console Draft still contains the older Uzbek short description shown in the
table. This repository-only change is not evidence that the revised copy was
saved, submitted, reviewed, published, or made available to users.

Public evidence:
<https://play.google.com/store/apps/details?id=uz.ganikhodjaev.weather&hl=uz&gl=UZ>
and
<https://play.google.com/store/apps/details?id=uz.ganikhodjaev.weather&hl=ru&gl=UZ>.

## Decision

The Google UZ country listing exists as an unpublished Console draft with its
localized feature graphics and six captioned screenshot stories, but its Uzbek
short description must still be synchronized with the newer repository
candidate. Submission, review, publication, and end-user availability remain
pending. The public Apple page still trails the prepared English subtitle and
Russian query-first title/subtitle; the repository draft is not treated as
deployed growth progress.

Release upload and publication remain blocked by the crash, source-signed
artifact, and remaining physical-device gates. Open-Meteo clearance passes for
the exact unpaid, non-monetized organic-promotion scope; saving the Google
listing as a project-only draft did not cross the remaining gates. Google
Console is currently authenticated, while App Store Connect is not. The public
Apple page
still reports `1.0.1` and Google reports `1.0.2`; neither proves that the
repository's `1.1.0` candidate, revised copy, or creatives are deployed.
