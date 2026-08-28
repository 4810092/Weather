# Nimbo UZ growth dashboard

`artifact.json` is the canonical, source-backed dashboard definition. The SQL
files contain the bounded reproducible snapshot queries embedded by the
artifact. `report.html` is generated from that artifact with the packaged Data
Analytics portable-artifact renderer; it must not be edited by hand.

The snapshot is intentionally `partial`. On 2026-08-29 the full monitored rank
capture is incomplete because the auxiliary Apple `Toshkent ob-havo` search
returned only one unique app, below the 10-app completeness floor. All required
goal surfaces are complete, so the day is correctly recorded as a failed goal
day with bounded absences and a zero-day streak. Missing raw store exports and
the missing symbolicated iOS crash report remain explicit access issues rather
than silently becoming zeroes or passes.

Refresh order:

1. Run the public rank monitor and import the latest store exports.
2. Reconcile every numerator, denominator, window, country, device, and version.
3. Update the bounded SQL and artifact snapshot.
4. Rebuild `report.html` with the Data Analytics delivery script.
5. Run the repository checks before a dashboard is published.
