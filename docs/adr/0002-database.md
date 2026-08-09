# ADR 0002: SQLDelight persistence

Status: accepted  
Date: 2026-08-09

## Context

The database must behave consistently on Android and iOS, expose reactive cached data, support explicit migrations and tests, and store hourly weather, observations, forecast snapshots, locations, and metadata.

## Options

- Room KMP 2.8.4: official AndroidX support, familiar DAO API, Flow, schema export, migrations, and recommended bundled SQLite; KMP requires per-target code generation and retains some Android-first limitations.
- SQLDelight 2.3.2: long-standing KMP/iOS support, checked SQL, explicit schema/migrations, small runtime, reactive queries, and no annotation processor.
- Settings/files: insufficient for relational hourly history and migration guarantees.

## Decision

Use SQLDelight with platform SQLite drivers. Keep database rows inside the data layer and map to domain models. Export and test every schema migration.

## Consequences

SQL and migrations remain visible and reviewable, and the iOS path avoids KSP complexity. The team must be comfortable owning SQL explicitly and cannot rely on Room-specific tooling.

