# UZ competitor ASO audit — 2026-08-29

Status: **bounded public-store evidence used to refine the unpublished UZ
listing draft**. Capture window: `2026-08-29 13:09–13:24 +05:00`. No store
listing, experiment, release, review, outreach message, or paid campaign was
created or changed.

## Decision

Keep the prepared Google Play UZ titles and strengthen the short descriptions
without losing the differentiated benefit:

- Uzbek audience: keep `Nimbo: Ob-havo va prognoz`; use the short copy
  `Toshkent va O‘zbekiston ob-havosi: chiqish uchun eng yaxshi vaqtni toping.`
- Russian audience: keep `Nimbo: Погода и прогноз`; change the short copy to
  `Прогноз погоды: найдите лучшее время, чтобы выйти на улицу.`

The titles and revised short descriptions cover the strongest truthful generic
and local term families without repeating both title terms in the Uzbek short
description. All three fixed Google profiles placed geographically named apps
first for `Toshkent ob-havo`, while Nimbo met no Top-10 quorum for that query.
The copy therefore adds truthful Tashkent and Uzbekistan context while retaining
the differentiated best-time-outside benefit. None of the inspected competitor
title, subtitle, or short-description surfaces used Nimbo's best-time-outside
or recent-weather-comparison proposition.

The UZ-targeted full descriptions were also refined. They now add natural,
truthful context for Tashkent and Uzbekistan, ordinary city search, the
10-day forecast, and air quality. They do not adopt `radar`, `storm alerts`,
`real-time`, or `accurate` claims because Nimbo does not provide evidence for
those claims.

## Observed recurring term families

The audit deduplicated apps within each public result universe before counting
term-family presence in visible titles and Google short descriptions.

| Surface | Apps inspected | Core weather term | Forecast term | Radar term |
| --- | ---: | ---: | ---: | ---: |
| Google `hl=uz&gl=UZ` | 21 | 20 | 17 | 11 |
| Google `hl=ru&gl=UZ` | 23 | 22 | 17 | 8 |
| Google `hl=en&gl=UZ` | 23 | 22 | 15 | 14 |

Other recurring families were `live` / real-time, local / Uzbekistan, then
storm, rain, alerts, and widgets. Apple supplied 26 unique visible titles:
`weather` appeared in 15, `radar` in 7, `live` in 6, and `forecast` in 5.
Eighteen of those 26 App Store detail pages returned a subtitle during the
bounded capture; eight were rate-limited with HTTP 429 and were not inferred.
Within the 18 returned subtitles, weather appeared in 9 and forecast in 5;
rain, storm, and tracker each appeared in 4.

Exact local phrasing had the clearest query-specific evidence:

- Apple `ob havo`: `Ob havo Uzbekistan` was #1.
- Google `ob havo`: `Ob-havo Uzbekistan 2026` was #1 in each fixed
  `uz-UZ`, `ru-UZ`, and `en-UZ` logged-out profile.
- `Kunlik ob-havo` was also visible near the top of those Google result sets.

These observations support retaining `Ob-havo` in the title. They do not prove
that metadata alone will produce a Top-10 position, and they do not justify
keyword stuffing or unsupported feature claims.

The same evidence supports keeping `Local forecast, made familiar` as the
English Apple subtitle and adding a Russian App Store override with title
`Nimbo: Погода и прогноз` and subtitle `Лучшее время для прогулки`. The Russian
override moves the absent-query terms `погода` and `прогноз` into the strongest
visible metadata field while preserving Nimbo's implemented, differentiated
Best Time Outside benefit. The candidate base keyword fields deliberately retain
`weather` / `forecast` and `погода` / `прогноз` because the prepared Custom
Product Page assignment contract requires every planned target to exist in the
approved base keyword pool. Both fields remain within Apple's 100-byte limit;
this explicit CPP gate takes precedence over the usual duplicate-term
optimization until the base version is approved and assignment is verified.

## Target-app position at the same capture

- App Store UZ Weather chart: below the observed top 100.
- App Store search: `weather` #81; absent from the observed results for
  `ob havo`, `погода`, and `prognoz`; the `Toshkent ob-havo` Apple result was
  incomplete because it returned only one unique app.
- Google UZ Weather category: below the observed top 30 in all three fixed
  profiles.
- Google generic query quorum: 0 of 5 queries met Top-10 on at least two fixed
  profiles.
- Simultaneous goal streak: `0/7` days.

## Sources and boundary

- Apple official public Weather chart:
  <https://itunes.apple.com/uz/rss/topfreeapplications/limit=100/genre=6001/json>
- Apple public Search API, country `UZ`, for the five fixed queries.
- Google Play public category and search HTML with `gl=UZ`, logged out, across
  fixed `hl=uz`, `hl=ru`, and `hl=en` profiles.
- Fresh rank-capture SHA-256:
  `6f079fdd2bab7c8eb38d251825d983c5697f6283cbdcfe0c3197f4d524b1c947`.
- Competitor detail-capture SHA-256:
  `6504b5af187e9ac1df1bdc27b4abd9a1f65880910137150cb8c015c571e7a523`.
- Apple metadata limits and keyword guidance:
  <https://developer.apple.com/help/app-store-connect/reference/app-information/app-information>
  and <https://developer.apple.com/app-store/product-page/>.
- Google listing limits and metadata guidance:
  <https://support.google.com/googleplay/android-developer/answer/9859152>,
  <https://support.google.com/googleplay/android-developer/answer/13393723>,
  and <https://support.google.com/googleplay/android-developer/answer/9898842>.

Google ordering may still vary by IP, compatibility, experiments, and
server-side behavior. Apple Search API order can differ from on-device search.
Rate-limited subtitles remain unknown rather than negative evidence.
