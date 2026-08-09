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
- Touch exploration exposes each hour as a semantic item; an equivalent textual detail exists for screen readers.
- RTL mirrors layout direction while chronological meaning and gestures remain understandable.

## Adaptive layout

- Compact width: single reading column and full-width timeline.
- Medium/expanded width: current conditions and insights remain primary; comparison or selected-hour detail uses a secondary pane.
- Large text may reflow vertically rather than clip or shrink core information.

## States

- Cache is shown with a discreet refresh indicator rather than blocking loading UI.
- Offline and stale states always include the last successful update age.
- Empty states have one clear next action: grant permission, search a city, or retry.

