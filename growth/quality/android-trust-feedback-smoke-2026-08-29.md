# Android trust and feedback smoke — 2026-08-29

Status: **PASS within the exact debug/API 25 scope**.

This does not close the release-device gate. The tested bytes use the Android
debug certificate and are neither upload-signed nor Play-signed. No review,
message, form, location, account data, or analytics event was submitted.

## Identity

- Source: exact product commit
  `df5f82401348a2cca7405feec36c03621af43ea7`.
- Device: General Mobile 4G Dual `e76fd426`, Android 7.1.1 / API 25,
  `ru-RU`.
- Package: `uz.ganikhodjaev.weather`, `1.1.0 (8)`, minSdk 24,
  targetSdk 36, `armeabi-v7a`.
- Local and pulled installed APK SHA-256:
  `fb039c02964a0cbd49d9702998a2cba967c63bbc9ff368bcda9ea44936f0c753`.
- Debug certificate SHA-256:
  `7b112e7dce7a8e61ec85b2187fbc642fa196909a53351d298126ca2e23ffe3f8`.
  This is explicitly not the upload or Play app-signing identity.

## Bounded flow

1. The device had no installed Nimbo package before the run. The exact debug
   APK was installed fresh.
2. Tashkent was selected from onboarding without requesting or granting
   location permission. Nimbo loaded a live `34°` / `Ясно` forecast and the
   comparison with yesterday.
3. The footer rendered `Помощь и обратная связь` and `Оценить Nimbo`; both
   parent action nodes reported `clickable=true`.
4. Help opened an Android `VIEW` intent for exactly
   `https://nimbo.uz/support/` in Chrome.
5. Rate opened the Play details surface for package
   `uz.ganikhodjaev.weather` in `com.android.vending`. No rating, review, or
   text was entered.
6. Logcat collected after a pre-install clear contained zero matching Nimbo
   `FATAL` or ANR lines. This bounded absence is not a production crash-free
   metric.

The current public Play listing told this legacy API 25 device that the public
version is no longer compatible. That is a live catalog/version boundary, not
evidence that the exact debug candidate failed its declared minSdk 24 runtime
path. Store-derived compatibility must be rechecked after an exact-current
signed upload.

## Cleanup

Nimbo was force-stopped and uninstalled after capture. Package path and process
queries were empty, and all temporary device-side UI dumps were removed. The
connected Samsung installation was not changed.

The capture set was reviewed during the run. Representative transient hashes
were footer PNG
`5bbb53de6749f14a96050ce92b6c4f23940b130808c107c82a77d88bf0503f65`,
Help destination PNG
`ab45b61eb73ffbac7cd6f3840edeb7602048b01bca0434c00d2e2ee67f43f2e9`,
Play destination PNG
`1aace6953c31b958a9dac717281f93df81ef73f2f3c5dc1ceb71690e9579283b`,
and bounded logcat
`cb97cbb74ee790b4fb172711767120a0f1ff8c8abc9a7b8533eea1569e1ff589`.
The repository intentionally retains the aggregate, non-PII evidence record
rather than committing debug APKs or raw device captures.
