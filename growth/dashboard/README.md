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
the streak is therefore correctly zero. Exact commit `df5f824` resolves to
phone 1.1.0 (8), Wear OS 1.1.0 (1000008), and Apple 1.1.0 (6). Its
Bundletool-validated phone AAB
`8e590cca0d7e9945874c58a412520142e9d965584236f73cb2836f98a9b9bb19`
and mapping
`1e87fc59cbfae641bd70e980d33d9696284494f08aff0240d35995d912dc7846`
embed the exact revision, but the AAB has zero signature entries. The fresh
Wear AAB
`d4df3f2a4f7c315b8afd309ea9cd5d04825c8c9662faa2a7155faf982a155637`
also embeds `df5f824` and has zero signature entries; the retained signed Wear
bundle still embeds historical revision `4d9492a`. Exact Apple simulator
executables are app
`d293763bc3dcf0eee73ebac9db1d5f0e4eda7aca7849c6000e3caf714041f5d9`,
widget
`74b6c6af76d5dc01efb61c2cd66c4fa4b28975704b690bc1371ea21579fd533b`,
and watch
`0ebc1c8f49f390e57bee86420b5be977ead8f086cb4b9a7ed0ab6849c26068c7`.
Their UUID-matched dSYMs verify and the app passed 40 bounded cold launches,
but all three remain ad-hoc simulator products rather than uploadable archives.
The exact `df5f824` debug APK passed bounded fresh-install physical API 25 QA
and a same-certificate preserved-data update on physical API 36; pulled bytes
matched on both, and the exercised support/rating paths produced no matching
fatal or ANR log entry. Exact-current tablet, widget, signed-release, and paired
Wear OS coverage remains missing. The iPad
CoreDevice/DDI path is usable again, but no exact-current signed Apple build
exists, so it cannot provide current physical proof. The historical iOS crash
still lacks a symbolicated report; 212 passing tests, current-source hardening,
and the simulator loop cannot be attributed to that event and do not close the
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
