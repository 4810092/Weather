# Nimbo UZ growth dashboard

`artifact.json` is the canonical, source-backed dashboard definition. The SQL
files contain the bounded reproducible snapshot queries embedded by the
artifact. `report.html` is generated from that artifact with the packaged Data
Analytics portable-artifact renderer; it must not be edited by hand.

The dashboard is intentionally `blocked`. On 2026-08-29 the auxiliary Apple
`Toshkent ob-havo` search returned only one unique app, below the 10-app
completeness floor, while all required goal surfaces were complete and failed;
the streak is therefore correctly zero. Current phone vc8 and Apple build 6
cannot complete their protected private-signing operations and lack signed
artifacts plus matching release-certificate physical QA; the bounded phone vc8
API 25 debug/source pass is now historical because runtime source changed. The retained signed Wear
artifact is current but lacks physical-watch QA. The iOS crash lacks a symbolicated report, and
`nimbo.uz` is still waiting for registrar activation. Missing
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
