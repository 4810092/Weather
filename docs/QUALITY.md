# Quality strategy

## Automated gates

- Formatting and static analysis.
- Common/domain tests for comparisons, insights, comfort scoring, unit conversions, weather-code mapping, timezones, DST, and date boundaries.
- Data tests for decoding, mapping, cache policy, stale/fresh behavior, failures, snapshots, and migrations.
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

