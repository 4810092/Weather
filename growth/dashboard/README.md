# Nimbo UZ growth dashboard

`artifact.json` is the canonical, source-backed dashboard definition. The SQL
files contain the bounded reproducible snapshot queries embedded by the
artifact. `report.html` is generated from that artifact with the packaged Data
Analytics portable-artifact renderer; it must not be edited by hand.

The dashboard is intentionally `blocked`, with scale status `hold`.
Public outreach and acquisition scaling remain gated on provider clearance, crash diagnosis, source-synced signed phone, Wear OS, and Apple artifacts, complete physical-device coverage, and critical console guardrails.
On 2026-08-29 the auxiliary Apple
`Toshkent ob-havo` search returned only one unique app, below the 10-app
completeness floor, while all required goal surfaces were complete and failed;
the streak is therefore correctly zero. Product commit `24ea373` resolves to
phone 1.1.0 (8), Wear OS 1.1.0 (1000008), and Apple 1.1.0 (6). Its
Bundletool-validated phone AAB
`f91d0dce82aad7596118a6563d64b94f9f90daa2550cfb4b345fc3ef966bfdab`
and mapping
`d749110783872a36406c56a99b11d9c67764a7973d767656c3bd6f0ed59addfd`
embed the exact revision, but the AAB has zero signature entries. The Wear AAB
`6bcf5f9b947cb52887ba2e5c7a48c59cd5a1428c4680c67d63edd6a708bcd439`
also embeds `24ea373` and has zero signature entries; the retained signed Wear
bundle still embeds historical revision `4d9492a`. Exact Apple simulator
executables are app
`421b867257004a15e6042cb98817190570b91cb8c54ac61b3c4e8df049f94ad7`,
widget
`e639f0661cd6e96924803d8aa5982706ee0d78c981b7d2d4375b920d2eac1b27`,
and watch
`9f29f22984185f2c5cf072357434b442b5e95f90b6c292b9aabfc97993bd689d`.
Their UUID-matched dSYMs verify, 18 Swift surface tests pass, and the Release
simulator builds succeed, but all three remain ad-hoc simulator products rather
than uploadable archives. The exact debug phone APK passed a fresh-install
physical API 25 smoke in Russian, including Tashkent without location
permission, first-screen Best Time rendering, and 150% text; its installed
bytes matched. API 24 widget and API 37 round-Wear emulator scenarios remain
prior regression evidence for `ee7c36f`; none of this is source-synced signed
physical proof. Google Play Custom Store Listing `4834799756935529888` persists as an
Uzbekistan-only `Draft` with Uzbek fallback and separate Russian copy and
creatives. It was not submitted for review or published, and public production
remains `1.0.2 (6)`.
Exact-current signed-release phone, tablet, widget, and paired Wear OS coverage
is still missing despite the bounded exact debug-phone pass. The iPad
CoreDevice/DDI path is usable, but no exact-current signed
Apple build exists, so it cannot provide current physical proof. The historical
iOS crash still lacks a symbolicated report; current-source hardening, tests,
and simulator builds cannot be attributed to that event and do not close the
crash gate. The authenticated Gmail thread and broad Open-Meteo searches were
checked read-only at 13:12 +05:00: the 06:05:07 clarification remains the
only indexed matching message with label `SENT`, and no inbound Open-Meteo
reply is indexed in that account. This does not prove delivery or exclude
another account or a later unindexed reply; written clearance remains absent.
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
