# Quality strategy

## Automated gates

- Formatting and static analysis.
- Common/domain tests for comparisons, insights, comfort scoring, unit conversions, weather-code mapping, timezones, DST, and date boundaries.
- Data tests for decoding, mapping, cache policy, stale/fresh behavior, failures, snapshots, and migrations.
- `ReleasedDatabaseMigrationTest` runs against `nimbo-v1.db`, captured from a real API 36 launch of commit `63092bb` after selecting approximate device location and syncing 216 hourly rows. The fixture has SQLite `user_version=1`, one active location, 216 weather rows, and 216 forecast snapshots; it does not contain the later `app_setting` table.
- SQLDelight migration parity is also checked against the committed versioned schema by `verifySqlDelightMigration`; both checks run from a clean build in CI.
- State-holder tests for onboarding, permission, cached/offline, refresh, retry, and location changes.
- Android and iOS compilation on pull requests; release builds on release candidates.
- Critical UI flows and screenshot coverage for light, dark, Arabic RTL, large text, phone, and tablet when the selected tooling is stable on both targets.

## Manual release matrix

Clean install, install-over-production, foreground/background, process death, permission grant/deny/permanent deny, disabled location services, offline, slow network, provider failure, stale cache, locale/RTL, theme, font scale, screen reader, phone, tablet, iPhone, and iPad.

## Performance budgets

- Startup does not wait for history sync.
- Cached weather renders before network refresh.
- Timeline avoids per-frame allocations and unnecessary recomposition.
- Historical and snapshot maintenance run after primary current/hourly work.

## RTL and accessibility evidence

- Arabic was exercised on the non-Play API 36 `Nimbo_API_36` Android emulator and an iPhone 16 Pro / iOS 18.5 Simulator. On both platforms surrounding content follows RTL while the chronological timeline remains left-to-right by product decision.
- Timeline hours are individually focusable buttons with localized semantic weather summaries and selected state. The timeline is not exposed only as decorative pixels.
- Android 200% font scale was exercised on the emulator; the screen remains vertically scrollable and primary content does not overlap.

Simulator evidence does not replace final TalkBack/VoiceOver testing on release-signed builds and real devices. Those checks remain required in the release QA matrix.
