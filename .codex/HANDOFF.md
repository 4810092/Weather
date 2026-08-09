# Handoff

## Where we are

The legacy repository has been audited. A recovery tag and Nimbo branch exist. Architecture and provider decisions are recorded; implementation has not yet replaced legacy code.

## Green

Legacy `./gradlew test assembleDebug` succeeds at commit `8fcefb8`. The tracked legacy AAB signature verifies.

## Broken or blocked

No local Play upload keystore or Apple account verification. The exposed OpenWeather key requires external revocation.

## What remains

All KMP/CMP implementation, product features, global quality, store assets, signing, QA, and submission.

## Run next

Read `.codex/PROJECT_STATE.md` and `.codex/CURRENT_TASK.md`, then create and build the KMP/CMP vertical slice.

## Relevant files

`docs/AUDIT.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, and `docs/adr/`.

