# Project state

Last updated: 2026-08-09

## Current phase

Phase 4: KMP/CMP foundation and product vertical slice.

## Implemented

- Legacy audit and recovery tag `legacy-android-v1.0.1`.
- Production Android identity and signing certificate fingerprint recorded.
- Baseline product, design, architecture, privacy, quality, release, roadmap, and ADR documentation.
- KMP shared module targeting Android, iOS device, and iOS simulator.
- Separate Android application shell and UIKit iOS shell rendering shared Compose UI.
- Open-Meteo forecast/geocoding client, normalized weather domain, SQLDelight cache, and snapshot retention.
- Cache-first weather state with explicit loading, content, refresh, stale, offline, and empty-error presentation.
- Shared current-weather screen and interactive -24/+24-hour timeline.
- Legacy tracked AAB removed from the open-source branch because it embeds the revoked/rotated credential candidate; it remains recoverable from the legacy tag.

## Verified

- Baseline commit `8fcefb8` builds with `./gradlew test assembleDebug` on Java 17.
- Legacy AAB signature verifies and its certificate fingerprint is documented.
- Local toolchain includes Xcode 26.6, Swift 6.3.3, Android SDK 36, and iOS simulators.
- `./gradlew :shared:allTests :app:assembleDebug` succeeds on the Nimbo branch.
- iOS app builds with `xcodebuild` and launches on an iPhone 16 Pro iOS 18.5 simulator.
- Live Open-Meteo data rendered successfully in the iOS simulator.

## Known issues

- OpenWeather key is exposed in Git history and must be revoked/rotated by the credential owner.
- No signing keystore/config is available locally; Play App Signing and upload identity remain unverified.
- Apple App ID/account state remains unverified.
- Pre-existing `.idea` worktree changes belong to the user and remain untouched.

## Current release versions

- Legacy Android: 2 / 1.0.1.
- Nimbo target: Android version code greater than Play production; iOS 1.0 build 1 or greater.

## Last known green commit

`f2b26f5` plus the current foundation working tree. Replace with the foundation commit after it is created.

## Store status

- Google Play listing exists externally; access and current production configuration not yet verified.
- App Store listing does not yet exist per product brief.

## Important commands

- `./gradlew :shared:allTests :app:assembleDebug`
- `xcodebuild -project iosApp/Nimbo.xcodeproj -scheme Nimbo -sdk iphonesimulator -configuration Debug CODE_SIGNING_ALLOWED=NO build`
- `xcodebuild -version`
- `git status --short --branch`

## Next steps

1. Commit the green KMP/CMP foundation without staging `.idea` changes.
2. Replace the temporary Tashkent bootstrap with onboarding, city search, and platform location permission flows.
3. Implement deterministic insight and best-time-outside engines with shared tests.
