# ADR 0005: Cache, refresh, and forecast history

Status: accepted  
Date: 2026-08-09

## Decision

The database is the UI source of truth. A refresh writes current/hourly data and an issued forecast snapshot transactionally. UI renders cached data first and observes database changes.

Current/hourly data is stale after 6 hours. Stale data remains visible with its age until replaced or explicitly cleared. A primary request fetches yesterday plus the next two days and commits before a secondary seven-day history request starts. Historical data is therefore enriched independently and retained for the recent comparison window.

Provider payloads are mapped before opening the write transaction. A payload with no complete required hourly row fails without deleting or replacing cached data; shorter optional arrays use neutral defaults. A valid partial payload commits every complete row.

Forecast snapshots are recorded only for future hours in the next 48 hours. The issuance timestamp is rounded to the hour, so repeated refreshes within an hour replace rather than duplicate the same snapshot. Snapshots older than 14 days are removed on every successful write. This bounds the steady-state snapshot set to at most roughly 16,128 rows per retained location (14 days × 24 hourly issuances × 48 valid hours), before SQLite page overhead. Weather rows are kept for eight days behind and three days ahead.

Retries are bounded, cancellation-aware, and limited to transient failures.

## Consequences

Network failure cannot blank a usable screen. Users always see whether data is offline or stale. Secondary history work cannot delay the first meaningful UI.
