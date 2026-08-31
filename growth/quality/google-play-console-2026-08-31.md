# Google Play Console recheck — 2026-08-31

Status: **PARTIAL CURRENT EVIDENCE**. This authenticated, read-only recheck
records current aggregate dashboard values, the Publishing review state, and
both Internal tracks. It does not prove public propagation, a Play-delivered
installation, Uzbekistan-only conversion, retention, or Android vitals.

Observed at `2026-08-31 23:17–23:23` Asia/Tashkent in the `Khasan
Ganikhodjaev` developer account for package `uz.ganikhodjaev.weather`.

## Global dashboard aggregates

The dashboard labels its scope as the last 28 days compared with the preceding
28 days and reports:

| Metric | Value | Boundary |
| --- | ---: | --- |
| Installs | 25 | Global dashboard aggregate, not UZ-only |
| First launches by device | 18 | Global dashboard aggregate |
| Monthly active devices | 13 | Device count, not a retention cohort |

The directional `18 / 25 = 72%` ratio is not promoted to a decision-eligible
first-launch rate because the UI does not prove identical populations. The
previously reported 779 impressions and 40.82% listing conversion were not
shown on this surface and remain carried forward where explicitly marked.

## Publishing review

- Publishing overview says changes are under review and managed publishing is
  off.
- Review history request `14` is displayed as submitted on `2026-08-31 14:41`
  and has status `На рассмотрении`.
- The request contains only Google Play store data for the Uzbekistan Custom
  Store Listing `4834799756935529888`:
  - `en-US`: `Nimbo: Ob-havo va prognoz`;
  - `ru-RU`: `Nimbo: Погода и прогноз`.
- The latest verified publication remains `2026-08-27`.

This proves submission for review, not approval, publication, propagation, or
rank impact.

## Phone Internal

- Track `4700083514281298386` is `Активно`.
- Release `Nimbo 1.1.0 (8) — UZ growth QA` is available to internal testers,
  with release time displayed as `2026-08-31 21:47`.
- Exactly one selected list is visible: the automatically created License
  testers list with four accounts.
- The join link exists, but invite acceptance and a Play-delivered installation
  remain unverified.

## Wear OS Internal

- Track `4699242452771231163` is `Неактивно`.
- Release `Nimbo Wear 1.1.0 (1000008) — UZ growth QA` is available to internal
  testers, with release time displayed as `2026-08-31 21:49`.
- Zero tester lists are selected. The existing four-account License testers
  list is visible but was not selected or saved during this read-only check.
- No Wear installation or paired-device run is claimed.

## Boundary

No production release, tester-permission change, invite acceptance, message,
spend, deletion, or other state-changing action was performed during this
recheck. The separate August 29 policy check remains the latest direct
no-policy-issues observation.
