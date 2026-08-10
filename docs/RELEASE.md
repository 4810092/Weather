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
enabled. The current Nimbo candidate is version code 4 / version name 1.0.0.
The original extensionless upload keystore was recovered outside the repository
with alias `weather`; the
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

The production listing draft was completed on August 10. The legacy icon,
feature graphic, and two legacy phone screenshots were detached, while the
version-controlled Nimbo icon, feature graphic, five phone screenshots, four
7-inch tablet screenshots, and four 10-inch tablet screenshots were assigned.
The final asset counts are 1/1 icon, 1/1 feature graphic, 5/8 phone, 4/8
7-inch, and 4/8 10-inch. The saved draft uses the Nimbo name and source-backed
copy.

The Play app-content overview reports every declaration complete. Health is
declared as having no health functions or regional health requirements. Data
Safety records encrypted transport, no account, no third-party sharing,
optional approximate location and in-app search history collected for app
functionality, and automatic deletion within 90 days. The privacy-policy URL
was corrected to the current repository `docs/PRIVACY.md`. These are saved
drafts pending production release submission; they are not yet public.

The first Production review draft used the Play-tested version code 3 binary.
Play correctly warned that the coarse-location permission implicitly made
`android.hardware.location` required, excluding one phone and five tablets.
That contradicted the product contract because manual city search works without
location permission or hardware. RC2 therefore adds only an explicit
`android:required="false"` location-hardware declaration and increments Android
version code to 4 while retaining version name 1.0.0. A repository check now
guards the optional-hardware declaration.

The upload-signed RC2 AAB was accepted by Play with SHA-256
`919fa79df1f52cc7ed4750f3f979f812c84e796741aa7ec5adf0251e42b05dd3`.
Internal review reports all six devices restored, totals of 11,361 phones and
6,279 tablets, and no device-loss warning. The only remaining warning is the
non-blocking recommendation to upload native debug symbols. Internal release
`Nimbo 1.0.0 (4) — Internal RC2` became active for the existing three testers at
12:35 Asia/Tashkent on August 10, 2026. The preserved version code 3 install then
updated through Google Play to version code 4 at 13:20 without uninstall;
`firstInstallTime` and the Play installer were preserved. Online and
airplane-mode cached cold launches passed with the expected saved-weather state
and no crash. Version code 3 must not be promoted to Production.

RC2 is tagged `v1.0.0-rc.2` at master commit
`692c0acbb1a807ae1b9024f104f0dbf657cad4f7`. Pull request 5 passed both
Android/shared and unsigned iOS CI before merge.

As of 2026-08-31, Google Play updates must target Android 16 / API 36. Nimbo targets API 36 from its first release candidate.

## iOS prerequisites

Verify or create App ID `uz.ganikhodjaev.weather` in the named Apple Developer team, then configure distribution signing and App Store Connect. Since 2026-04-28, uploads must be built with Xcode 26 or later and an iOS 26 SDK. Archive, validate, upload, complete privacy/age-rating metadata, smoke-test through TestFlight, then submit.

The device archive command is:

```sh
xcodebuild -project iosApp/Nimbo.xcodeproj -scheme Nimbo \
  -configuration Release -destination 'generic/platform=iOS' \
  -archivePath build/Nimbo.xcarchive \
  CODE_SIGN_STYLE=Manual CODE_SIGN_IDENTITY='Apple Distribution' \
  DEVELOPMENT_TEAM=5SWEZ7HTYP \
  PROVISIONING_PROFILE_SPECIFIER='Nimbo App Store 1.0' archive
xcodebuild -exportArchive -archivePath build/Nimbo.xcarchive \
  -exportPath build/app-store-export \
  -exportOptionsPlist iosApp/ExportOptions.plist
```

On August 10, 2026 these commands produced and exported a valid arm64 App Store
archive without requiring an Xcode account login. The archive and exported IPA
use the explicit Nimbo profile and the existing Apple Distribution private key;
the post-export verification below is mandatory before upload.

The authenticated App Store Connect team currently has no Nimbo app. The current
Admin now has Certificates, Identifiers & Profiles access, and explicit App ID
`uz.ganikhodjaev.weather` was registered as `Nimbo` in team `5SWEZ7HTYP` on
August 10, 2026 without optional capabilities. The New App form now exposes the
exact Bundle ID. Xcode 26.6 still has no signed-in Apple Account, but the valid
Apple Distribution private key is present locally. App Store profile
`Nimbo App Store 1.0` was generated and installed, and Xcode 26.6 exported a
distribution-signed iOS 1.0 (1) IPA with SHA-256
`cb5c75bdcb574770e887aede7b05a36f33b2d4c4eb944f2dcf42032e23a46335`.
Deep codesign validation passed; the embedded profile has
`beta-reports-active=true` and `get-task-allow=false`. Apple rejected `Nimbo` as
a globally occupied App Store name, so the minimal store-only fallback
`Nimbo Weather` is prepared; the binary display name remains `Nimbo`.
`iPhone (Khasan)` on iOS 26.6 is connected for the TestFlight smoke.

## Credentials

No signing key, certificate, provisioning profile, API key, Play service account, App Store Connect key, or password belongs in Git. CI receives short-lived or encrypted secrets. Release artifacts are attached to releases or uploaded to stores, not committed.
