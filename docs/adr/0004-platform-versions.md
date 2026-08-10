# ADR 0004: Platform and toolchain baseline

Status: accepted  
Date: 2026-08-09

## Decision

- Android min SDK 26, compile/target SDK 36.
- iOS deployment target 15.0 for iPhone and iPad.
- Production toolchain starts from stable Kotlin 2.4.10 and Compose Multiplatform 1.11.1, subject to dependency compatibility validation during the foundation build.
- Xcode 26+ and iOS 26 SDK are required for App Store archives.

## Rationale

Compose Multiplatform 1.11.1 supports Android 5+ and iOS 14+, and Android/iOS targets are stable. Keeping Android 26 preserves the legacy audience while avoiding additional compatibility work below the existing minimum. The selected current networking, persistence, and UI artifacts are compiled for iOS 15, so Nimbo uses iOS 15 as its verified floor instead of carrying linker-version mismatches. Google Play's 2026 submission deadline requires API 36.

## Consequences

CI needs Linux/Android and macOS/iOS jobs. Stable-version compatibility is verified by actual Android and iOS builds; a dependency incompatibility may justify pinning the newest compatible stable Kotlin patch and updating this ADR.
