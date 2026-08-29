# Weekly console evidence availability — 2026-08-29

Status: **BLOCKED — DO NOT IMPORT A WEEKLY CSV YET**.

The consoles were checked read-only between `2026-08-29 11:31` and `11:39
+05:00`. No store listing, release, event, report configuration, rating, or
policy state was changed.

## Google Play Console

The authenticated Nimbo Play Console was filtered to Uzbekistan. The candidate
`2026-08-22..2026-08-28` window is not decision-ready: different reports expose
different last available dates, and required acquisition, activation, and
quality values are missing or privacy-suppressed.

A conservative `2026-08-19..2026-08-25` inspection established these bounds:

- `Users with your app installed` contains one Uzbekistan user on each of the
  seven displayed days. This is the active installed-audience definition, not
  `google_installations`, and is therefore not substituted into the weekly KPI
  schema.
- new-user acquisition and legacy store-listing acquisition show `-`/no data;
  the missing values are not zero;
- first opens reports that some data is currently unavailable and exposes only
  suppressed rows;
- MAU exposes rows only for August 19 and 20, so it is not a complete weekly or
  30-day population;
- Android Vitals exposes no user-perceived crash or ANR value;
- Ratings Overview reports a global default rating of `1.000` from `1` user,
  but the inspected page does not prove that the rating belongs to storefront
  UZ, so it is not imported as a UZ rating;
- the monitoring overview reports no policy violations. This global
  point-in-time observation cannot by itself close the two-store app-global
  policy guardrail.

The aggregate installed-audience CSV is retained outside Git at
`../.nimbo-release/growth/console/2026-08-29/play-installed-users-uz-2026-08-19_25.csv`.
It contains no PII and has SHA-256
`dc07b1de33be37388023400c0b176f6dcda7604c9d9d8467c2b5a2be4e7d85f8`.

## App Store Connect

The Nimbo Analytics URL redirected to App Store Connect login with
`authResult=FAILED`. No password, passkey, or 2FA value was guessed or extracted.
No current Apple weekly aggregate was obtained, and older point-in-time console
observations were not relabelled as a complete UZ weekly slice.

## Import decision

No file was written to `growth/data/weekly/`. Import user metrics only after
both consoles expose the same seven complete days with explicit UZ filters and
source/device/version definitions. Suppressed, partial, or unavailable values
must remain absent rather than becoming zero. Policy status is instead an
app-global point-in-time value and must use storefront `ALL`; both
`apple_policy_issues` and `google_policy_issues` are required before the
combined critical policy guardrail may pass.
