# Localization status

English is the canonical source locale in Compose Multiplatform resources.

Locale overlays currently exist for Russian, Arabic, Spanish, French, German, Portuguese, Simplified Chinese, Japanese, Korean, Hindi, Turkish, and Uzbek. The first-run flow, primary controls, current conditions, timeline heading, recent-days heading, units heading, and outside-time states are localized. Secondary insight/reason/hazard strings still fall back to English in overlays that do not yet override them; this must be closed and reviewed by native speakers before release.

The app follows the system language. Android per-app language metadata is intentionally not enabled yet; the published app identity caused the Play-enabled QA emulator to replace/remove debug builds signed with the debug certificate, so per-app locale switching could not be evaluated reliably there.

## Release gates

- Complete every resource key in all 12 overlays.
- Review translations in context with native speakers.
- Run Arabic on a non-Play API 36 emulator and an iOS simulator/device.
- Verify mirrored timeline direction and gestures, selected-hour placement, numerals, time formatting, and icons.
- Verify 200% font scale and narrow phone layouts in every script family.
