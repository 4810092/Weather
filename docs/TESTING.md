# Testing and validation

Nimbo combines deterministic tests, repository policy scripts, cross-platform compilation, and manual release evidence. The scopes are intentionally separated so a passing unit suite is not mistaken for completed device or store QA.

## Automated inventory

The source tree keeps common Kotlin tests, Android-host persistence/migration
tests, Android app unit tests, and iOS-specific tests in their native source
sets. Common tests execute for both Android host and iOS Simulator. Use the
Gradle/JUnit reports from the current commit as the authoritative count instead
of copying a number into this document. The Python validation suite is likewise
discovered dynamically with `python3 -m unittest discover -s
scripts/growth/tests -p 'test_*.py'`; its `Ran N tests` summary is authoritative.

| Area | Current evidence |
| --- | --- |
| Provider decoding/mapping | Ktor mock-engine city search/fallback; complete-row truncation; optional-array defaults; air-quality mapping. |
| Domain | Weather comparison, upcoming rain/temperature changes, two-hour outdoor scoring/hazards. |
| Time | IANA timezone conversion, spring/fall DST, local-day boundaries, ±24-hour timeline selection. |
| Privacy boundary | Positive and negative coordinates rounded symmetrically before use. |
| Presentation helpers | Unit preference/conversion, theme preference parsing, dark color contrast. |
| Growth paths | First-run state and UZ quick cities, denied/disabled/unavailable location outcomes, review retry/once-per-version rules, canonical share links, transient background retry classification, and stale activation/refresh race rejection. |
| Persistence | Saved-location/cache retention with the SQLite driver; released v1 fixture migration and retained data. |

The current tree contains direct `WeatherStateHolder` race tests, but it does not contain Compose UI automation tests, screenshot-golden tests, or end-to-end live-provider tests. Those are known gaps; [QUALITY.md](QUALITY.md) and [QA_MATRIX.md](QA_MATRIX.md) distinguish manual evidence from automation.

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
python3 scripts/check_store_previews.py
python3 scripts/check_dashboard_report.py
python3 scripts/build_site.py --output build/pages-check
python3 scripts/build_site.py --output build/pages-drafts-check --include-drafts
git diff --check
```

Run the checks that cover your change locally; CI runs the complete pull-request set.

## Clean Android/shared gate

```sh
./gradlew clean ktlintCheck \
  :shared:allTests \
  :shared:testAndroidHostTest \
  :app:testDebugUnitTest \
  :wearApp:testDebugUnitTest \
  :shared:verifySqlDelightMigration \
  :app:assembleDebug \
  :app:lintRelease \
  :app:bundleRelease \
  :wearApp:assembleDebug \
  :wearApp:lintRelease \
  :wearApp:bundleRelease
```

The explicit release-lint tasks cover the full Android Lint surface; the release
bundles separately exercise R8/resource shrinking and lint-vital tasks. They are
unsigned development artifacts unless maintainer signing is supplied outside Git.

The phone and Wear unit-test tasks both execute the shared Android surface contract. Fixed timestamps cover empty and partial payloads, real zero values, the strict six-hour stale boundary, bounded clock skew, malformed future timestamps, and the visibility flags consumed by both UIs.

## Apple gate

Run `bash scripts/test_ios_surfaces.sh` for the deterministic Swift Empty/Fresh/Stale contract. Its 18 XCTest cases cover missing and malformed payloads, strict integer storage types, valid zero values, AQI sentinels, daily-range consistency, the strict six-hour boundary, bounded future clock skew and clock rollback, cache clearing, and WidgetKit's cache-only boundary reload date.

The unsigned iOS and watchOS commands are documented in [DEVELOPMENT.md](DEVELOPMENT.md) and mirror the two CI builds. The macOS job runs both `:shared:iosSimulatorArm64Test` and the Swift surface suite, then retains the shared Kotlin JUnit XML and HTML report for seven days.

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

`.github/workflows/ci.yml` runs on every pull request and pushes to `master`, uses read-only repository permissions, cancels superseded runs for the same ref, and applies job timeouts. Android unsigned release bundles and iOS Simulator test results are retained for seven days as diagnostic artifacts. The macOS job also builds iOS/WidgetKit and watchOS without signing.
