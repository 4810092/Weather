# Development guide

This guide covers an unsigned contributor workflow. Production signing, store consoles, and release credentials are maintainer-only and are documented separately in [RELEASE.md](RELEASE.md).

## Toolchain

| Tool | Required or verified state |
| --- | --- |
| JDK | JDK 17 is the local baseline and the Xcode build script selects it. |
| Gradle | Use the checked-in Gradle 9.7.0 wrapper. Do not substitute a system Gradle. |
| Android | Android SDK 36; phone/tablet min SDK 24; Wear OS min SDK 30. |
| Apple | macOS and Xcode 26+; Xcode 26.6 with iOS/watchOS 26.5 SDKs is locally verified. |
| Python | Python 3.11 for the canonical local gate. |

The local and manually hosted fallback gates use the same JDK 17/Python 3.11
toolchain. The complete local gate additionally requires Pillow 12.2.0, `ffmpeg`/
`ffprobe`, three Android AVDs described in [Testing](TESTING.md), and Xcode for
the Apple portion. Run `bash scripts/local-ci.sh full`; use its scoped modes
while iterating.

`local.properties`, IDE metadata, build directories, signing material, and `.codex/` session state are intentionally ignored.

## First build

```sh
git clone https://github.com/4810092/Weather.git
cd Weather
./gradlew :app:assembleDebug
```

No API key or local secrets file is required. Nimbo uses the public Open-Meteo endpoints under the deployment limits in [PROVIDERS.md](PROVIDERS.md).

The first application screen lets you search for a city without granting location permission. Device location is optional and requests approximate foreground access only after a user action.

## Android

Open the repository root in Android Studio or build from the shell:

```sh
./gradlew :app:assembleDebug
./gradlew :wearApp:assembleDebug
```

The phone/tablet and Wear OS modules share the same application ID because they are delivered as form factors of the same Play application. Their version-code ranges are intentionally separate.

Useful source entry points:

- [MainActivity](../app/src/main/java/uz/ganikhodjaev/weather/MainActivity.kt)
- [NimboApplication](../app/src/main/java/uz/ganikhodjaev/weather/NimboApplication.kt)
- [Android location adapter](../shared/src/androidMain/kotlin/uz/ganikhodjaev/weather/shared/location/DeviceLocationProvider.android.kt)
- [Android surface publisher](../shared/src/androidMain/kotlin/uz/ganikhodjaev/weather/shared/WeatherSurfacePublisher.android.kt)

The normal release Gradle build is unsigned unless a maintainer supplies
signing outside the repository. Local or manually hosted CI artifacts are
explicitly unsigned and are not store releases.

## iOS and watchOS

The checked-in Xcode project can be opened directly:

```sh
open iosApp/Nimbo.xcodeproj
```

For a reproducible unsigned command-line build, use the dedicated simulator scheme:

```sh
xcodebuild \
  -project iosApp/Nimbo.xcodeproj \
  -scheme NimboSimulator \
  -configuration Release \
  -sdk iphonesimulator \
  -destination 'generic/platform=iOS Simulator' \
  CODE_SIGNING_ALLOWED=NO \
  ARCHS=arm64 \
  ONLY_ACTIVE_ARCH=YES \
  build
```

Build the watchOS companion without signing:

```sh
xcodebuild \
  -project iosApp/Nimbo.xcodeproj \
  -scheme NimboWatch \
  -configuration Release \
  -sdk watchsimulator \
  -destination 'generic/platform=watchOS Simulator' \
  CODE_SIGNING_ALLOWED=NO \
  ARCHS=arm64 \
  ONLY_ACTIVE_ARCH=YES \
  build
```

The `NimboSimulator` target embeds WidgetKit but deliberately omits the watch companion so a generic iOS Simulator build does not require a paired watch destination. The `Nimbo` device/archive scheme requires Apple signing and is not a contributor prerequisite.

The iOS app and home-screen widget both target iOS 15. Accessory widget
families are registered only on iOS 16 and later, while the removable WidgetKit
container background is used on iOS 17 and later with an iOS 15–16 background
fallback. A successful lower-deployment build proves API compatibility, not
runtime rendering on an unavailable older simulator.

`iosApp/project.yml` is the human-reviewable XcodeGen definition. The generated `Nimbo.xcodeproj` is also committed so XcodeGen is not required for a first build. If a change regenerates the project, review and commit both the definition and the resulting project changes.

## Shared code workflow

Most behavior starts in:

- [NimboApp](../shared/src/commonMain/kotlin/uz/ganikhodjaev/weather/shared/NimboApp.kt) for composition and lifecycle-driven refresh;
- [WeatherStateHolder](../shared/src/commonMain/kotlin/uz/ganikhodjaev/weather/shared/presentation/WeatherStateHolder.kt) for UI state/actions;
- [WeatherRepository](../shared/src/commonMain/kotlin/uz/ganikhodjaev/weather/shared/data/WeatherRepository.kt) for cache/network coordination;
- [WeatherScreen](../shared/src/commonMain/kotlin/uz/ganikhodjaev/weather/shared/ui/WeatherScreen.kt) for shared Compose UI;
- [Weather.sq](../shared/src/commonMain/sqldelight/uz/ganikhodjaev/weather/db/Weather.sq) for persistence.

Prefer deterministic unit tests for domain/mapping changes and host tests for actual SQLite driver/migration behavior. See [TESTING.md](TESTING.md).

## Common problems

### Wrong Java version during Xcode builds

The Xcode pre-build script resolves JDK 17 with `/usr/libexec/java_home -v 17`. Install a JDK 17 distribution visible to that command; setting only an IDE-specific JDK may not be enough.

### Missing Android SDK 36

Install Android SDK Platform 36 and current build tools through Android Studio’s SDK Manager, then ensure `local.properties` points to the SDK. Do not commit that file.

### Signing errors

Use `NimboSimulator` with `CODE_SIGNING_ALLOWED=NO` for contributor builds. Do not modify production bundle identifiers, team IDs, or entitlements merely to make a local device build sign.

### Provider or location test data

Do not commit a personal application database or precise coordinates. Reproduce with a searched city, fixed coordinate constants already used by tests, or a new synthetic fixture.
