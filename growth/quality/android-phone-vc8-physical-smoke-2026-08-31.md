# Android phone vc8 physical smoke — 2026-08-31

Status: **PASS for the exact AAB-derived, upload-key-signed physical phone
scope**. The broader Android physical gate remains **BLOCKED**.

## Byte authority

- Product source revision:
  `2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652`.
- Exact retained phone AAB: `nimbo-phone-1.1.0-vc8.aab`, SHA-256
  `d4a90676f32745ea314b50ced2c9955e86923589534a1a7654ac6f1207e88a62`.
- Pinned Bundletool `1.18.3`, SHA-256
  `a099cfa1543f55593bc2ed16a70a7c67fe54b1747bb7301f37fdfd6d91028e29`.
- Derived signed APK set SHA-256:
  `28ab80e1693a23586edfac76278409e7749ede4db476e67841ee61f6fa181752`.
- Derived universal APK SHA-256:
  `e970352d54e4c95100f03539c54dbecb0732c635e2f6057715215f271d24e976`.
- Pulled installed `base.apk` SHA-256:
  `e970352d54e4c95100f03539c54dbecb0732c635e2f6057715215f271d24e976`.
- APK Signature Scheme v2 and v3 verified. The single signer certificate
  SHA-256 is
  `431548a4871c9c090eee808ac3a34898f5d78602d9e747dfe81e228415aac252`,
  matching the manifest upload certificate.
- Manifest identity: package `uz.ganikhodjaev.weather`, version `1.1.0 (8)`,
  `minSdk=24`, `targetSdk=36`.

Bundletool generated the universal APK directly from the exact retained AAB.
Signing values were read from the local Keychain without printing or writing
them to the evidence bundle. The AAB itself was not rebuilt or modified.

## Physical target and precondition

- Dedicated General Mobile 4G Dual (`gm4g_sprout`, serial `e76fd426`).
- Physical Android `7.1.1`, API 25, ARM, 720 x 1280, Russian locale.
- Nimbo was absent before installation. The device had no SIM; Wi-Fi was the
  only connected network.

## Smoke result

1. Clean `adb install` succeeded. Pulling the installed `base.apk` reproduced
   the exact derived universal APK hash. `dumpsys package` confirmed version
   `1.1.0 (8)` and first install at `2026-08-31 20:20:21 +05:00`.
2. Forced cold launch displayed `MainActivity` in 1,797 ms. The process stayed
   alive and rendered the localized onboarding without requesting location.
3. Selecting the quick city `Ташкент` produced a live forecast with current
   conditions, yesterday comparison, and `Лучшее время для прогулки`.
4. The share action opened the native Android chooser. No destination was
   selected and no message was sent.
5. Wi-Fi was disabled through Settings UI; the device had no SIM and DNS lookup
   for `api.open-meteo.com` failed. A force-stop/cold start still rendered the
   saved Tashkent forecast. Explicit refresh retained the cached forecast and
   showed `Не удалось обновить. Показана сохранённая погода.`
6. Wi-Fi was restored and connectivity was proven by a successful provider
   probe. Refresh recovered and the fallback warning disappeared.
7. The Nimbo PID-scoped log had no fatal exception, ANR, native fatal signal,
   TLS, certificate-path, or trust-anchor failure. The only application-scoped
   exception signal was the expected `UnknownHostException` from the deliberate
   offline refresh.
8. Nimbo was uninstalled after capture. Package absence, airplane mode off,
   mobile-data setting restored, and connected Wi-Fi were rechecked.

During installation, the old device Play Store process `com.android.vending`
had an independent native abort: `JNI ERROR (app bug): local reference table
overflow (max=512)`. The crash buffer identifies the process as
`com.android.vending`; Nimbo remained alive. The Play Store dialog was dismissed
before the product smoke continued. This system-app event is retained in the
private mode-0600 evidence bundle and is not attributed to Nimbo.

## Reviewable UI evidence

- [Clean Russian onboarding](evidence/android-phone-vc8-2026-08-31/onboarding-clean.png)
  and [accessibility tree](evidence/android-phone-vc8-2026-08-31/onboarding-clean.xml)
- [Live Tashkent forecast](evidence/android-phone-vc8-2026-08-31/tashkent-live.png)
  and [accessibility tree](evidence/android-phone-vc8-2026-08-31/tashkent-live.xml)
- [Native share chooser](evidence/android-phone-vc8-2026-08-31/share-sheet.png)
  and [accessibility tree](evidence/android-phone-vc8-2026-08-31/share-sheet.xml)
- [Proven-offline cached cold start](evidence/android-phone-vc8-2026-08-31/offline-proven-cold-start.png)
  and [accessibility tree](evidence/android-phone-vc8-2026-08-31/offline-proven-cold-start.xml)
- [Offline refresh fallback](evidence/android-phone-vc8-2026-08-31/offline-refresh.png)
  and [accessibility tree](evidence/android-phone-vc8-2026-08-31/offline-refresh.xml)
- [Recovered online refresh](evidence/android-phone-vc8-2026-08-31/restored-refresh.png)
  and [accessibility tree](evidence/android-phone-vc8-2026-08-31/restored-refresh.xml)

The complete APK/APKS, pulled installed bytes, signer output, package dump,
device properties, logs, screenshots, UI trees, and hashes are retained outside
the public repository under an owner-only directory (`0700`, files `0600`). No
credential material is present in that bundle.

## Remaining boundary

This pass binds the exact phone AAB to a local universal APK and a clean physical
API 25 runtime. It is not Google Play app-signing-key delivery evidence and does
not prove split selection on Play. Still missing are Play Internal delivery,
physical phone verification of the Play-delivered package, physical
tablet/widget coverage, and paired physical Wear OS coverage for version code
`1000008`. No upload, internal-track assignment, public rollout, crash-vitals,
or public availability is claimed.
