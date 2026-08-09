# Handoff

## Where we are

The legacy repository is audited and recoverable through `legacy-android-v1.0.1`. The Nimbo branch now has a working KMP/CMP foundation: shared Compose UI/domain/data, Android shell, iOS shell, Open-Meteo, and SQLDelight cache.

## Green

Shared tests and Android debug assembly succeed. The iOS simulator app builds, launches, and renders live Tashkent weather on an iPhone 16 Pro simulator.

## Broken or blocked

No local Play upload keystore or Apple account verification. The exposed OpenWeather key requires external revocation.

## What remains

Onboarding/location selection, deterministic insight engines, historical comparison UX, localization, settings, accessibility/adaptive polish, store assets, CI, signing, upgrade QA, and submission.

## Run next

Read `.codex/PROJECT_STATE.md` and `.codex/CURRENT_TASK.md`, then implement onboarding and location selection without regressing the green vertical slice.

## Relevant files

`shared/`, `app/`, `iosApp/`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, and `docs/adr/`.
