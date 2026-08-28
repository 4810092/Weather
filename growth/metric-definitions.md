# Nimbo growth metric contract

Last reviewed: 2026-08-28. Operating timezone: `Asia/Tashkent`. Target market: Uzbekistan (`UZ`).

The machine-readable catalogue is [metric-catalog.json](metric-catalog.json). Weekly imports must preserve platform, storefront, acquisition source, device, app version, time window, and source path. Values from different scopes are not combined.

## Outcome and rank surfaces

- **Apple Weather chart rank** is the position in Apple's public UZ Top Free Weather feed (`genre=6001`), first item = rank 1. The feed is Apple-hosted but is a public observation rather than an App Store Connect metric. Absence means only `> observed_count`, never “unranked.”
- **Apple query position** is the order returned by Apple's public Search API with `country=uz`, `entity=software`, and a fixed limit. Apple documents that public API as a catalog search surface; it is not guaranteed to reproduce every device's personalized App Store UI.
- **Google category/query position** is the first occurrence of a unique package ID in public logged-out Google Play HTML with fixed `gl=UZ`, language, user agent, and no cookie jar. Google states that results can vary by device, location, carrier, compatibility, and personalization. It is an auditable public-surface observation, not an official Google rank.
- A **complete Top-10 day** requires Apple Weather rank 10 or better, Google Weather category position 10 or better in all three fixed profiles, and at least two distinct generic queries in the top 10 on at least two Google profiles. A failed or incomplete fetch is `unknown` and breaks, rather than advances, the seven-day streak.

## Acquisition and engagement

- Apple's official **Conversion Rate** is total downloads and eligible pre-orders divided by unique device impressions. It cannot be reproduced from first-time downloads and total impressions. See [Apple metric definitions](https://developer.apple.com/help/app-store-connect-analytics/reference/metrics-definitions/).
- Google's current store-listing funnel uses **store-listing visitors**, **unique user install clicks**, and click-through rate. The imported Nimbo KPI is install clicks divided by visitors for the same dimensions. See [Google Play user-base metrics](https://support.google.com/googleplay/android-developer/answer/9859173).
- **First-launch rate** uses unique first launches divided by completed new installations from the same platform, population, and window. If the stores do not expose comparable values, the KPI is `unknown`; downloads, clicks, and installations are not interchangeable.
- **D7 retention** uses a day-7 returning numerator and the matching eligible cohort. Apple opt-in usage data and Google user data may represent different populations, so each platform is evaluated separately.
- **DAU/MAU** uses average daily active users/devices over 30 complete days divided by active users/devices over that same 30-day population. Do not average pre-computed percentages across countries or versions.

## Quality and guardrails

- iOS crash data in App Store Connect covers users who opted in to share diagnostics. Apple's `Crashes` is a crash count; it does not define crash-free sessions. The 99.8% guardrail therefore requires a direct source-defined crash-free-session metric. See [Apple app usage](https://developer.apple.com/help/app-store-connect-analytics/engagement/app-usage/).
- Android vitals user-perceived rates are percentages of daily active users who experienced at least one issue. Current bad-behavior thresholds are: overall crash `<1.09%`, overall ANR `<0.47%`, phone-model crash/ANR `<8%`, watch-model crash `<4%`, and watch-model ANR `<5%`. See [Android vitals](https://developer.android.com/games/optimize/vitals).
- Google **User loss** counts users who uninstalled from all devices or became inactive for more than 30 days. A percentage is evaluated only when the same denominator definition is recorded for every compared period. See [Google Play statistics](https://support.google.com/googleplay/android-developer/answer/139628).
- Low-volume console data can be thresholded or omitted. Missing usage rows are not zeros. Apple documents privacy thresholds and statistical noise for analytics reports in [Analytics Reports](https://developer.apple.com/help/app-store-connect-analytics/overview/analytics-reports-api).

## Baseline caveat

The [2026-08-28 baseline](baseline/2026-08-28.json) is a reported console readout without raw exports or dimension breakdowns. Its reported conversion rates are preserved but cannot be recomputed from the supplied counts. The weekly import path establishes the reproducible series going forward.
