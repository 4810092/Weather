# Privacy

Nimbo is designed without accounts, ads, analytics, or background location.

## Data flow

- Foreground approximate location is requested only after an explanatory screen and explicit user action.
- Coordinates are sent to the selected weather provider to retrieve weather. Manual city queries are sent to the geocoding provider.
- The active place, cached weather, forecast snapshots, unit/theme settings, and refresh metadata are stored locally on the device.
- Nimbo does not retain a location trail and does not continuously access location in the background.
- No data is sold and no cross-app tracking SDK is included.

Provider network logs and policies still apply to requests. Store privacy declarations and the published policy must be updated if telemetry, a different provider, or new data collection is introduced.

This document is an engineering source of truth, not a substitute for jurisdiction-specific legal review.

