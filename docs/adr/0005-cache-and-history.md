# ADR 0005: Cache, refresh, and forecast history

Status: accepted  
Date: 2026-08-09

## Decision

The database is the UI source of truth. A refresh writes current/hourly data and an issued forecast snapshot transactionally. UI renders cached data first and observes database changes.

Current/hourly data is fresh for 15 minutes, usable-but-aging for 6 hours, and stale after 6 hours. Stale data remains visible with its age until replaced or explicitly cleared. Historical observations are refreshed independently and retained for the recent comparison window; forecast snapshots are retained long enough to compare issued values with observations.

Refresh order is current/hourly, today's context, yesterday, deeper history, then issued-forecast enrichment. Retries are bounded, cancellation-aware, and limited to transient failures.

## Consequences

Network failure cannot blank a usable screen. Users always see whether data is offline or stale. Secondary history work cannot delay the first meaningful UI.

