# Nimbo project state

Last updated: 2026-08-10

## Current phase

Production release execution for Nimbo 1.0.0 RC2. Product and architecture work
are frozen; only signing, publishing, compliance, release QA, security, and
release-journal changes are in scope.

## Source and versions

- Android: `uz.ganikhodjaev.weather`, version name `1.0.0`, version code `4`,
  target API 36.
- iOS: `uz.ganikhodjaev.weather`, marketing version `1.0`, build `1`, team
  `5SWEZ7HTYP`.
- RC tags: `v1.0.0-rc.1` at
  `223864157d5fde8ccf4c686912473a9878285457`; `v1.0.0-rc.2` at
  `692c0acbb1a807ae1b9024f104f0dbf657cad4f7`.
- RC2 is a release-only compatibility fix after Play review found that the
  coarse-location permission implicitly required location hardware. The app now
  explicitly marks `android.hardware.location` optional, and CI prevents this
  declaration from regressing.
- Pull requests 1 through 5 are merged. Current master is
  `692c0acbb1a807ae1b9024f104f0dbf657cad4f7`; PR CI run `31365961384` is green
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
- The required real Play delivery gate passed on the Android 16 / API 36
  `Small_Phone` Play Store emulator (720 x 1280). Production version 1.0.1 (2)
  was installed from Google Play at 11:08 Asia/Tashkent, launched, rendered live
  Tashkent weather, and created persisted state. Without uninstalling, that
  installation opted into Internal Testing and updated through Google Play to
  Nimbo 1.0.0 (3) at 11:12. `firstInstallTime` remained 11:08 while
  `lastUpdateTime` became 11:12; both installer and initiating package are
  `com.android.vending`, and the Play app-signing certificate remained the
  expected SHA-256 above.
- Post-update smoke passed on that preserved installation: online cold launch,
  background/foreground, force-stop/relaunch, offline cold launch from the local
  database with the saved-weather indicator, Tashkent -> Samarkand -> Tashkent
  manual city changes, metric selection persistence, light/dark appearance,
  English, Russian, and Arabic RTL, selected-hour timeline interaction,
  yesterday comparison, recent-day history, and Best Time Outside. Timeline
  hour nodes expose localized semantic descriptions including time,
  temperature, condition, apparent temperature, precipitation, and wind. No app
  crash or ANR was observed in logcat or process exit history.
- The English default Play listing is saved as an unpublished Nimbo draft. Its
  legacy icon, feature graphic, and two legacy phone screenshots were detached
  and replaced with the version-controlled Nimbo icon, feature graphic, five
  phone screenshots, four 7-inch tablet screenshots, and four 10-inch tablet
  screenshots. The resulting asset counts are 1/1, 1/1, 5/8, 4/8, and 4/8.
- All Play app-content declarations are complete. The Health declaration records
  no health features or regional health requirements. Data Safety now matches
  the source: encrypted transport, no account, no third-party sharing, optional
  approximate location and in-app search history collected for app
  functionality, and automatic deletion within 90 days. The listing privacy URL
  now points to the repository's current `docs/PRIVACY.md` rather than the stale
  legacy URL. These changes are saved as drafts and are not yet submitted for
  Play review.
- The first Production review draft using version code 3 exposed one phone and
  five tablets as newly unsupported because Play inferred required
  `android.hardware.location`. Those devices have zero active installs, but the
  exclusion contradicted Nimbo's manual-city flow, so version code 3 will not be
  promoted. Version code 4 contains only the explicit optional-hardware manifest
  fix. Its upload-signed AAB was accepted into an Internal RC2 draft; SHA-256 is
  `919fa79df1f52cc7ed4750f3f979f812c84e796741aa7ec5adf0251e42b05dd3`.
  Play validation now restores all six devices (11,361 phones and 6,279 tablets
  supported) and reports no device-loss warning. The sole remaining warning is
  the non-blocking recommendation to upload native debug symbols.

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

1. Activate Internal RC2, install the Play-delivered version code 4 update on the
   preserved version code 3 test installation, run the manifest-scoped smoke,
   then promote version code 4 to Production with the completed listing and
   policy changes.
2. The Apple Account Holder must grant the current Admin access to Certificates,
   Identifiers & Profiles (or sign the Account Holder into Xcode). Then create
   the exact App ID, App Store profile/record, upload build 1, complete
   TestFlight, and submit for review.

## Worktree rule

Pre-existing `.idea` changes belong to the user. Do not reset, stash, stage, or
commit them.
