# Project state

Last updated: 2026-08-09

## Current phase

Phase 0-3: audit, product definition, research, and architecture decisions.

## Implemented

- Legacy audit and recovery tag `legacy-android-v1.0.1`.
- Production Android identity and signing certificate fingerprint recorded.
- Baseline product, design, architecture, privacy, quality, release, roadmap, and ADR documentation.

## Verified

- Baseline commit `8fcefb8` builds with `./gradlew test assembleDebug` on Java 17.
- Legacy AAB signature verifies and its certificate fingerprint is documented.
- Local toolchain includes Xcode 26.6, Swift 6.3.3, Android SDK 36, and iOS simulators.

## Known issues

- OpenWeather key is exposed in Git history and must be revoked/rotated by the credential owner.
- No signing keystore/config is available locally; Play App Signing and upload identity remain unverified.
- Apple App ID/account state remains unverified.
- Pre-existing `.idea` worktree changes belong to the user and remain untouched.

## Current release versions

- Legacy Android: 2 / 1.0.1.
- Nimbo target: Android version code greater than Play production; iOS 1.0 build 1 or greater.

## Last known green commit

`8fcefb8` (legacy baseline).

## Store status

- Google Play listing exists externally; access and current production configuration not yet verified.
- App Store listing does not yet exist per product brief.

## Important commands

- `./gradlew test assembleDebug`
- `xcodebuild -version`
- `git status --short --branch`

## Next steps

1. Commit audit/research documentation without staging `.idea` changes.
2. Replace the Android-only build with a KMP/CMP vertical slice while preserving the application ID.
3. Build Android and iOS targets before expanding features.

