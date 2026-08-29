# Nimbo UZ growth dashboard

`artifact.json` is the canonical, source-backed dashboard definition. The SQL
files contain the bounded reproducible snapshot queries embedded by the
artifact. `report.html` is generated from that artifact with the packaged Data
Analytics portable-artifact renderer; it must not be edited by hand.

The dashboard is intentionally `blocked`, with scale status `hold`.
Public outreach and acquisition scaling remain gated on provider clearance, crash diagnosis, source-synced signed phone, Wear OS, and Apple artifacts, complete physical-device coverage, registry delegation/DNS/TLS, and critical console guardrails.
On 2026-08-29 the auxiliary Apple
`Toshkent ob-havo` search returned only one unique app, below the 10-app
completeness floor, while all required goal surfaces were complete and failed;
the streak is therefore correctly zero. Current phone vc8 and Apple build 6
cannot complete their protected private-signing operations and lack signed
artifacts plus matching release-certificate physical QA. Exact commit `97c26cb`
has a Bundletool-validated phone AAB with zero signature entries and a matching
debug APK that passed bounded API 25/API 36 QA. Its exact-current Apple simulator
products passed 40 bounded cold launches but carry only ad-hoc linker signatures,
so they provide neither an archive nor physical-device proof. The retained signed
Wear bundle embeds historical revision `4d9492a`; its non-signature payload matches
the fresh `97c26cb` output except for VCS metadata, but no exact-current signed Wear
bundle exists. The historical iOS crash
still lacks a symbolicated report; the current-source hardening evidence cannot
be attributed to that event and does not close the crash gate. The
Open-Meteo clarification has been sent but is awaiting a written response.
At 09:52 +05:00, WHOIS showed `nimbo.uz` active with the intended Cloudflare
nameservers, clearing the registrar-record blocker; the Cloudflare zone remains
pending, and parent delegation, public resolution, and HTTPS are still unavailable. Missing
evidence remains explicit rather than silently becoming a zero or pass.
The dashboard also exposes every critical weekly metric guardrail; all eight
are currently `unknown`, independently blocking scale. The point-in-time
`store_policy_console_clearance` operational gate is intentionally distinct
from the weekly `open_policy_issues` metric.

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
