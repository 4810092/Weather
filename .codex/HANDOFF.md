# Handoff

## Where we are

The legacy repository is audited and recoverable through `legacy-android-v1.0.1`. Nimbo now has a working KMP/CMP product flow: shared Compose UI/domain/data, Android/iOS shells, Open-Meteo, SQLDelight cache, onboarding, optional location, city switching, insights, outside scoring, and recent history.

## Green

Shared tests and Android debug assembly succeed. iOS clean-install onboarding is visually verified. Android API 36 clean install, search, live Tashkent selection, centred timeline, insights, outside scoring, history, and approximate permission UI are visually verified.

## Broken or blocked

No local Play upload keystore or Apple account verification. The exposed OpenWeather key requires external revocation.

## What remains

Localization, units/settings, structured errors, accessibility/adaptive polish, store assets, CI, signing, upgrade QA, and submission.

## Run next

Read `.codex/PROJECT_STATE.md` and `.codex/CURRENT_TASK.md`, then implement units and localization without regressing the tested location/weather flow.

## Relevant files

`shared/`, `app/`, `iosApp/`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, and `docs/adr/`.
