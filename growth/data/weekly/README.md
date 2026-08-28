# Normalized weekly console aggregates

`import_weekly.py` writes one `YYYY-MM-DD.json` per seven-day period, where the filename/date is `week_end`. Each raw record preserves platform, storefront, source scope, device, app version, metric, unit, source path, evidence date, and note. Derived metrics include their exact numerator and denominator keys.

The evaluator consumes only explicit `UZ` summary rows (`source_scope=summary`, `device=all`, `app_version=all`) for all-up KPIs. Per-device Android/Wear guardrails are evaluated across their device rows. Breakdown rows are retained for diagnosis and are never summed automatically.

Do not commit user-level data, private exports, credentials, device identifiers, or precise locations. Missing/suppressed console data is represented by an absent metric, not zero.
