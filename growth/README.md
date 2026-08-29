# Nimbo growth operations

Current verdict (2026-08-29): **HOLD ACQUISITION**. The reproducible public
monitor and daily snapshots are in place, but the required rank surfaces fail
and the Top-10 streak is zero. Current phone vc8 and Apple build 6 cannot
complete their protected private-signing operations and therefore have no
source-synced signed artifact, matching hash, or physical QA; signed phone vc7
and Apple build 5 are historical evidence only. OpenMeteo GmbH has confirmed
the exact unpaid, non-monetized organic-promotion scope for the non-commercial
API. The iOS crash diagnostic, complete device matrix, and reconciled console
exports are still missing. A build, a Pages
deployment, or historical device evidence does not close those gates.

## Evidence model

| Evidence | Path | Meaning |
| --- | --- | --- |
| Reported baseline | [baseline/2026-08-28.md](baseline/2026-08-28.md) | User-provided console values, preserved with missing definitions and breakdowns |
| Public rank/search | [data/public-rank](data/public-rank) | Fixed, unauthenticated daily observations with response hashes and bounded absences |
| Console aggregates | [data/weekly](data/weekly) | Validated long-format weekly imports from named App Store Connect / Play Console paths |
| KPI contract | [kpi-framework.json](kpi-framework.json) | Targets, guardrails, seven-day goal, and fail-closed 90-day rules |
| Metric contract | [metric-definitions.md](metric-definitions.md) | Denominators, populations, source caveats, and current official references |
| Operational gates | [quality/gates.json](quality/gates.json) | Provider, crash, device-smoke, and policy state; unknown is not pass |
| Provider clarification | [legal/open-meteo-clarification-email.md](legal/open-meteo-clarification-email.md) | Exact written Free/non-commercial API permission scope and the material-change boundary |
| Seasonal content backlog | [content/articles.json](content/articles.json) and [content/calendar.csv](content/calendar.csv) | Two source-backed UZ/RU/EN draft articles per month from September through November 2026; every route remains draft-blocked until all publication gates pass |
| Provider capacity | [legal/open-meteo-capacity-contingency-2026-08-29.md](legal/open-meteo-capacity-contingency-2026-08-29.md) | Source-derived request model, implemented cache gate, official limits, and the no-key-in-client boundary |
| Android emulator QA | [quality/android-emulator-smoke-2026-08-28.md](quality/android-emulator-smoke-2026-08-28.md) | API 24/36 live, denied-location, search, offline/error, recovery, and cold-start evidence |
| Android physical QA | [quality/android-physical-smoke-2026-08-28.md](quality/android-physical-smoke-2026-08-28.md) | Clean API 25 live/search/cold-start evidence and uninstall boundary |
| Trust and feedback QA | [quality/android-trust-feedback-smoke-2026-08-29.md](quality/android-trust-feedback-smoke-2026-08-29.md) | Exact-commit API 25 fresh-install plus API 36 preserved-data update, support/rate destinations, byte identity, and cleanup boundary |
| Public ASO deployment gap | [quality/public-store-deployment-gap-2026-08-29.md](quality/public-store-deployment-gap-2026-08-29.md) | Dated public-store proof plus the authenticated unpublished Google UZ draft boundary |
| UZ competitor ASO audit | [reports/aso-competitor-audit-2026-08-29.md](reports/aso-competitor-audit-2026-08-29.md) | Bounded official-store term evidence and the resulting truthful Apple/Google metadata revisions |
| Provider-throttle physical QA | [quality/android-provider-throttle-smoke-2026-08-29.md](quality/android-provider-throttle-smoke-2026-08-29.md) | Current-commit API 25 fresh-cache skip, manual bypass, recovery, and cleanup evidence |
| Apple runtime QA | [quality/apple-runtime-smoke-2026-08-28.md](quality/apple-runtime-smoke-2026-08-28.md) | Simulator and bounded iPad proof plus the explicit iPhone DDI blocker |
| iOS 15 widget compatibility | [quality/ios-widget-compatibility-2026-08-29.md](quality/ios-widget-compatibility-2026-08-29.md) | Exact product-source minOS/UUID/hash proof plus available-runtime host integration and the explicit missing iOS 15/16 runtime boundary |

The public monitor does not log in, use cookies, bypass access controls, or claim to reproduce personalized store UI. Google results remain sensitive to IP, compatibility, experiments, and server behavior. An absent target is recorded only as `> observed_count`.

## Daily public monitor

Run once per day while the host timezone is `Asia/Tashkent`:

```sh
python3 scripts/growth/monitor_public_rank.py
python3 scripts/growth/evaluate_growth.py --replace
```

The first command writes `growth/data/public-rank/YYYY-MM-DD.json`. It returns
zero when the required goal evidence is decisive, whether the result is pass or
fail, and non-zero only when that result remains unknown. Auxiliary diagnostic
incompleteness does not fail a decisive goal snapshot. It refuses to silently
overwrite a day unless `--replace` is provided. The second command writes the
current decision record in `growth/reports/`.

For hourly visibility after the canonical daily file already exists, use
`--check-current` for a compact non-writing JSON result or
`--append-intraday` for an append-only local observation. Intraday files are
explicitly ineligible for streak calculation and are ignored by Git; they do
not replace or supplement the one canonical daily result. `--stdout` emits the
full current capture without writing a file. See
[data/public-rank/README.md](data/public-rank/README.md) for the exact contract.

The Codex task has an active local heartbeat named
`Nimbo UZ rank and domain monitor` on a temporary hourly cadence while crash
and release-access blockers are unresolved. It refreshes the public
rank/evaluation state when needed and may append a local intraday observation
without changing the canonical daily streak input; on
Mondays it also imports a new user-supplied, valid seven-day console CSV when
one is present. It never bypasses authentication or 2FA. The optional macOS launchd template in
[automation](automation) remains uninstalled, avoiding a duplicate machine
scheduler.

## Weekly console import

1. In App Store Connect, select the same seven complete days, territory `UZ`, and the needed source/device/version cuts. Capture acquisition, downloads, usage/retention, ratings, crashes, and current policy state. Preserve unique versus total labels.
2. In Play Console, select the same seven days and `UZ`. Capture store-listing visitors/install clicks, installations/first launches, retention, active users, ratings, Android vitals (including worst relevant device models), user loss, and policy state.
3. Copy [imports/templates/weekly_metrics.csv](imports/templates/weekly_metrics.csv). Add one row per metric and dimension. Use `source_scope=summary`, `device=all`, and `app_version=all` only for an actual all-up UZ summary; keep breakdown rows separate.
   The two app-global policy-state metrics are the exception: import them with
   `storefront=ALL`, and require both Apple and Google before the combined
   policy guardrail can pass.
4. Remove unavailable metrics rather than entering zero. Every row needs a human-readable console path in `source_ref`, an evidence date, and the catalogue's exact unit.
5. Validate and normalize:

```sh
python3 scripts/growth/import_weekly.py /path/to/weekly_metrics.csv
python3 scripts/growth/evaluate_growth.py --replace
python3 scripts/growth/generate_weekly_report.py \
  growth/reports/evaluation-YYYY-MM-DD.json
```

The importer rejects unknown metrics, wrong units, negative/non-finite values, duplicate scopes, non-seven-day windows, and stale `source_as_of` dates. Derived rates are calculated only inside an identical platform/storefront/source/device/version scope. The report generator writes `growth/reports/weekly-YYYY-MM-DD.md`, accepts only a schema-valid same-date public-rank snapshot and the exact seven-day weekly period referenced by the evaluation, and cross-checks current ranks, derived ratios, KPI actuals, ratings, and quality guardrails before displaying a result. Missing, rejected, or conflicting linked evidence is rendered as `UNKNOWN` or `CONFLICT`, never as a pass. It is deterministic, offline, and uses an atomic no-clobber write unless `--replace` is explicitly supplied. Raw exports/screenshots should stay in approved private storage; this repository needs only aggregate, non-PII evidence.

The generated report follows [reports/weekly-template.md](reports/weekly-template.md) for the operating review. Do not average store percentages across breakdowns or interpret privacy-thresholded missing rows as zeros.

## 90-day rule and action boundary

The checkpoint is 2026-11-26. The evaluator applies rules in this order:

1. Any critical gate/guardrail failed or unknown → hold acquisition and fix the gate.
2. Sufficient conversion or retention data below target → iterate product and listing.
3. Quality passes and at least one exact comparable primary surface improves by 20+ positions → continue organic work.
4. Quality passes and comparable improvement is below 20 → prepare a paid-pilot/provider-cost proposal only.
5. Non-comparable or insufficient evidence → continue measurement; no paid decision.

No script publishes store changes, sends email/outreach, buys ads, changes the Open-Meteo endpoint, or authorizes spend. Those remain explicit human approvals.

## Verification

All parser and metric tests use local fixtures and do not require network access:

```sh
python3 -m unittest discover -s scripts/growth/tests -v
python3 -m compileall -q scripts/growth
```
