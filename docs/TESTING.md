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
| Compose UI | Android device-test coverage for no-auto-location onboarding, denied-location city search, forecast/tip/header semantics, cached-error retry, Uzbek LTR, Arabic RTL, and Russian UI at 200% font scale. |

The Compose suite renders deterministic production `WeatherScreen` states; it
does not call the live provider and does not replace signed physical-device or
assistive-technology QA. Screenshot-golden and end-to-end live-provider tests
remain known gaps. [QUALITY.md](QUALITY.md) and [QA_MATRIX.md](QA_MATRIX.md)
distinguish emulator automation from manual evidence.

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

Run only the targeted checks that help during development. Before integration,
`bash scripts/local-ci.sh full` is the complete locally reproducible gate.
GitHub-hosted CI is not the routine authority and is not started by pushes or
pull requests.

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

The unsigned iOS and watchOS commands are documented in [DEVELOPMENT.md](DEVELOPMENT.md).
`bash scripts/local-ci.sh apple` runs both `:shared:iosSimulatorArm64Test`, the
Swift surface suite, and the two unsigned simulator builds.

## Android Compose UI gate

The `androidDeviceTest` source set uses the AndroidJUnitRunner and Compose UI
test v2. `bash scripts/local-ci.sh android-ui` runs
`:shared:connectedAndroidDeviceTest` sequentially on a local API 24 phone, API
36 phone, and API 36 tablet AVD. The runner auto-selects matching AVDs. Override
them with `NIMBO_AVD_PHONE_API24`, `NIMBO_AVD_PHONE_API36`, and
`NIMBO_AVD_TABLET_API36` when needed; a missing exact form factor/API fails
closed rather than silently reducing coverage.

The suite verifies deterministic UI behavior and semantics only. Emulator
success is not upload signing, Play delivery, physical phone/tablet evidence,
TalkBack gesture/audio proof, widget runtime proof, or Wear OS pairing.

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

`scripts/local-ci.sh` is the canonical ordinary CI entrypoint. `core`,
`android-ui`, and `apple` correspond to the former hosted jobs; `full` runs all
three. The Android emulator runner uses a portable TERM-then-KILL timeout and
writes local diagnostics below `build/android-ui-diagnostics`.

`.github/workflows/ci.yml` has only a manual trigger and must not be dispatched
for routine validation. It remains a separately authorized hosted fallback,
keeps read-only repository permissions, and delegates its core and Apple work
to the same local script to prevent command drift. Automatic GitHub execution
is reserved for capabilities that need a hosted trust boundary, OIDC, or the
unattended canonical rank writer. The former Trusted-to-Pages chain is dormant;
restoring a manual Pages publication path is a separately authorized workflow
change. The Gradle wrapper validates the official 9.7.0 distribution SHA-256,
and normal task resolution enforces the checked-in dependency verification
metadata.

`.github/workflows/signed-candidate.yml` is a distinct manual, environment-
protected GitHub-hosted path for maintainer release bytes. It never runs for a
pull request or push, accepts only `4810092/Weather` `master`, keeps
`contents: read`, and separates an exact-source unsigned build job with no
secrets from a fresh protected signing job. The first job transfers only a
checksummed inert unsigned package retained for one day. All third-party
actions are pinned to full reviewed commits; the repository validator binds
complete action blocks, run bodies, shells, exact secret environments, and
upload paths. The final job uploads only a receipt-bound signed tarball and
receipt after phone, Wear OS, Apple archive/IPA, profile, signer, Bundletool,
source-revision, closed-tree, mapping, and dSYM checks all pass. Ordinary
contributors and local CI never receive signing material.

No mutable repository script executes on the protected runner while secret
files or the unlocked ephemeral Keychain exist. The verifier scripts are
checked against reviewed SHA-256 pins before signing, copied outside the
checkout, rehashed after signing material is destroyed, and launched with
isolated Python path handling. The verifier rejects either detached-build or
current-checkout release-source drift from the manifest revision.
