# Nimbo project state

Last updated: 2026-08-10

## Current phase

Production release execution for Nimbo 1.0.0 RC1. Product and architecture work
are frozen; only signing, publishing, compliance, release QA, security, and
release-journal changes are in scope.

## Source and versions

- Android: `uz.ganikhodjaev.weather`, version name `1.0.0`, version code `3`,
  target API 36.
- iOS: `uz.ganikhodjaev.weather`, marketing version `1.0`, build `1`, team
  `5SWEZ7HTYP`.
- RC tag: `v1.0.0-rc.1`, source commit
  `223864157d5fde8ccf4c686912473a9878285457`.
- Pull requests 1 and 2 are merged. Current master is
  `a769449ba4e7053b26c5286f849124a9a6c04076`; CI run `31358514085` is green
  for Android/shared checks and the unsigned iOS build.
- The August 10 gate executes 36 shared/host tests with zero failures.

## Android release state

- The existing Google Play app is `Tashkent Weather`, package
  `uz.ganikhodjaev.weather`. Production is version code 2 / version name 1.0.1.
- Play App Signing is enabled. The Google app-signing certificate SHA-256 is
  `99:B8:76:1F:7E:FB:2F:02:90:E4:A1:98:E9:46:54:36:C7:3B:CA:D0:DD:61:91:14:12:6F:F5:67:FF:80:BF:63`.
- The accepted upload certificate SHA-256 is
  `43:15:48:A4:87:1C:9C:09:0E:EE:80:8A:C3:A3:48:98:F5:D7:86:02:D9:E7:47:DF:E8:1E:22:84:15:AA:C2:52`.
- The original extensionless upload keystore was recovered outside the
  repository. Its modification date is March 27, 2024, its alias is `weather`,
  and Android Studio created matching store/key password entries in macOS
  Keychain on March 29, 2024. The exact local path is intentionally retained in
  the Keychain item label rather than committed to the public repository.
- macOS Keychain access was authorized and the recovered keystore certificate
  was verified. Its SHA-256 exactly matches the accepted Play upload
  certificate; upload-key reset is not required.
- The current Play Console role can upload releases but cannot request an upload
  key reset: the official reset control is disabled with `Permission required`.
  Reset is unnecessary if the recovered keystore is unlocked and its certificate
  matches the accepted upload certificate.
- An unchanged R8 release AAB for 1.0.0 (3) was signed outside the repository
  with the recovered upload key. Its file SHA-256 is
  `90f4b3c0a002341855701fbf2c8714f48dcff0ba5c820acd89edd0123a0674c6`.
  Play accepted it as version code 3, target API 36, and activated Internal
  release `Nimbo 1.0.0 (3) — Internal` at 10:42 Asia/Tashkent. The existing
  license-testers list (three accounts) has access.
- The real Play-signed legacy universal APK, artifact
  `4859919545693253619`, passed clean launch, network, background/foreground,
  repeat launch, and offline cold launch on API 36. The required vc2 -> vc3
  Play-delivered upgrade remains pending. The Android 16 Play Store emulator is
  running and the official Google sign-in flow is waiting for the Account
  Holder to scan its passkey QR; no Google account was previously present on the
  emulator.
- The English default Play listing text is saved as an unpublished Nimbo draft.
  Old visual assets still need to be replaced with the version-controlled
  production assets before the listing is submitted.

## Apple release state

- App Store Connect is accessible as `kh.ganikhodjaev@gmail.com`, role Admin,
  all apps. The Account Holder is `4810092@gmail.com`.
- A valid Apple Distribution identity for team `5SWEZ7HTYP`, including its
  private key, exists in login Keychain.
- Sixteen current provisioning profiles for this team exist locally, including
  App Store profiles for other apps; none targets
  `uz.ganikhodjaev.weather`.
- Xcode 26.6 currently has no signed-in Apple Account.
- App Store Connect has no Nimbo record. Its New App Bundle ID list does not
  contain `uz.ganikhodjaev.weather`.
- The Apple Developer identifier portal returns `This request is forbidden for
  security reasons` for the current Admin. App Store Connect's role dialog lists
  the generic Admin developer privileges, but the separate Certificates,
  Identifiers & Profiles resource is not assigned to this user.
- Local App Store Connect `.p8` candidates belong to another app workflow; no
  usable issuer/key pairing for this team was found. The Integrations page is
  not accessible to the current web user.
- A device archive builds with Xcode 26.6 / iOS 26.5 SDK but is development
  signed. There is no App Store export, upload, TestFlight build, or App Review
  submission.
- Four physical iOS devices are known to Xcode but are currently offline.

## Legacy OpenWeather credential

- Nimbo uses keyless Open-Meteo and does not depend on the exposed legacy key.
- Gitleaks reports zero leaks in all reachable public history after sanitation.
- OpenWeather has no authenticated browser session, no matching environment
  configuration, and no matching Keychain credential on this workstation. Key
  status or revocation cannot be verified without the provider account.

## Next executable gates

1. Complete the passkey sign-in currently displayed on the Android 16 Play
   Store emulator. Install legacy production vc2 from Play, accept the Internal
   update to vc3 without
   uninstalling, and run the documented upgrade/smoke matrix.
2. Replace the legacy Play listing visual assets, complete policy declarations,
   and start the production rollout after the
   Play-delivered upgrade passes.
3. The Apple Account Holder must grant the current Admin access to Certificates,
   Identifiers & Profiles (or sign the Account Holder into Xcode). Then create
   the exact App ID, App Store profile/record, upload build 1, complete
   TestFlight, and submit for review.

## Worktree rule

Pre-existing `.idea` changes belong to the user. Do not reset, stash, stage, or
commit them.
