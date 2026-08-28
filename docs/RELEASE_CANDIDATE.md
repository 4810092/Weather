# Nimbo 1.0.2 release candidate

Prepared and uploaded on August 13, 2026.

Updated on August 20, 2026 after Google rejected the Wear OS production change
for quality requirements WO-V13 (black app background) and WO-V15 (48 dp
branded launch icon on black). The source hotfix advances only the Wear OS build
to 1000007; the earlier paragraphs and artifact hashes remain the historical
August 13 checkpoint.

## Store status

- Google Play phone/tablet 1.0.2 (6) is available in production in 177
  countries/regions. Its 100% rollout completed on August 13, 2026 at 08:56.
- Wear OS 1.0.2 (1000006) was rejected for a non-black in-app background and a
  missing branded launch icon. Source build 1000007 corrects both findings and
  passes local build, lint, repository-policy, signing, Bundletool, and emulator
  checks. At 17:50 Asia/Tashkent on August 20, Play published it to the internal
  Wear track with 1000006 excluded. At 17:51, Play accepted the replacement
  Production release for review with the same exclusion and a 100% rollout.
- App Store Connect build 3 completed processing, export compliance was
  classified as using no app-implemented encryption, and the build was approved
  for the external `testers group`. Its public TestFlight link is
  <https://testflight.apple.com/join/HdE18dsh>.
- App Store Connect accepted iOS 1.0.1 build 4 for App Review on August 23,
  2026. Submission `2655e3c2-03eb-4ca4-be40-e8f74e87a12b` is `Waiting for
  Review`; automatic full release is enabled after approval. Build 3 remains
  the external TestFlight checkpoint and build 2 remains the currently live
  App Store binary until Apple approves and propagates build 4.

## Version identity

| Surface | Version |
| --- | --- |
| Android phone/tablet | 1.0.2 (6) |
| Wear OS | 1.0.2 (1000007 source hotfix; 1000006 rejected) |
| iOS/iPadOS, WidgetKit, watchOS | 1.0.1 (4), waiting for App Review |

Wear OS uses a separate version-code range because Google Play requires version
codes to be unique across every form factor sharing a package name.

## Wear OS policy hotfix evidence

- Both default and night resources resolve the app and window background to
  pure `#000000`; readable foreground colors are identical across modes.
- AndroidX Core SplashScreen 1.2.0 renders the existing launcher glyph through
  a 48 dp centered drawable on `@android:color/black`, then transitions to the
  black application theme.
- On the 480 x 480, 320 dpi Wear OS XL Round emulator, rapid cold-start captures
  recorded the centered launch glyph with black corner pixels, followed by the
  fully rendered app with black corner pixels in light and dark UI modes.
- `assembleDebug`, `lintDebug`, and `bundleRelease` pass for version 1.0.2
  (1000007). The upload-signed bundle SHA-256 is
  `aeecf509e977036f9af3f0d48c55e80413619a3fa5ea6061fa9f070f73ba2b91`;
  it matches the accepted Play upload certificate and passes Bundletool 1.18.3
  validation. Its generated universal APK is correctly v3-signed, reports
  version 1.0.2 (1000007), installs cleanly, and passes the same cold-start and
  light/dark checks.
- The unchanged watchOS target builds with Xcode 26.6/watchOS 26.5 SDK and its
  asset catalog compiles without icon or launch errors. watchOS does not require
  the Google-specific branded launch treatment.

## Local artifacts

Release artifacts and signing material remain outside the Git repository.

| Artifact | SHA-256 |
| --- | --- |
| `/Users/khasan/work/ganikhodjaev/.nimbo-release/android/1.0.2-rc1/nimbo-phone-1.0.2-vc6.aab` | `798cfe33b636cbe6a291ef0125abc193dbd1549e31c7daf50b261a0105c322ca` |
| `/Users/khasan/work/ganikhodjaev/.nimbo-release/android/1.0.2-rc1/nimbo-phone-1.0.2-vc6-mapping.txt` | `bbc6c1e13e81fe13d7303bf96cbec2f67fa6c73b571ac8c90e68bbb301b890e6` |
| `/Users/khasan/work/ganikhodjaev/.nimbo-release/android/1.0.2-rc1/nimbo-wear-1.0.2-vc1000006.aab` | `8e71db1ae0d611ec63a3eff685f69883ce6883d1791bdef1a237aa68c5dc1723` |
| `/Users/khasan/work/ganikhodjaev/.nimbo-release/android/1.0.2-wear-hotfix/nimbo-wear-1.0.2-vc1000007.aab` | `aeecf509e977036f9af3f0d48c55e80413619a3fa5ea6061fa9f070f73ba2b91` |
| `/Users/khasan/work/ganikhodjaev/.nimbo-release/ios/1.0-3/Nimbo.ipa` | `20e5a6483c91bceb5bcf0b76c4fdce5a91791c7e6c5b630f1046bf668e71f375` |
| `/Users/khasan/work/ganikhodjaev/.nimbo-release/ios/1.0.1-4/export/Nimbo.ipa` | `5f2b260023bedf2450174de2be4f299a2a2c7adbf4cfcec45ff34f13614425c4` |

All three AABs are signed with the accepted Google Play upload certificate
SHA-256 `43:15:48:A4:87:1C:9C:09:0E:EE:80:8A:C3:A3:48:98:F5:D7:86:02:D9:E7:47:DF:E8:1E:22:84:15:AA:C2:52`.
Bundletool 1.18.3 validates all three bundles. Universal APKs generated from those
exact bundles were installed on API 36 phone and Wear OS emulators; both cold
launched without a crash. The phone bundle also embeds the matching R8 mapping;
an external copy is retained beside the AAB for crash deobfuscation.

The IPA includes the iOS app, WidgetKit extension, and watchOS companion. All
three use App Store distribution profiles with `get-task-allow=false` and
`beta-reports-active=true`. The iOS app and widget share registered App Group
`group.uz.ganikhodjaev.weather`. Deep codesign verification passed.
The matching Xcode archive is retained beside the IPA at
`/Users/khasan/work/ganikhodjaev/.nimbo-release/ios/1.0-3/Nimbo.xcarchive`.

## Automated evidence

- Clean Android gate: formatting, 38 shared/host tests, SQLDelight migrations,
  R8, lint vital, phone AAB, and Wear OS AAB pass.
- iOS Release simulator build, WidgetKit build, watchOS build, device archive,
  App Store export, and deep codesign verification pass.
- Repository, 13-language localization, store metadata, and 63 production-image
  checks pass.
- Required raw store captures exist for Wear OS (480 x 480) and Apple Watch
  Series 11 (416 x 496), with no alpha channel.

## Remaining release follow-ups

- Let GitHub CI pass on the exact release commit.
- Perform a release-candidate smoke test on a physical iPhone/iPad and paired
  Apple Watch: fresh install, upgrade, WidgetKit, watch sync, C/F and Auto units,
  light/dark appearance, background refresh, offline state, and VoiceOver.
- Perform a release-candidate smoke test on a physical Android phone and paired
  Wear OS watch: fresh install, upgrade, home widget, watch sync, C/F and Auto
  units, light/dark appearance, background refresh, offline state, and TalkBack.
- Monitor the corrected Google Play review and post-launch Android vitals for
  both the phone and Wear OS production releases.
- Monitor App Review submission `2655e3c2-03eb-4ca4-be40-e8f74e87a12b` and
  verify storefront propagation after automatic release. The Apple Watch
  screenshot is already attached to version 1.0.1.

The August 20 build 1000007 hotfix is source-, signing-, Bundletool-, and
emulator-validated and is under Play Production review. That evidence does not
substitute for the two paired physical-device release gates above or prove Play
delivery before Google approves the change.
