# Product design principles

Nimbo uses calm, information-first surfaces with restrained weather ambience. It is not a card dashboard and does not copy Apple Weather or Google Weather.

## Visual language

- Large current conditions establish the first reading point.
- A soft atmospheric gradient reflects daylight and condition without reducing text contrast.
- Typography, spacing, shapes, semantic colors, and motion are tokenized in the shared design system.
- Past timeline data is quieter; future data has stronger contrast; now is the fixed visual anchor.
- Motion communicates selection and state change, never gates content, and respects reduced-motion settings.

## Timeline interaction

- One horizontally scrollable plot, not 48 large cards.
- Temperature curve, compact condition markers, precipitation, hour labels, selected hour, and now marker share a consistent time scale.
- Tap selects and centers an hour. A normal swipe browses without changing selection; hold then drag explores visible hours and centers on release. “Current hour” resets selection. Each known hour remains a screen-reader button with full text; gaps are announced without inventing a value.
- RTL mirrors surrounding content but keeps the time axis chronological from left to right.
- Sunrise/sunset for the selected city and date choose sun/moon symbols; invalid or stale solar data uses a neutral symbol. Whole-day summaries use neutral weather symbols. The atmospheric palette respects the explicitly selected light/dark theme.

## Adaptive layout

- Compact width: single reading column and full-width timeline.
- At 720dp and above (normal text), selected-hour detail and walk advice share a row. Content stops growing at 1120dp. Larger text restores a single column.
- Large text may reflow vertically rather than clip or shrink core information.

## States

- Cache is shown with a discreet refresh indicator rather than blocking loading UI.
- Offline and stale states always include the last successful update age.
- Empty states have one clear next action: grant permission, search a city, or retry.


The city name is the primary place switch. Refresh and settings remain fixed, accessible header actions; share and source/update attribution live below the forecast. A failed refresh preserves usable content with a visible timestamped warning. Short transitions (140ms) run only on state changes and are disabled by Reduce Motion; no idle visual animation runs on the forecast.
