# Nimbo

Nimbo is a Kotlin Multiplatform weather app for Android and iOS. Its main idea is simple: future weather is easier to understand when it is compared with weather you recently felt. Alongside the hourly forecast, Nimbo shows yesterday comparisons, recent context, and a deterministic Best Time Outside recommendation.

The app is offline-first. SQLDelight is the UI source of truth; network refreshes write normalized weather data to the local database before the interface observes an update. No account, ads, analytics, or background location are included.

## Build

Requirements:

- JDK 17 or newer and Android SDK 36
- Xcode 26 or newer for iOS
- macOS for the iOS application

Android debug build:

```sh
./gradlew :app:assembleDebug
```

iOS Simulator build:

```sh
xcodebuild \
  -project iosApp/Nimbo.xcodeproj \
  -scheme Nimbo \
  -sdk iphonesimulator \
  -destination 'generic/platform=iOS Simulator' \
  CODE_SIGNING_ALLOWED=NO build
```

Run the production gates locally:

```sh
python3 scripts/check_localizations.py
python3 scripts/check_repository.py
python3 scripts/check_store_metadata.py
python3 scripts/check_store_assets.py
./gradlew ktlintCheck :shared:allTests :shared:testAndroidHostTest \
  :shared:verifySqlDelightMigration :app:bundleRelease
```

## Screenshots

| Phone | Tablet |
| --- | --- |
| ![Nimbo hourly weather on a phone](store/screenshots/google-play/phone-en/03-details.png) | ![Nimbo adaptive two-column weather layout on a tablet](store/screenshots/google-play/tablet-en/01-overview.png) |

## Project map

- `shared/` — shared domain, data, SQLDelight, Compose UI, resources, and tests
- `app/` — Android application shell
- `iosApp/` — iOS application shell and Xcode project
- `docs/` — product, architecture, privacy, quality, release, and ADR documentation

See [Architecture](docs/ARCHITECTURE.md), [Localization](docs/LOCALIZATION.md), [Privacy](docs/PRIVACY.md), and [Contributing](CONTRIBUTING.md).

Weather and place search are provided by [Open-Meteo](https://open-meteo.com/); its geocoding service is based on [GeoNames](https://www.geonames.org/). Provider terms and deployment constraints are documented in [Provider attribution](docs/PROVIDERS.md).

Licensed under Apache-2.0.
