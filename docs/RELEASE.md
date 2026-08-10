# Release process

## Version identity

- Product name: Nimbo.
- Android application ID: `uz.ganikhodjaev.weather` — never change.
- iOS bundle ID: `uz.ganikhodjaev.weather`.
- Android Nimbo 1.0 must use a version code greater than the highest code already accepted by Google Play (legacy repository code is 2).
- iOS marketing version starts at 1.0; build numbers are monotonically increasing.

## Android prerequisites

Verify Play App Signing and the upload certificate in Play Console. A local or CI release build must use protected credentials and must match the accepted upload identity. Build an AAB with R8, validate package/version/permissions, install a Play-derived production APK, then install the Nimbo update before any rollout.

Play Console inspection on August 10, 2026 confirmed the existing production
listing at version code 2 / version name 1.0.1 and confirmed Play App Signing is
enabled. Nimbo is version code 3 / version name 1.0.0. The original extensionless
upload keystore was recovered outside the repository with alias `weather`; the
matching store/key passwords remain in macOS Keychain. Its file and Keychain
dates align with the March 2024 legacy release. Keychain access and certificate
verification completed on August 10: the certificate exactly matches the
accepted upload SHA-256 below. Keep all private material outside Git. The current
Play role cannot request an upload-key reset (`Permission required`), but no
reset is needed.

The accepted upload certificate SHA-256 reported by Play is
`43:15:48:A4:87:1C:9C:09:0E:EE:80:8A:C3:A3:48:98:F5:D7:86:02:D9:E7:47:DF:E8:1E:22:84:15:AA:C2:52`.

The production legacy input is no longer inferred from package metadata. App
Bundle Explorer artifact `4859919545693253619` was downloaded as Google's signed
universal APK and verified as version code 2 / version name 1.0.1. On the API 36
emulator it passed clean install, real network rendering, background/foreground,
repeat launch, and offline cold launch. Its Play signing certificate SHA-256 is
`99:B8:76:1F:7E:FB:2F:02:90:E4:A1:98:E9:46:54:36:C7:3B:CA:D0:DD:61:91:14:12:6F:F5:67:FF:80:BF:63`.
Installing a locally QA-signed Nimbo APK over it fails with
`INSTALL_FAILED_UPDATE_INCOMPATIBLE`, as it must. The remaining upgrade gate is
therefore specifically a Play-signed version code 3 internal-track build, not
legacy artifact availability.

Play accepted the unchanged signed AAB as version code 3 / version name 1.0.0,
target API 36. Internal release `Nimbo 1.0.0 (3) — Internal` became active for
the existing three-account license-testers list at 10:42 Asia/Tashkent on August
10. Its signed file SHA-256 is
`90f4b3c0a002341855701fbf2c8714f48dcff0ba5c820acd89edd0123a0674c6`.
The real upgrade gate passed on August 10 on the Android 16 / API 36
`Small_Phone` Play Store emulator (720 x 1280). Production 1.0.1 (2) was
installed from Google Play and launched at 11:08 Asia/Tashkent. The same
installation opted into Internal Testing and accepted the Play-delivered Nimbo
1.0.0 (3) update at 11:12 without uninstalling. Package-manager evidence shows
the original `firstInstallTime`, a later `lastUpdateTime`, installer and
initiating package `com.android.vending`, and the unchanged expected Play
app-signing certificate.

The preserved post-update installation passed background/foreground,
force-stop and online cold launch, offline cold launch with database-backed
saved weather, manual city change and persistence, metric unit persistence,
light/dark appearance, English, Russian, Arabic RTL, timeline selection and
hour semantics, yesterday comparison, recent-day history, and Best Time
Outside. Logcat and process exit history showed no crash or ANR. This closes the
legacy Play 1.0.1 (2) -> Nimbo 1.0.0 (3) release gate; listing/policy completion
and production promotion remain.

As of 2026-08-31, Google Play updates must target Android 16 / API 36. Nimbo targets API 36 from its first release candidate.

## iOS prerequisites

Verify or create App ID `uz.ganikhodjaev.weather` in the named Apple Developer team, then configure distribution signing and App Store Connect. Since 2026-04-28, uploads must be built with Xcode 26 or later and an iOS 26 SDK. Archive, validate, upload, complete privacy/age-rating metadata, smoke-test through TestFlight, then submit.

The device archive command is:

```sh
xcodebuild -project iosApp/Nimbo.xcodeproj -scheme Nimbo \
  -configuration Release -destination 'generic/platform=iOS' \
  -archivePath build/Nimbo.xcarchive -allowProvisioningUpdates archive
xcodebuild -exportArchive -archivePath build/Nimbo.xcarchive \
  -exportPath build/app-store-export \
  -exportOptionsPlist iosApp/ExportOptions.plist \
  -allowProvisioningUpdates
```

At the August 10, 2026 checkpoint the first command produced a valid arm64 archive
with the requested team and bundle ID. Export stopped with `No Accounts` and no
App Store provisioning profile, so that archive must not be uploaded or described
as distribution-signed. Sign in to the named team in Xcode, repeat export, inspect
the exported entitlements, and only then upload.

The authenticated App Store Connect team currently has no Nimbo app. The New App
form's Bundle ID list does not contain `uz.ganikhodjaev.weather`; the exact App ID
therefore needs to be registered before creating the record. The current web user
is an App Store Connect Admin, but the Apple Developer identifier portal returns
`This request is forbidden for security reasons` because the separate
Certificates, Identifiers & Profiles resource is not assigned. Xcode 26.6 also
has no signed-in Apple Account. A valid Apple Distribution private key for team
`5SWEZ7HTYP` and current profiles for other apps exist locally, but no profile
targets Nimbo. The Account Holder must grant that resource to the current Admin
or sign the Account Holder into Xcode; then register this exact explicit ID—never
a new or approximate identifier—and create its App Store distribution profile.

## Credentials

No signing key, certificate, provisioning profile, API key, Play service account, App Store Connect key, or password belongs in Git. CI receives short-lived or encrypted secrets. Release artifacts are attached to releases or uploaded to stores, not committed.
