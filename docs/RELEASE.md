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
enabled. Nimbo is version code 3 / version name 1.0.0. The accepted upload private
key is not available locally, so internal-track upload and the real install-over-
production test remain blocked until that key is recovered or Play completes an
upload-key reset.

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
therefore needs to be registered before creating the record. The current Apple
Developer web user receives `Access Unavailable` on Certificates, Identifiers &
Profiles despite having App Store Connect access. The Account Holder (or an Admin
with that resource permission) must register this exact explicit ID—never a new
or approximate identifier—then make it available to the Xcode signing session.

## Credentials

No signing key, certificate, provisioning profile, API key, Play service account, App Store Connect key, or password belongs in Git. CI receives short-lived or encrypted secrets. Release artifacts are attached to releases or uploaded to stores, not committed.
