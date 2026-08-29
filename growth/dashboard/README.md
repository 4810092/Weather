# Nimbo UZ growth dashboard

`artifact.json` is the canonical, source-backed dashboard definition. The SQL
files contain the bounded reproducible snapshot queries embedded by the
artifact. `report.html` is generated from that artifact with the packaged Data
Analytics portable-artifact renderer; it must not be edited by hand.

The dashboard is intentionally `blocked`, with scale status `hold`.
Public outreach and acquisition scaling remain gated on crash diagnosis,
source-synced signed phone, Wear OS, and Apple artifacts, complete
physical-device coverage, and critical console guardrails. Open-Meteo written
clearance passes for the exact unpaid, non-monetized organic-promotion scope.
The canonical `2026-08-30T00:00:25+05:00` capture places Nimbo at `#87`
for Apple `weather` search and `#22` in the official Apple Weather chart;
all three Google category profiles remain outside the first 30 and `0/5`
generic queries qualify. The auxiliary Apple `Toshkent ob-havo` search
returned only one unique app, below the 10-app completeness floor, but it is
a non-goal diagnostic source error: `goal_evidence_complete=true`, all
required goal surfaces are complete and failed, and the streak remains `0/7`.
Product commit
`9c2dce4200dbba5487c8c458ade4616005fde6e6` resolves to phone 1.1.0 (8),
Wear OS 1.1.0 (1000008), and Apple 1.1.0 (6). Its Bundletool-validated phone
AAB
`b7c7acb6e90189e8d73e5b8a5f780bf1d3ab36f43edaf3d5076a1dba4e22d4e5`
and mapping
`4fdfeefa05c8f71eb3cc2ac538732672ae2c5ba5793ddd35f03bfa7f6b714d18`
were reproduced in a clean standalone checkout and embed the exact revision,
but the AAB has zero signature entries. Mutable main-worktree `build/outputs`
are not the pinned candidate. The Wear AAB
`2d73fdf1e4fd661a96a699a9fd2ef7b2e989b0f4ab019692ce7c97465673d3fa`
also embeds the exact revision and has zero signature entries; the retained
signed Wear bundle still embeds historical revision `4d9492a`. Exact Apple
simulator executables are app
`b7c3ba937658007b07ee9ad8e85ddc892e90f423e7839e0dc112a1070ea04849`,
widget
`7191acd40334d4d9fec6062bc5023450fefbb55006fbd92f57109f41eb27a7ff`,
and watch
`c310c785750ffa779e5dfdc30384088fca889deddb11417f2b4e8e0e30109728`.
Their UUID-matched dSYMs verify; the shared iOS simulator suite, 18 Swift
surface tests, full Gradle release gate, and localization parity pass. All
three Apple products remain ad-hoc simulator outputs rather than uploadable
archives. Twelve EN/RU/UZ iPhone phone sources now come from the exact-current
`9c2dce4` build-6 simulator app: overview, recent comparison, selected timeline,
and 10-day/AQI details in each locale. The attempted Apple offline transition
was not captured and is not claimed. This proves localized phone screenshot
provenance only, not signing, physical-device, TestFlight, or store state.
Apple Watch sources remain historical build-5 simulator evidence. Product
commit `9c2dce4` also closes three
deterministic storage-failure exception escapes and adds four
throwing-repository regressions.

Exact-current debug APK and installed bytes
`52146b883a04e4c2d272ea4e3ecc9b1277a8c78c117b547a121de3a7d90c3730`
passed a clean physical General Mobile API 25 smoke in Russian: Tashkent
without location permission, live forecast, truthful late-day Best Time,
durable-tip persistence, offline cache, recovery, process health, and cleanup
passed, with zero product-scoped fatal/ANR/SSL/CertPath/trust-anchor matches.
The exact-source API 24 emulator APK
`168bb6acdb95453a8dfd141947edbcb9292b756fd3429fffa56fc4baf125dbec`
retains its fresh live/cache/recovery pass. The byte-identical exact-current
debug APK and installed bytes
`52146b883a04e4c2d272ea4e3ecc9b1277a8c78c117b547a121de3a7d90c3730`
also passed a fresh no-snapshot API 36 Pixel Tablet emulator smoke in Uzbek:
landscape onboarding, live forecast, Best Time, durable-tip persistence,
home-screen widget render/tap, font scale `1.3`, rotation, process health, and
cleanup passed. These are debug regression results; the API 36 result is
emulator evidence, not physical-tablet or upload-signed release proof. Prior
API 37 round-Wear evidence remains historical. Google Play Custom Store Listing
`4834799756935529888` persists as an Uzbekistan-only `Draft` with Uzbek fallback
and separate Russian copy and creatives. It was not submitted for review or
published, and public production remains `1.0.2 (6)`.
At 22:56 +05:00, authenticated App Store Connect API inventory reads confirmed
that Apple exposes public iOS `1.0.1` with valid build `4`, and contains no
`1.1.0` version or builds `5`/`6`. Build-detail and diagnostic-signature GETs
for build `4` returned security `403`. A single bounded POST attempting to
create only a manual-release `1.1.0` version also returned `403`; a final
authenticated GET again returned zero `1.1.0` versions, proving that no partial
version or localization draft was created. No build, localization, screenshot,
Custom Product Page, submission, or release mutation followed. The Apple copy
and creative payload therefore remains repository-prepared, not an App Store
Connect draft or deployed store state.
The same authenticated preflight found zero existing analytics report requests.
Exactly one bounded POST then attempted to create an `ONGOING` analytics report
request for app `6799886897`; App Store Connect returned security `403` without
a resource ID. The request was not retried, and no duplicate, report instance,
segment, user-level data, or PII was created or downloaded. Automated weekly
Apple analytics therefore remains permission-blocked for the current key and
the dashboard's missing-console-data state remains explicit.
An authenticated Play Console refresh at `2026-08-29 23:37–23:46 +05:00`
confirmed the global default rating remains `1.000` from one user, with zero
written reviews across the all-time range. The lone star-only rating has no
reply surface and is not attributed to Uzbekistan, a device, version, or
storefront. Account-level email notifications were enabled and saved for new
one- through five-star reviews and edited reviews; no email address, reviewer
data, or other PII is stored in the dashboard. The existing daily heartbeat
now checks the Nimbo review inbox once per day after `09:15` Asia/Tashkent.

The same refresh showed a rolling `Last 28 days` acquisition snapshot of `778`
device impressions, `21` installs, `14` first opens, `11` monthly active
devices, unavailable D7 retention, and the unchanged `40.82%` summary
conversion. The dated historical baseline remains `779` impressions and is not
rewritten by a moving-window refresh. The separate modern Store Listings window
`2026-07-27..2026-08-23` reported `44` visitors, `18` install clicks, and `41%`
CTR across listing surfaces; its published default-listing row separately
reported `42` visitors and `28.6%` conversion. These are distinct populations
and are not reconciled with each other or with the acquisition-summary card.
For the exact `2026-08-16..2026-08-22` export, Console retained `UZ` in the
request but omitted the UZ series from both the table and CSV. No UZ visitor,
acquisition, or conversion value is imported, zero-filled, or derived.
Exact-current signed-release phone, tablet, widget, and paired Wear OS coverage
is still missing despite the bounded exact API 24 emulator and API 25 physical
phone plus API 36 emulator tablet/widget debug passes. Android Keychain
metadata and the existing mode-600 keystore are present, but the protected value
was not retrieved and upload signing remains unavailable. At 20:44 +05:00 the
iPad was again available and paired, but lock-state and DDI queries failed
because it had not been unlocked recently; the iPhone and watch remained
unavailable. No exact-current signed Apple build exists, so it cannot provide
current physical proof; iOS 15 runtime coverage is also unverified. The
historical iOS crash still lacks a diagnostic and symbolicated report. The
authenticated inventory path closes the API-authentication discovery gap, but
its diagnostic request is permission-blocked by `403` and cannot recover the
suppressed crash signature or log.
Current-source hardening, tests, and simulator builds cannot identify or be
attributed to that event and do not close the crash gate. OpenMeteo GmbH
replied at 17:25 +05:00 in ticket `234272` and
explicitly confirmed non-commercial API entitlement under the complete terms
sent at 06:05:07 +05:00. The pass is limited to the described free,
non-monetized app and unpaid organic promotion; a material monetization,
promotion, attribution, or usage-limit change reopens the licensing decision.
At 10:40–10:41 +05:00, GitHub Pages showed a successful DNS check with
`Enforce HTTPS` enabled. The Let's Encrypt certificate validates for both
`nimbo.uz` and `www.nimbo.uz`; WHOIS, `.uz` delegation, Cloudflare records,
independent public DNS, HTTPS, redirects, canonicals, language declarations,
all 12 localized routes, growth, robots, sitemap, and metadata schema passed.
The domain gate is now `pass`; Uzbek intentionally uses the site root rather
than a separate Uzbek-prefixed route.
Missing evidence elsewhere remains explicit rather than silently becoming a
zero or pass.
The dashboard also exposes every critical metric guardrail; all eight are
currently `unknown`, independently blocking scale. The app-global point-in-time
`open_policy_issues` metric requires both `storefront=ALL` records and remains
intentionally distinct from the operational `store_policy_console_clearance`
gate.

Refresh order:

1. Run the public rank monitor and import the latest store exports.
2. Reconcile every numerator, denominator, window, country, device, and version.
3. Update the bounded SQL and artifact snapshot.
4. Rebuild `report.html` with the installed Data Analytics portable-artifact
   renderer:

   ```sh
   NIMBO_DATA_ANALYTICS_PLUGIN_ROOT=/absolute/path/to/data-analytics-plugin
   node "$NIMBO_DATA_ANALYTICS_PLUGIN_ROOT/skills/build-report/scripts/deliver_portable_artifact.mjs" \
     --input growth/dashboard/artifact.json \
     --output growth/dashboard/report.html
   ```

5. Run `python3 scripts/check_dashboard_report.py` to prove every cited SQL/JSON
   input, the canonical artifact, and the embedded report payload agree.
6. Run the repository checks again before a dashboard is published.
