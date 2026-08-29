# Current-source signing readiness — 2026-08-29

Status: **BLOCKED for Android phone and Apple; VERIFIED-CURRENT for the
unchanged Wear OS artifact**. No artifact was uploaded, submitted, or
published during these checks.

## Android phone and Wear OS

- Fresh release bundles build successfully as phone `1.1.0 (8)` and Wear OS
  `1.1.0 (1000008)`, but the Gradle release variants have no signing
  configuration and the fresh outputs are unsigned.
- An isolated exact-commit rebuild at
  `f97238beb8d99cea5ed19883b1528dca4923baee` produced the unsigned phone AAB
  `build/release/nimbo-phone-1.1.0-vc8-unsigned-f97238b.aab` with SHA-256
  `a631c67df19761964d25dd6fbbdc89b7d9c0ee6d8544ebc23113bcee52043ed9`.
  Bundletool 1.18.3 validation passed; its manifest reports package
  `uz.ganikhodjaev.weather`, versionCode `8`, versionName `1.1.0`, minSdk `24`,
  and targetSdk `36`. Archive inspection found zero signature entries. The
  companion mapping file
  `build/release/nimbo-phone-1.1.0-vc8-mapping-f97238b.txt` has SHA-256
  `b25870ff3173eb6bccd0ee6bceffba098685d11aa828d27dc9f7a1965ec2c6c7`.
  Both ignored local files are source/build evidence only, not release
  candidates, and neither is referenced by the upload manifest.
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
- Current commit `f97238beb8d99cea5ed19883b1528dca4923baee` debug APK SHA-256
  `7b2f2c12d56fdda293f19317ef6eb6da153213f84b1daeef11fd35f8e9e30edb`
  passed bounded QA on the dedicated physical API 25 phone and API 36 emulator,
  including onboarding, live city selection/search, share chooser, legacy
  navigation contrast, true-offline cache/error/recovery, IME resize, dark
  landscape, and process stability. See
  `growth/quality/android-current-head-device-smoke-2026-08-29.md`. Debug
  signing does not satisfy the upload-signed artifact or full physical-matrix
  requirements.

## Apple app, widget, and watch

- All three targets resolve to `1.1.0 (6)`. Automatic signing, compatible
  development and App Store provisioning profiles, and valid development and
  distribution identities are visible.
- Exact current commit `f97238beb8d99cea5ed19883b1528dca4923baee` passed
  arm64 Release simulator builds with `CODE_SIGNING_ALLOWED=NO`:
  - iOS app `uz.ganikhodjaev.weather`, `1.1.0 (6)`, minimum iOS 15.0:
    executable SHA-256
    `67a99d6cfc04302c54aeb71fed0a78a6e3c6c9d9aaaca7bb4d0f1e13ed62bb58`;
  - embedded widget `uz.ganikhodjaev.weather.widget`, `1.1.0 (6)`, minimum
    iOS 17.0: executable SHA-256
    `3c65e9c8716a0f0426e19f2682b0d0ab1f1c0c0975106e773694d22600f72a4e`;
  - watch app `uz.ganikhodjaev.weather.watchkitapp`, `1.1.0 (6)`, minimum
    watchOS 10.0: executable SHA-256
    `75a329ed9ad25ae8fe25dcdb54afcd0b5828a9975d2056a9ec28bc079761713a`.
  Their exact executable paths and source-sync boundary are recorded in
  `growth/quality/release-artifact-source-sync-2026-08-29.md`.
- Each bundle lacks a `_CodeSignature` directory. Each simulator Mach-O has
  only Xcode's ad-hoc linker signature: `TeamIdentifier` is unset, the
  `Info.plist` is not bound, and resources are not sealed. This is not a
  development or distribution signature. These simulator products are not
  uploadable and provide no xcarchive, exported IPA, validated dSYM set, or
  physical Apple smoke evidence.
- A full Nimbo archive selects the expected profiles but fails when `codesign`
  reaches the widget with `errSecInternalComponent`. A separate watch archive
  fails at its `codesign` step with the same error.
- One commit-80 device archive attempt again reached widget CodeSign
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
