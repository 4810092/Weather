# Testing and validation

Nimbo combines deterministic tests, repository policy scripts, cross-platform compilation, and manual release evidence. The scopes are intentionally separated so a passing unit suite is not mistaken for completed device or store QA.

## Automated inventory

As of August 16, 2026, the source tree contains 30 unique `@Test` functions:

- 28 common tests, executed for Android host and iOS Simulator;
- one Android-host location-retention/persistence test;
- one Android-host released-database migration test.

Running both relevant test tasks produces 58 cross-target test executions. The count is descriptive and should be updated when tests change; coverage quality matters more than preserving the number.

| Area | Current evidence |
| --- | --- |
| Provider decoding/mapping | Ktor mock-engine city search/fallback; complete-row truncation; optional-array defaults; air-quality mapping. |
| Domain | Weather comparison, upcoming rain/temperature changes, two-hour outdoor scoring/hazards. |
| Time | IANA timezone conversion, spring/fall DST, local-day boundaries, ±24-hour timeline selection. |
| Privacy boundary | Positive and negative coordinates rounded symmetrically before use. |
| Presentation helpers | Unit preference/conversion, theme preference parsing, dark color contrast. |
| Persistence | Saved-location/cache retention with the SQLite driver; released v1 fixture migration and retained data. |

The current tree does not contain direct `WeatherStateHolder` tests, Compose UI automation tests, screenshot-golden tests, or end-to-end live-provider tests. Those are known gaps; [QUALITY.md](QUALITY.md) and [QA_MATRIX.md](QA_MATRIX.md) distinguish manual evidence from automation.

## Fast contributor checks

For a common Kotlin/domain/data change:

```sh
./gradlew ktlintCheck \
  :shared:allTests \
  :shared:testAndroidHostTest \
  :shared:verifySqlDelightMigration
```

For documentation, resources, provider, privacy, or store inputs:

```sh
python3 scripts/check_repository.py
python3 scripts/check_localizations.py
python3 scripts/check_store_metadata.py
python3 scripts/check_store_assets.py
git diff --check
```

Run the checks that cover your change locally; CI runs the complete pull-request set.

## Clean Android/shared gate

```sh
./gradlew clean ktlintCheck \
  :shared:allTests \
  :shared:testAndroidHostTest \
  :shared:verifySqlDelightMigration \
  :app:assembleDebug \
  :app:bundleRelease \
  :wearApp:assembleDebug \
  :wearApp:bundleRelease
```

The release bundles exercise R8/resource shrinking and lint-vital tasks. They are unsigned development artifacts unless maintainer signing is supplied outside Git.

## Apple gate

The unsigned iOS and watchOS commands are documented in [DEVELOPMENT.md](DEVELOPMENT.md) and mirror the two CI builds. `:shared:allTests` also links and runs the iOS Simulator common test binary on macOS.

## SQLDelight migrations

Schema changes require both migration layers:

- `:shared:verifySqlDelightMigration` verifies migration/schema parity;
- `:shared:testAndroidHostTest` includes [ReleasedDatabaseMigrationTest](../shared/src/androidHostTest/kotlin/uz/ganikhodjaev/weather/shared/data/ReleasedDatabaseMigrationTest.kt), which migrates `nimbo-v1.db` with the production Android driver path.

Do not replace a released fixture with a database produced only from the new schema; that would stop testing the upgrade boundary. New fixtures must be synthetic or sanitized.

## Manual validation

UI changes should be checked for:

- cached and first-run states;
- online, offline, stale, and provider-failure behavior;
- optional location grant/deny/disabled services and manual search;
- light/dark appearance and increased contrast;
- large text and narrow/expanded layouts;
- Arabic RTL with a left-to-right chronological timeline;
- TalkBack/VoiceOver semantics and selected-hour activation;
- widget/watch parity when the compact snapshot changes.

Simulator/emulator evidence is useful but does not prove physical-device battery behavior, Bluetooth/watch handoff, actual background scheduling cadence, VoiceOver gestures/audio, store delivery, or signing. The dated [QA matrix](QA_MATRIX.md) records which release checks were actually performed.

## CI behavior

`.github/workflows/ci.yml` runs on every pull request and pushes to `master`, uses read-only repository permissions, cancels superseded runs for the same ref, and applies job timeouts. Android unsigned release bundles are retained for seven days as diagnostic artifacts. The macOS job builds iOS/WidgetKit and watchOS without signing.
