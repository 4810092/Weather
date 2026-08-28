# Current-source signing readiness — 2026-08-29

Status: **BLOCKED for Android phone and Apple; VERIFIED-CURRENT for the
unchanged Wear OS artifact**. No artifact was uploaded, submitted, or
published during these checks.

## Android phone and Wear OS

- Fresh release bundles build successfully as phone `1.1.0 (8)` and Wear OS
  `1.1.0 (1000008)`, but the Gradle release variants have no signing
  configuration and the fresh outputs are unsigned.
- The expected upload keystore exists outside the repository with owner-only
  permissions. Both password items are present in the login Keychain, but
  exact account-and-service lookups that request their values make the
  `security` command exit with status `51`. No password value was printed,
  persisted, or made available to the build.
- A signed phone vc8 artifact therefore does not exist. The previous phone vc7
  signature and physical smoke remain historical evidence only.
- The unchanged, retained Wear OS vc1000008 AAB remains the current signed
  artifact with SHA-256
  `ac19a0eab1a60554db309166f135e754c97205b79c4f5182164a8b21594e7dc6`.
  Its AAB signature and retained universal APK signature still verify, but it
  has no physical-watch result and has not been uploaded.

## Apple app, widget, and watch

- All three targets resolve to `1.1.0 (6)`. Automatic signing, compatible
  development and App Store provisioning profiles, and valid development and
  distribution identities are visible.
- A full Nimbo archive selects the expected profiles but fails when `codesign`
  reaches the widget with `errSecInternalComponent`. A separate watch archive
  fails at its `codesign` step with the same error.
- Unified Security framework logs for all observed attempts report
  `errSecAuthFailed` (`-25293`) from the `seckey` path. They do not report a
  provisioning-profile or entitlement failure, user cancellation, or
  `errSecInteractionNotAllowed`. This localizes the blocker to authorization of
  the private-key operation without over-claiming whether the remaining cause
  is keychain lock state, ACL, or UI policy.
- No Apple `1.1.0 (6)` xcarchive or IPA was produced. The earlier build-5 IPA
  remains historical and cannot satisfy the current-source gate.
- One current iPad appears as an available Xcode destination with Developer
  Mode enabled, but a compatible, usable DDI was not proven. The other observed
  iPad is unavailable and reports lock/developer-mode-related readiness errors.
  No app was installed or launched.

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
