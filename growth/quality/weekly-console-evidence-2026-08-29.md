# Weekly console evidence availability — 2026-08-29

Status: **BLOCKED — DO NOT IMPORT A WEEKLY CSV YET**.

The consoles were checked read-only between `2026-08-29 11:31` and `12:16
+05:00`. No store listing, release, event, report configuration, rating, or
policy state was changed.

A later authenticated Play Console pass at `2026-08-29 23:37–23:46 +05:00`
created two non-PII CSV exports and enabled account-level email notifications
for new one- through five-star reviews and edited reviews. That notification
change is operational review-SLA state, not a store listing, release, rating,
review response, or publication change.

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
- Ratings Overview reports a global default rating of `1.000` from `1` user.
  The all-time reviews page contains zero text reviews, and the rating breakdown
  exposes no matching rating in its most recent 90-day range. The lone rating
  is therefore not evidence of a new reported defect, but the page still does
  not prove its date, app version, device, or storefront. It is not imported as
  a UZ rating;
- the monitoring overview reports no policy violations. This global
  point-in-time observation cannot by itself close the two-store app-global
  policy guardrail.

The aggregate installed-audience CSV is retained outside Git at
`../.nimbo-release/growth/console/2026-08-29/play-installed-users-uz-2026-08-19_25.csv`.
It contains no PII and has SHA-256
`dc07b1de33be37388023400c0b176f6dcda7604c9d9d8467c2b5a2be4e7d85f8`.

### Exact store-listing export boundary

The later pass selected country dimension `Overall, UZ` and exported legacy
store-listing acquisitions and visitors. The explicit `2026-08-01..2026-08-28`
request returned rows only through August 22. Its UZ series contains two
visitors on August 6, one on August 9, one on August 10, and one store-listing
acquisition on August 6. This is a dated sparse daily series, not evidence for
the latest seven-day candidate window and not a basis for attributing the
global `40.82%` summary conversion to Uzbekistan.

For the latest seven complete rows, the report was narrowed to
`2026-08-16..2026-08-22` while `UZ` remained requested in the URL. The Console
and the resulting CSV omitted the UZ columns entirely and exported only the
Overall series. The omitted UZ series is privacy-suppressed or unavailable; it
is **not numeric zero**. Therefore even this exact seven-day export cannot
populate UZ store-listing visitors, acquisitions, or conversion.

Both non-PII raw exports are retained outside Git:

- `../.nimbo-release/growth/console/2026-08-29/play-store-listing-country-2026-08-01_28.csv`
  — SHA-256
  `bb65db7919ac539302807602498dbc2a65de2b7d5fcd0fb446e529798fb1e2a9`;
- `../.nimbo-release/growth/console/2026-08-29/play-store-listing-country-2026-08-16_22.csv`
  — SHA-256
  `7bcf89cf40a4a62e0f2c3ea2f3174863117e625681772130f4029784200387d2`.

## App Store Connect

The Nimbo Analytics URL redirected to App Store Connect login with
`authResult=FAILED`. A passkey flow was started but did not establish a session;
the page was reloaded to cancel the pending verification. No password, passkey
secret, or 2FA value was entered, guessed, or extracted. No current Apple weekly
aggregate was obtained, and older point-in-time console observations were not
relabelled as a complete UZ weekly slice.

## Import decision

No file was written to `growth/data/weekly/`. Import user metrics only after
both consoles expose the same seven complete days with explicit UZ filters and
source/device/version definitions. An export that silently omits the requested
UZ series does not meet that requirement. Suppressed, partial, or unavailable
values must remain absent rather than becoming zero. Policy status is instead
an app-global point-in-time value and must use storefront `ALL`; both
`apple_policy_issues` and `google_policy_issues` are required before the
combined critical policy guardrail may pass.
