# Localization

Nimbo ships 13 languages: English plus complete overlays for Arabic, German, Spanish, French, Hindi, Japanese, Korean, Portuguese, Russian, Turkish, Uzbek, and Simplified Chinese.

## Resource ownership

English Compose Multiplatform resources in `shared/src/commonMain/composeResources/values/` are canonical. The same locale set is maintained for:

- shared Compose strings and accessibility summaries;
- Android application widget strings;
- Wear OS strings;
- iOS location-permission descriptions;
- WidgetKit and watchOS surface strings;
- store metadata and localized screenshot sets.

User-facing state carries semantic message identifiers rather than preformatted English errors. Time formatting uses platform formatters with the selected location’s IANA timezone. SI values are converted only at the presentation boundary, and relative-day labels use plural resources rather than sentence concatenation.

Manual city search sends the active app language to Open-Meteo. If the localized search returns no matches, it retries once in English; it does not fan out across every supported language. Reverse-geocoded device-place labels use the platform locale when available.

## Automated parity check

```sh
python3 scripts/check_localizations.py
```

The script checks canonical keys, string/plural resource types, positional placeholders, every Android app/Wear overlay, all iOS permission localizations, and Apple widget/watch surface keys. It currently reports 102 canonical Compose resources, 12 translated overlays, and 13 Apple/permission locale sets.

The script proves structural completeness, not translation quality. Native-language review and in-context screenshots remain necessary.

## RTL and chronological data

Arabic sets the surrounding Compose layout to RTL. The hourly and recent-day chronological rows install a local LTR direction so past-to-future meaning remains left-to-right and gestures do not reverse the time axis. Text inside each semantic description stays localized.

This is an explicit product decision, not an automatic Compose default. Changes to the timeline must test Arabic selection, scrolling, focus order, localized time, and surrounding mirrored controls.

## Contribution rules

- Update every production overlay when adding or removing a canonical resource.
- Preserve positional placeholders and resource type.
- Translate a complete idea; do not construct sentences by concatenating fragments.
- Keep provider/product terminology consistent with the privacy and attribution docs.
- Do not use machine translation output as proof of correctness without review.
- Include an in-context screenshot for a correction that depends on truncation, layout, or script rendering.

## Release QA

- Exercise at least one representative device size for each major script family.
- Verify Arabic RTL, selected-hour placement, and chronological direction.
- Check localized numerals/time, IANA timezone behavior, and a DST boundary where applicable.
- Check 200% Android font scale and an iOS accessibility Dynamic Type size.
- Verify TalkBack/VoiceOver summaries rather than only visible text.
- Re-run store metadata/screenshot checks when production locale material changes.
