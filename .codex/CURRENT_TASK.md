# Current task

## Goal

Create the Nimbo KMP/CMP foundation and first real vertical slice from Open-Meteo through normalized domain state into shared Compose UI on Android and iOS.

## Acceptance criteria

- Android application ID remains `uz.ganikhodjaev.weather`.
- Android and iOS compile from the same shared UI/domain code.
- No API secret is present in new code.
- Current/hourly Open-Meteo data is decoded into domain models and rendered through explicit UI state.
- Foundation tests pass on supported host targets.

## Affected areas

Gradle structure, Android shell, new iOS shell, shared model/data/domain/UI, CI, and legacy code removal.

## Checks

Android unit tests and debug build; shared tests; iOS simulator framework/app build; secret scan; package identity validation.

