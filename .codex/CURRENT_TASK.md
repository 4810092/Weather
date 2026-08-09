# Current task

## Goal

Build the real first-run location experience and deterministic insight engines on the green KMP/CMP foundation.

## Acceptance criteria

- Android application ID remains `uz.ganikhodjaev.weather`.
- A clean install asks for context before showing a location.
- Users can search for a city and use the app when location access is unavailable or denied.
- Platform location requests are contextual, optional, and approximate by default.
- Insight and best-time-outside domain outputs are deterministic, explainable, localized outside domain, and unit tested.
- Cache-first behavior and both platform builds stay green.

## Affected areas

Shared onboarding/domain/presentation/UI, Android and iOS location adapters, SQLDelight queries, and tests.

## Checks

Shared tests; Android debug/release build; iOS simulator build and launch; permission-denied and offline smoke tests.
