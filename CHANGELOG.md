# Changelog

This file records public product and repository checkpoints supported by source history and the release journal. Android, Apple, and watch surfaces do not yet share one synchronized public-store version, so entries state their scope explicitly.

## Unreleased

- Fix the Wear OS review blockers by using a pure-black app background and a
  policy-sized branded launch icon, and advance the Wear OS build to version
  code 1000007.
- Improve open-source onboarding, architecture/reference documentation, contributor workflows, dependency updates, CI hardening, and security reporting.
- Add GitHub prerelease objects for the existing `v1.0.0-rc.1` and `v1.0.0-rc.2` tags without changing tag history.

## iOS 1.0.1 — submitted 2026-08-23

- Submit App Store build 4 with the iOS/iPadOS app, WidgetKit extension, and
  Apple Watch companion for review.
- Add the Apple Watch product-page screenshot and localized release notes for
  all supported App Store localizations.
- Enable automatic full release after Apple approval. The submission is waiting
  for review and is not yet recorded as live.

## Android 1.0.2 — 2026-08-13

- Record the completed Google Play phone/tablet production rollout of version code 6.
- Add Android home-screen widget and constrained WorkManager refresh.
- Add Wear OS, WidgetKit, and watchOS companion surfaces to the source tree and release candidate.
- Add daily forecast and air-quality persistence, migrations, and localized surface resources.

Apple build 3 from this checkpoint was distributed through external TestFlight; it is not recorded as an App Store production release. Wear OS production review and paired physical-device QA remained open at the dated checkpoint.

## Android 1.0.0 — 2026-08-10

- Replace the legacy Android-only implementation with the Nimbo Kotlin Multiplatform application.
- Share Compose UI, presentation state, domain engines, networking, SQLDelight persistence, and localization across Android and iOS.
- Add offline-first cached rendering, manual/optional device location, deterministic insights, units, 13 locales, RTL, adaptive UI, accessibility semantics, CI, privacy/store materials, and release gates.
- Verify a Google Play upgrade from the legacy production application ID and publish Android version code 4.

## `v1.0.0-rc.2` — 2026-08-10

- Mark Android location hardware optional so the manual-city flow remains installable on devices without location hardware.
- Preserve the tested app identity and record the Play internal-upgrade gate.

This tag is a release candidate, not a production release.

## `v1.0.0-rc.1` — 2026-08-10

- First tagged Nimbo KMP release candidate with shared Android/iOS UI, offline persistence, insights, localization, privacy documentation, CI, and store preparation.

This tag is a release candidate, not a production release.

## `legacy-android-v1.0.1`

- Recovery checkpoint for the pre-Nimbo Android-only application.
- Retained for history and upgrade verification; not a supported Nimbo release line.
