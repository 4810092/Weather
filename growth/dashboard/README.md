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
On 2026-08-29 the auxiliary Apple
`Toshkent ob-havo` search returned only one unique app, below the 10-app
completeness floor, while all required goal surfaces were complete and failed;
the streak is therefore correctly zero. Product commit `9342824` resolves to
phone 1.1.0 (8), Wear OS 1.1.0 (1000008), and Apple 1.1.0 (6). Its
Bundletool-validated phone AAB
`e1c65555ed6848e30b335af2312acd37200f741bc42f55e2754a79134b84c5f8`
and mapping
`df9153ef1bc8973c39df369a2d5fb14825bcd0a04c9ea3ee5a2634e7494d9a6a`
were reproduced in a detached exact-source standalone checkout and embed the
exact revision, but the AAB has zero signature entries. Mutable main-worktree
`build/outputs` are not the pinned candidate. The Wear AAB
`d5c681fb292596b8703cea3a1b40e33d1f9ce450202648777af02d69066437c5`
also embeds `9342824` and has zero signature entries; the retained signed Wear
bundle still embeds historical revision `4d9492a`. Exact Apple simulator
executables are app
`0db3db757a7c0c497f7712c565a9b40e71edf271505cf0d0887c0ff3d59c0a76`,
widget
`57e2fcafc984c050104ceb29d16ea49a1c97c563522426833094692882edf022`,
and watch
`c6e8ff6543aa4ece0ccab7c7ee740eaef720fa07ab211e3846ca2cb00a48da66`.
Their UUID-matched dSYMs verify, 18 Swift surface tests pass, and the Release
simulator builds succeed. Exact-product EN/RU/UZ iPhone captures also pass
current-UI provenance: the first five stories now use distinct source/focus
compositions and include the real first-forecast tip. This is screenshot-source
evidence only; it does not establish conversion lift, signing, physical-device
coverage, TestFlight readiness, or publication. All three Apple products remain
ad-hoc simulator outputs rather than uploadable archives. An exact-source device
archive attempt failed at Widget CodeSign and produced no archive. The exact
debug phone APK passed a fresh-install physical API 25 smoke in Russian,
including the durable-tip CTA, acknowledgement persistence, and cold-start
suppression; its installed bytes matched. A fresh no-snapshot API 24 emulator
rerun rebuilt the same exact product source and passed live forecast, persisted
tip acknowledgement, offline cache, recovery, and the bounded fatal/TLS/ANR log
check. Prior widget and API 37 round-Wear evidence remains historical; none of
this is source-synced signed physical proof. Google Play Custom Store Listing
`4834799756935529888` persists as an Uzbekistan-only `Draft` with Uzbek fallback
and separate Russian copy and creatives. It was not submitted for review or
published, and public production remains `1.0.2 (6)`.
Exact-current signed-release phone, tablet, widget, and paired Wear OS coverage
is still missing despite the bounded exact debug-phone passes. Android Keychain
metadata and the existing mode-600 keystore are present, but the protected value
was not retrieved and upload signing remains unavailable. At 20:44 +05:00 the
iPad was again available and paired, but lock-state and DDI queries failed
because it had not been unlocked recently; the iPhone and watch remained
unavailable. No exact-current signed Apple build exists, so it cannot provide
current physical proof. The historical
iOS crash still lacks a symbolicated report; current-source hardening, tests,
and simulator builds cannot be attributed to that event and do not close the
crash gate. OpenMeteo GmbH replied at 17:25 +05:00 in ticket `234272` and
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
