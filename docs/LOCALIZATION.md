# Localization

English is the canonical source locale in Compose Multiplatform resources. Complete overlays ship for Russian, Arabic, Spanish, French, German, Portuguese, Simplified Chinese, Japanese, Korean, Hindi, Turkish, and Uzbek.

User-facing state carries semantic message identifiers, never preformatted English errors, so error, retry, offline, search, and permission paths resolve through the same localized resources. Time is formatted by the platform locale while applying the selected city's IANA timezone. Units are converted only at the presentation boundary. Relative-day labels use plural resources rather than sentence concatenation.

Manual city search sends the active app language to Open-Meteo so matching place names and returned labels are localized. If that search has no matches, Nimbo retries once in English; it does not fan out requests across every supported language.

City and country labels resolved from device coordinates use the platform locale when the system geocoder can provide them. The localized "current location" label remains the fallback when no place name is available.

Run `python3 scripts/check_localizations.py` to compare every overlay with the canonical set, including resource types and positional placeholders. The same check verifies all 13 localized iOS location-permission descriptions in `InfoPlist.strings`. CI runs the command, so a new canonical resource without every production translation or a missing system permission localization fails the build.

## Release QA

- Review translations in context with native speakers before store submission.
- Run Arabic on a non-Play API 36 emulator and iOS Simulator/device.
- Chronological weather data remains past-to-future from left to right in all locales; surrounding controls and text follow RTL. This avoids reversing the meaning of the time axis merely because the reading direction changes.
- Verify selected-hour placement, localized numerals/time, icons, 200% font scale, and narrow layouts for every script family.
