# Release process

This is a chronological release journal. Statements inside a dated paragraph describe
that checkpoint and may be superseded later in the same document. The latest recorded
public state is Android phone/tablet 1.0.2 (6), iOS/iPadOS 1.0.1 (4), and Wear
OS 1.0.2 (1000007). The next coordinated candidate is 1.1.0: phone 7, Wear
1000008, and Apple build 5. Signed Android artifacts are locally validated; the
phone universal APK passed physical API 25 clean/live/cold-start and was
removed. Nothing in 1.1.0 has been uploaded or published. Store consoles remain
the authority for live status.

## Version identity

- Product name: Nimbo.
- Android application ID: `uz.ganikhodjaev.weather` — never change.
- iOS bundle ID: `uz.ganikhodjaev.weather`.
- Every Android upload must exceed the highest store-accepted code; at this checkpoint phone must be greater than 6 and Wear OS greater than 1000007.
- iOS marketing version starts at 1.0; build numbers are monotonically increasing.

## Nimbo 1.1.0 internal candidate — 2026-08-28

The coordinated candidate uses Android phone `1.1.0 (7)`, Wear OS `1.1.0
(1000008)`, and Apple `1.1.0 (5)`. The phone and Wear AABs are upload-signed,
Bundletool-validated, and retained outside the repository; a universal phone APK
passed bounded physical API 25 release smoke. See the [growth checkpoint](GROWTH_RELEASE.md)
and [signed Android artifact evidence](../growth/quality/android-release-artifacts-2026-08-28.md).
This section records local readiness only: no 1.1.0 store upload, review,
approval, rollout, or public availability is claimed.

## App Store 1.0.1 submission — 2026-08-23

App Store Connect accepted Nimbo 1.0.1 build 4 and reports submission
`2655e3c2-03eb-4ca4-be40-e8f74e87a12b` as `Waiting for Review`. The submitted
binary contains the iOS/iPadOS app, WidgetKit extension, and Apple Watch
companion. The product page includes iPhone, iPad, and Apple Watch screenshots;
release notes are populated for all 12 App Store localizations used by Nimbo.
Automatic release is enabled, with an immediate full rollout after Apple
approval and no phased release. This is not yet a live App Store release; App
Store Connect remains authoritative until review and storefront propagation
complete.

The exported IPA is retained at
`/Users/khasan/work/ganikhodjaev/.nimbo-release/ios/1.0.1-4/export/Nimbo.ipa`
with SHA-256
`5f2b260023bedf2450174de2be4f299a2a2c7adbf4cfcec45ff34f13614425c4`.
Release simulator build, shared tests, repository/localization/store checks,
archive/export, distribution signing, and deep code-sign verification passed
before upload.

## Wear OS policy rejection and hotfix — 2026-08-20

Google rejected Wear OS version code 1000006 because the in-app background was
not pure black and startup did not show the launcher icon at 48 dp on black. The
1000007 source hotfix makes the default and night app/window backgrounds
`#000000`, adds AndroidX Core SplashScreen 1.2.0, and uses the existing launcher
glyph through a centered 48 dp splash drawable. Repository checks guard the
policy resources, starting theme, launcher-theme assignment, call ordering, and
version-code floor.

The hotfix passes `assembleDebug`, `lintDebug`, and `bundleRelease`. Its
upload-signed AAB has SHA-256
`aeecf509e977036f9af3f0d48c55e80413619a3fa5ea6061fa9f070f73ba2b91`,
matches the accepted upload certificate, and passes Bundletool 1.18.3
validation. A Bundletool-generated universal APK is v3-signed with the same
certificate and reports package `uz.ganikhodjaev.weather`, version 1.0.2
(1000007), min SDK 30, and target SDK 36. Rapid
cold-start captures on the 480 x 480 / 320 dpi Wear OS XL Round emulator show
the centered branded glyph on black followed by a readable black app surface in
both UI modes. The unchanged NimboWatch target also builds successfully with
Xcode 26.6/watchOS 26.5 SDK; no Apple launch-screen change is required.
Play Console accepted build 1000007 into Production release
`Nimbo Wear 1.0.2 (1000007) — Policy fix`; build 1000006 appears under `Not
Included` and rollout is 100%. At 17:50 Asia/Tashkent on August 20, the same
replacement became the latest internal Wear release, with 1000006 excluded. At
17:51, Play Console accepted the Production change for review and now lists it
under `Changes under review`. The internal track has no selected testers, and
managed publishing remains off, so an approved Production release will publish
automatically.

## Android prerequisites

Verify Play App Signing and the upload certificate in Play Console. A local or CI release build must use protected credentials and must match the accepted upload identity. Build an AAB with R8, validate package/version/permissions, install a Play-derived production APK, then install the Nimbo update before any rollout.

Play Console inspection on August 10, 2026 confirmed the existing production
listing at version code 2 / version name 1.0.1 and confirmed Play App Signing is
enabled. The Nimbo candidate at that checkpoint was version code 4 / version name 1.0.0.
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
was corrected to the current repository `docs/PRIVACY.md`.

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

The obsolete Production draft containing version code 3 was replaced with the
already validated version code 4 artifact. Google Play accepted Production
release `Nimbo 1.0.0 (4)` for review at 14:21 Asia/Tashkent on August 10, 2026.
The common-issues pre-submit check completed without another issue. The
Publishing overview reports `Изменения на проверке` and
`Изменения находятся на рассмотрении`. The release requests a 100% rollout
across all target countries because Production reports zero active installs; a
staged percentage cannot produce a meaningful risk sample. Managed publishing
is off, so an approved change will roll out automatically. The only validation
warning is the non-blocking native-debug-symbol recommendation.

Google Play made `Nimbo 1.0.0 (4)` available in Production at 14:32
Asia/Tashkent on August 10, 2026, across 177 countries. The localized city
search, resolved current-location city name, and rounded timeline interaction
update was then built as `Nimbo 1.0.1 (5)`. Its upload-signed AAB has SHA-256
`42f3d107c6a7e71c6895f13e34822604ac35632f774a86d9a75196769ac1f581`
and the accepted upload certificate documented above. Play accepted the new
Production release with English and Russian release notes and a requested 100%
rollout across all target countries. At 23:14 Asia/Tashkent, the Publishing
overview reported the change under review; the automated common-issues check
will pass it to Google review when complete. Managed publishing remains off,
and the only validation warning remains the non-blocking native-debug-symbol
recommendation.

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

The current Admin has Certificates, Identifiers & Profiles access, and explicit App ID
`uz.ganikhodjaev.weather` was registered as `Nimbo` in team `5SWEZ7HTYP` on
August 10, 2026 without optional capabilities. Xcode 26.6 is authenticated for
the same team, and the valid Apple Distribution private key is present locally. App Store profile
`Nimbo App Store 1.0` was generated and installed, and Xcode 26.6 exported a
distribution-signed iOS 1.0 (1) IPA with SHA-256
`cb5c75bdcb574770e887aede7b05a36f33b2d4c4eb944f2dcf42032e23a46335`.
Deep codesign validation passed; the embedded profile has
`beta-reports-active=true` and `get-task-allow=false`. Apple rejected `Nimbo` as
a globally occupied App Store name, so the minimal store-only fallback
`Nimbo Weather` is used for App Store Connect record `6799886897`; the binary
display name remains `Nimbo`. Xcode uploaded the verified IPA at 13:29
Asia/Tashkent, Apple processed build 1, and the build is attached to version
1.0 with export compliance recorded as no custom encryption. English metadata,
review notes/contact, manual release, and real production-UI iPhone/iPad
screenshots are saved. App Information is saved with Weather category, subtitle,
and a 4+ rating. App Privacy is published with only Coarse Location and Search
History disclosed for App Functionality, not linked to identity and not used for
tracking; the public privacy-policy URL targets `docs/PRIVACY.md` on `master`.
Build 1 reports `Ready to Submit`. At the owner's explicit direction to proceed
directly to release, no internal TestFlight tester was assigned and no physical
TestFlight smoke is claimed. Pricing is free with United States as the base
storefront, all 175 countries or regions are selected, and untested Apple
Silicon Mac and Apple Vision Pro distribution are disabled. Content-rights
information records the necessary rights for the third-party weather and place
data. App Store version 1.0 build 1 was submitted at 14:18 Asia/Tashkent on
August 10, 2026. Submission
`1e305187-129c-466b-bc74-3347254eaea1` is `Waiting for Review`; manual release is
selected for the first version.

The same localized-location and timeline update was archived as iOS 1.0 build
2. During verification, the hard-coded bundle version values in `Info.plist`
were replaced with `MARKETING_VERSION` and `CURRENT_PROJECT_VERSION`, making
the Xcode project settings the source of truth. The final distribution-signed
IPA has SHA-256
`3988430bd6fd85e84f830dbd24ff020059e5ebcb4de6fc160a0042fed58eaf2d`;
deep codesign validation passed, and the embedded profile again has
`beta-reports-active=true` and `get-task-allow=false`. Xcode uploaded build 2 at
23:01 Asia/Tashkent. The obsolete build 1 review submission was canceled,
build 1 was removed from version 1.0, and build 2 was attached with export
compliance recorded as no encryption. Submission
`d44f3a55-ae31-4a17-9195-371ba9efa478` was sent at 23:14 Asia/Tashkent and is
`Waiting for Review`. Manual release remains selected.

## Credentials

No signing key, certificate, provisioning profile, API key, Play service account, App Store Connect key, or password belongs in Git. CI receives short-lived or encrypted secrets. Release artifacts are attached to releases or uploaded to stores, not committed.
