# Nimbo 1.0.2 release candidate

Prepared and uploaded on August 13, 2026.

## Store status

- Google Play phone/tablet 1.0.2 (6) is in production review for a 100% rollout.
  Managed publishing is off, so an approval will publish it automatically.
- Wear OS 1.0.2 (1000006) is active in the Wear OS internal-testing track. The
  required 480 x 480 Wear OS screenshot is saved in Play Console. Production
  enrollment still requires the account holder to accept the Wear OS review
  rules, after which the form-factor changes can be submitted.
- App Store Connect build 3 completed processing, export compliance was
  classified as using no app-implemented encryption, and the build was approved
  for the external `testers group`. Its public TestFlight link is
  <https://testflight.apple.com/join/HdE18dsh>.
- The existing App Store production submission on build 2 was not changed;
  build 3 is TestFlight-only until it is deliberately selected for a later App
  Store release.

## Version identity

| Surface | Version |
| --- | --- |
| Android phone/tablet | 1.0.2 (6) |
| Wear OS | 1.0.2 (1000006) |
| iOS/iPadOS, WidgetKit, watchOS | 1.0 (3) |

Wear OS uses a separate version-code range because Google Play requires version
codes to be unique across every form factor sharing a package name.

## Local artifacts

Release artifacts and signing material remain outside the Git repository.

| Artifact | SHA-256 |
| --- | --- |
| `/Users/khasan/work/ganikhodjaev/.nimbo-release/android/1.0.2-rc1/nimbo-phone-1.0.2-vc6.aab` | `798cfe33b636cbe6a291ef0125abc193dbd1549e31c7daf50b261a0105c322ca` |
| `/Users/khasan/work/ganikhodjaev/.nimbo-release/android/1.0.2-rc1/nimbo-phone-1.0.2-vc6-mapping.txt` | `bbc6c1e13e81fe13d7303bf96cbec2f67fa6c73b571ac8c90e68bbb301b890e6` |
| `/Users/khasan/work/ganikhodjaev/.nimbo-release/android/1.0.2-rc1/nimbo-wear-1.0.2-vc1000006.aab` | `8e71db1ae0d611ec63a3eff685f69883ce6883d1791bdef1a237aa68c5dc1723` |
| `/Users/khasan/work/ganikhodjaev/.nimbo-release/ios/1.0-3/Nimbo.ipa` | `20e5a6483c91bceb5bcf0b76c4fdce5a91791c7e6c5b630f1046bf668e71f375` |

Both AABs are signed with the accepted Google Play upload certificate
SHA-256 `43:15:48:A4:87:1C:9C:09:0E:EE:80:8A:C3:A3:48:98:F5:D7:86:02:D9:E7:47:DF:E8:1E:22:84:15:AA:C2:52`.
Bundletool 1.18.3 validates both bundles. Universal APKs generated from those
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
- After the phone production review completes, submit the pending Wear OS store
  screenshot without restarting the phone review.
- Add the Apple Watch screenshot to the App Store product page before selecting
  a future production build.

Simulator and local signing evidence make this candidate upload-ready, but do
not substitute for the two paired physical-device release gates above.
