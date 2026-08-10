# ADR 0002: SQLDelight persistence

Status: accepted  
Date: 2026-08-09

## Context

The database must behave consistently on Android and iOS, expose reactive cached data, support explicit migrations and tests, and store hourly weather, observations, forecast snapshots, locations, and metadata.

## Options

- Room KMP 2.8.4: official AndroidX support, familiar DAO API, Flow, schema export, migration helpers, and a bundled SQLite option. It is a credible choice and has better familiarity for Android-heavy teams. Its KMP setup adds KSP/code-generation configuration per target, its iOS adoption history is shorter, and DAO annotations hide more of the executed SQL.
- SQLDelight 2.3.2: long-standing KMP/iOS support, checked SQL, explicit schema/migrations, small runtime, reactive queries, and no annotation processor. It requires the team to own SQL, relationship mapping, dispatcher choices, and migration fixtures directly; it also provides fewer Android-specific conveniences than Room.
- Settings/files: insufficient for relational hourly history and migration guarantees.

## Decision

Use SQLDelight with platform SQLite drivers. The deciding factors are equal Android/iOS maturity, explicit reviewable SQL, and avoiding per-target KSP in this small codebase—not a claim that SQLDelight is universally better. Keep database rows inside the data layer and map to domain models. Export and test every schema migration against a checked-in database produced by the preceding released schema.

## Consequences

SQL and migrations remain visible and reviewable, and the iOS path avoids KSP complexity. The team must be comfortable owning SQL explicitly and cannot rely on Room-specific tooling.
