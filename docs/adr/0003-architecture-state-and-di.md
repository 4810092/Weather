# ADR 0003: Shared UI, UDF, and manual dependency injection

Status: accepted  
Date: 2026-08-09

## Decision

Share domain, data, presentation state, design system, and Compose UI across Android and iOS. Platform shells own only lifecycle entry points, permission/location adapters, signing, and platform settings links.

Features use immutable `UiState`, explicit actions, `StateFlow`, and small state holders. Navigation is typed app state for the small v1 graph. Dependencies are assembled by a manual application container rather than a DI framework.

## Rationale

Koin 4.2 is production-capable, but Nimbo's initial graph is small and manual construction keeps startup, ownership, and iOS integration explicit. A framework can be introduced if graph size or scoped lifetimes make manual wiring materially worse.

## Consequences

Constructors remain testable and no service locator enters domain code. The composition root must stay disciplined as modules grow.

