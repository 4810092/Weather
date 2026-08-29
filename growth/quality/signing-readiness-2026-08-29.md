# Current-source signing readiness — 2026-08-29

Status: **BLOCKED for Android phone and Apple; VERIFIED-CURRENT for the
unchanged Wear OS artifact**. No artifact was uploaded, submitted, or
published during these checks.

## Android phone and Wear OS

- Fresh release bundles build successfully as phone `1.1.0 (8)` and Wear OS
  `1.1.0 (1000008)`, but the Gradle release variants have no signing
  configuration and the fresh outputs are unsigned.
- An isolated exact-HEAD rebuild at commit
  `80cdd608b93056edd05e29873da43834a916cd3a` produced the unsigned phone AAB
  SHA-256
  `12da2a0d69d6ff5b5925a03cec419d7ae988e1092b5748f0662c795ea31771cc`.
  Bundletool 1.18.3 validation passed; its manifest reports package
  `uz.ganikhodjaev.weather`, version `1.1.0 (8)`, minSdk 24, and targetSdk 36.
  Jarsigner explicitly reports that this AAB is unsigned. The ignored local
  copy is retained as
  `build/release/nimbo-phone-1.1.0-vc8-unsigned-head.aab`; it is not a release
  candidate and is not referenced by the upload manifest.
- The expected upload keystore exists outside the repository with owner-only
  permissions. Both password items are present in the login Keychain, but
  exact account-and-service lookups that request their values make the
  `security` command exit with status `51`. A second value-only attempt during
  the isolated exact-HEAD build produced the same empty result. No password
  value was printed, persisted, passed in an argument, or made available to
  the build environment.
- A signed phone vc8 artifact therefore does not exist. The previous phone vc7
  signature and physical smoke remain historical evidence only.
- The unchanged, retained Wear OS vc1000008 AAB remains the current signed
  artifact with SHA-256
  `ac19a0eab1a60554db309166f135e754c97205b79c4f5182164a8b21594e7dc6`.
  Its AAB signature and retained universal APK signature still verify, but it
  has no physical-watch result and has not been uploaded.
- The current HEAD debug APK passed bounded phone QA on a physical API 25
  device and matching-byte API 36 emulator QA, including legacy navigation
  contrast, IME resize, landscape cutout insets, true offline cache, recovery,
  and share paths. See
  `growth/quality/android-current-head-device-smoke-2026-08-29.md`. Debug
  signing does not satisfy the upload-signed artifact or full physical-matrix
  requirements.

## Apple app, widget, and watch

- All three targets resolve to `1.1.0 (6)`. Automatic signing, compatible
  development and App Store provisioning profiles, and valid development and
  distribution identities are visible.
- Exact current commit `80cdd608b93056edd05e29873da43834a916cd3a`
  passes a clean unsigned arm64 iOS Simulator Release build. The unsigned main
  binary SHA-256 is
  `6be0ce6bfe0ede43ca9caa70180f428626a37188b2e551e35deda3b7c6f19956`;
  the bundled unsigned widget binary SHA-256 is
  `23899278a6e02caff65a1c93209450015fd6b6c6b79fb200c271b46d615f5dd2`.
  Both report `1.1.0 (6)` and arm64; the app reports minimum iOS 15.0. These
  hashes prove source/build consistency only and are not release artifacts.
- A full Nimbo archive selects the expected profiles but fails when `codesign`
  reaches the widget with `errSecInternalComponent`. A separate watch archive
  fails at its `codesign` step with the same error.
- One exact-current-HEAD device archive attempt again reached widget CodeSign
  and failed with `errSecInternalComponent`; no provisioning or compilation
  error preceded it and no xcarchive was produced.
- Unified Security framework logs for all observed attempts report
  `errSecAuthFailed` (`-25293`) from the `seckey` path. They do not report a
  provisioning-profile or entitlement failure, user cancellation, or
  `errSecInteractionNotAllowed`. This localizes the blocker to authorization of
  the private-key operation without over-claiming whether the remaining cause
  is keychain lock state, ACL, or UI policy.
- No Apple `1.1.0 (6)` xcarchive or IPA was produced. The earlier build-5 IPA
  remains historical and cannot satisfy the current-source gate.
- One current iPad now has Developer Mode enabled, a compatible and usable DDI,
  and a connected local-network tunnel. Signing still blocks creation of an
  exact installable build. The observed iPhones and paired watch are currently
  unavailable to CoreDevice, so no Apple app was installed or launched.

## Decision

Certificate/profile metadata being visible is not proof that the private
signing operation works. Keep `release_artifact_source_sync`,
`android_physical_smoke`, and `ios_physical_smoke` blocked until:

1. the existing private signing material is usable by the non-interactive
   release process;
2. exact current-source signed artifacts are produced, hashed, and fully
   validated; and
3. those exact artifacts pass the required physical-device matrix.

This file deliberately records no passwords, private-key data, certificate
subject names, profile UUIDs, device identifiers, or account identifiers.
