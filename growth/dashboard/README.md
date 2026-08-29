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
the streak is therefore correctly zero. Product commit `ee7c36f` resolves to
phone 1.1.0 (8), Wear OS 1.1.0 (1000008), and Apple 1.1.0 (6). Its
Bundletool-validated phone AAB
`e16da522aca84776419a999db82a9ddb5a42b15660516bfe6f1fd65cf5a3edcb`
and mapping
`7e678576d95e36dd8e27cab78a565a47a1539a3caf6f769a283f9aca415a324f`
embed the exact revision, but the AAB has zero signature entries. The Wear AAB
`d1088ec635b69258baf5aaa42e42423b930a97a3077f059a2ae59c6d06061e71`
also embeds `ee7c36f` and has zero signature entries; the retained signed Wear
bundle still embeds historical revision `4d9492a`. Exact Apple simulator
executables are app
`279185d6778c7819d889a1f769d8ce2eb10b861790ed4ef2cc833044946aad90`,
widget
`bd651c05eb19551853fd5dde604fafdc7233f1615f21a9462b20f45199dc3209`,
and watch
`14c419fb71f35097c0fe4396183acb1d701ef229ea55f3608a2982d5bab5c493`.
Their UUID-matched dSYMs verify, 18 Swift surface tests pass, and the Release
simulator builds succeed, but all three remain ad-hoc simulator products rather
than uploadable archives. A clean Gradle gate parsed 232 test executions with
zero failures. API 24 widget and API 37 round-Wear emulator scenarios pass the
strict Empty/Fresh/Stale contract; this is not source-synced signed physical
proof. Google Play Custom Store Listing `4834799756935529888` persists as an
Uzbekistan-only `Draft` with Uzbek fallback and separate Russian copy and
creatives. It was not submitted for review or published, and public production
remains `1.0.2 (6)`.
Historical physical Android evidence remains scoped to commit `df5f824`.
Exact-current signed-release phone, tablet, widget, and paired Wear OS coverage
is missing. The iPad CoreDevice/DDI path is usable, but no exact-current signed
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
