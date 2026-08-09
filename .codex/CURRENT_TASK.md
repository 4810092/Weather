# Current task

## Goal

Add production units, localization, RTL, and adaptive/accessibility behavior to the green product flow.

## Acceptance criteria

- Android application ID remains `uz.ganikhodjaev.weather`.
- Automatic, metric, and imperial units convert only at the presentation boundary.
- English, Russian, Arabic, Spanish, French, German, Portuguese, Simplified Chinese, Japanese, Korean, Hindi, Turkish, and Uzbek user-facing strings exist.
- Arabic layout direction, timeline behavior, selected-hour affordances, and large font scale are verified.
- Location/refresh failures are localized semantic states rather than domain-authored sentences.
- Cache-first behavior and both platform builds stay green.

## Affected areas

Shared resources/settings/presentation/UI, SQLDelight settings migration, conversion tests, and platform UI smoke tests.

## Checks

Shared tests; Android debug/release build; iOS simulator build and launch; permission-denied and offline smoke tests.
