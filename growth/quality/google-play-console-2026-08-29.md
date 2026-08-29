# Google Play Console evidence — 2026-08-29

Status: **authenticated read-only point-in-time observation** for Nimbo
(`uz.ganikhodjaev.weather`). The capture was completed at
`2026-08-29 08:41:37 +05:00` (`2026-08-29T03:41:37Z`). No Console setting,
release, rollout, policy declaration, review response, report, or export was
created or changed.

## Current production and publishing state

- The phone production track is `Active` with latest release
  `Nimbo 1.0.2 (6)` and rollout `100%` across 177 countries/regions.
- Play Console displayed the release timestamp as `13 Aug 03:56`; the page did
  not expose a timezone for that timestamp.
- The production-track summary displayed `4` installations. This track-summary
  count is not the same metric or time window as the 28-day acquisition count
  below and must not be reconciled by assumption.
- Both the app dashboard and the testing-and-release overview explicitly said
  that there were no unpublished changes.
- The publishing overview showed managed publishing as off and the latest
  publication date as `2026-08-27`.

## Policy state

The policy-status page explicitly reported `No issues found` / `Проблем не
найдено`. This is a mutable Console observation at the capture timestamp, not
evidence that no future review or policy action can occur.

## Acquisition summary

The acquisition overview used unit `Device` and the visible preset
`Last 28 days`. The page did not expose explicit start and end dates in its URL
or visible content, so this evidence preserves the preset label and does not
silently assign calendar endpoints.

| Funnel stage | Console metric and definition | Visible value |
| --- | --- | ---: |
| Reach | `Device impressions`; device is the selected reporting unit | 779 |
| Acquire | `Installs`; device is the selected reporting unit | 21 |
| Activate | `First opens (devices)`: devices on which the app was first launched within 180 days after a first or repeat installation | 14 |
| Engage | `Monthly active devices`: devices on which the app was launched at least once during the preceding 28 days | 11 (`+38%`) |
| Retain | `Device retention (day 7)` | unavailable |

The same overview displayed standard store-listing conversion as `40.82%`.
The capture did not expose that card's numerator and denominator, so the value
is preserved as a Console summary and is not recomputed from the other cards.

## Rating-age boundary

A second authenticated read-only check completed at `2026-08-29 12:16 +05:00`.
Ratings Overview still reported a global default rating of `1.000` from one
user. The all-time reviews page reported zero ratings with written reviews, and
the rating breakdown showed no matching record for the most recent 90 days.
This supports only the bounded conclusion that the lone rating is not a new
textual defect report. The Console surface did not expose its date, app version,
device, country, or storefront, so it must not be attributed to Uzbekistan or
to the current public build.

## Engagement detail and data lag

The detailed Statistics URLs explicitly carried
`dateRange=2026_8_1-2026_8_28`, dimension `Country/region`, and included the
`Overall` series. The latest shared complete row visible for all three metrics
below was `2026-08-20`, not the end of the selected range:

| Metric | Console definition | Overall value on 2026-08-20 |
| --- | --- | ---: |
| DAU | Users who launched the app on the specified day | 5 |
| MAU | Users who launched the app at least once during the preceding 28 days | 11 |
| DAU/MAU | Daily ratio of DAU to MAU | 45.45% |

The arithmetic is internally consistent for that row: `5 / 11 = 45.45%`
after rounding. It is a dated daily observation, not an average over the
28-day report range. The separate first-open-by-user report warned that some
data was currently unavailable, so its partial rows are not promoted to an
authoritative period total here.

## Crashes, ANRs, and retention remain unknown

For production version code `6`, the release page linked 28-day
`USER_PERCEIVED_CRASHES` and `USER_PERCEIVED_ANRS` metrics. Both displayed
`-` and `Data unavailable`; the most-common-issues table displayed `No data`.
The separate crash/ANR issues page showed the range `2026-08-01` through
`2026-08-29` with active-mode crash and ANR types selected and no visible issue
rows.

These observations do **not** prove zero crashes or zero ANRs. Missing rates,
an empty issue list, and `No data` remain unavailable evidence rather than a
numeric zero. Device D7 retention is likewise unavailable and cannot be graded
pass or fail.

## 13:12 refresh and technical-quality recommendations

An authenticated read-only refresh at `2026-08-29 13:12 +05:00` confirmed
that production remained `Active` at `Nimbo 1.0.2 (6)`, with no unpublished or
under-review changes and no policy issues. Ratings remained `1.000` from one
user. Android Vitals still did not expose a numeric crash or ANR rate, so the
quality guardrails remain unknown rather than zero.

Play displayed three recommendations against the processed public build:

1. update an outdated `androidx.fragment` version;
2. improve edge-to-edge coverage;
3. remove unsupported edge-to-edge APIs or parameters.

No additional runtime patch is justified in the current `1.1.0 (8)` source:

- the exact-current dependency graph resolves `androidx.fragment:fragment` to
  stable `1.9.0`; older `1.0.0` / `1.1.0` requests are transitive and resolve
  to that override, and the exact-current AAB contains the `1.9.0` marker;
- phone compileSdk/targetSdk are 36, `enableEdgeToEdge()` runs before content,
  `adjustResize` is declared, and the root content applies
  `WindowInsets.safeDrawing` on all sides;
- app-owned themes no longer set deprecated status/navigation bar colors;
  remaining system-bar compatibility calls in DEX belong to stable AndroidX
  Activity `1.13.0`, while `isNavigationBarContrastEnforced=false` is an
  officially documented three-button-navigation path.

The recommendation cards therefore remain **open until Google Play processes
version code 8**. If any card survives that upload, its expanded origin must be
captured before changing code. A library-owned compatibility call is not by
itself a reason to replace the current supported edge-to-edge implementation
with manual deprecated APIs.

Implementation references:

- `gradle/libs.versions.toml`
- `app/src/main/java/uz/ganikhodjaev/weather/MainActivity.kt`
- `app/src/main/AndroidManifest.xml`
- `shared/src/commonMain/kotlin/uz/ganikhodjaev/weather/shared/ui/WeatherScreen.kt`
- <https://developer.android.com/jetpack/androidx/releases/fragment>
- <https://developer.android.com/develop/ui/compose/system/setup-e2e>
- <https://developer.android.com/jetpack/androidx/releases/activity>

## Evidence URLs

- Production:
  <https://play.google.com/console/u/0/developers/5513021445726079938/app/4975846491997599461/tracks/production?releaseType=defaultReleases>
- Testing and release overview:
  <https://play.google.com/console/u/0/developers/5513021445726079938/app/4975846491997599461/test-and-release>
- Publishing overview:
  <https://play.google.com/console/u/0/developers/5513021445726079938/app/4975846491997599461/publishing>
- Policy status:
  <https://play.google.com/console/u/0/developers/5513021445726079938/app/4975846491997599461/policy-center>
- Acquisition overview:
  <https://play.google.com/console/u/0/developers/5513021445726079938/app/4975846491997599461/grow-overview>
- Statistics:
  <https://play.google.com/console/u/0/developers/5513021445726079938/app/4975846491997599461/statistics>
- Crash and ANR issues:
  <https://play.google.com/console/u/0/developers/5513021445726079938/app/4975846491997599461/vitals/crashes>

## Importer boundary

This file is not a seven-day importer dataset. It combines point-in-time
Console state, a `Last 28 days` acquisition preset without exposed calendar
endpoints, daily engagement rows with reporting lag, and unavailable quality
metrics. It contains no complete seven-day record envelope, daily source rows,
required scope set, or normalized importer schema. It therefore must not be
used to populate weekly actuals, infer missing days, or turn D7/crash/ANR
guardrails into `PASS`, `FAIL`, or numeric zero.
