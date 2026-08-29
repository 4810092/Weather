# Android API 24 current-product smoke — 2026-08-29

Status: **PASS for the exact current product source on an API 24 emulator**.

This is compatibility and regression evidence for the supported Android floor.
It is not an upload-signed release, physical-device, tablet, widget, Wear OS,
Play delivery, review, rollout, or public-availability result. The Android
release and physical-device gates remain blocked.

## Identity and source boundary

- Repository HEAD: `94d8883e55d6652196d05febafdc70f08f83f45b`.
- Recorded product source:
  `9342824db7c0dcadfc4bdfe11f580377c108d968`.
- Tracked product paths were byte-identical from the recorded source through
  HEAD and the working tree; no untracked product file was present.
- `./gradlew --no-daemon --rerun-tasks :app:assembleDebug` passed with 62 of 62
  tasks executed.
- Installed package: `uz.ganikhodjaev.weather`, `1.1.0 (8)`, min/target SDK
  `24/36`.
- Built and pulled-installed APK SHA-256:
  `c28a2ca94823a1bbcf54f5aa8e329dd217d4830e2831ae28e252e9646abba6c4`.
- Debug certificate SHA-256:
  `7b112e7dce7a8e61ec85b2187fbc642fa196909a53351d298126ca2e23ffe3f8`.

## Environment

The `Steppe_API24` emulator was cold-booted with snapshot loading and saving
disabled:

```sh
emulator -avd Steppe_API24 -port 5554 \
  -no-window -no-audio -no-snapshot-load -no-snapshot-save \
  -gpu swiftshader_indirect
```

The image was Android 7.0 / API 24, `arm64-v8a`, security patch
`2017-10-05`, English (US). The emulator was shut down after cleanup.

## Exercised paths

| Scenario | Result |
| --- | --- |
| Fresh uninstall/install and empty app data | PASS |
| Localized onboarding | PASS |
| Quick-city Tashkent without runtime location permission | PASS; location grants remained empty |
| Clean-cache live Open-Meteo forecast | PASS; forecast comparison and Best Time Outside rendered |
| First-forecast activation tip | PASS; the tip rendered after the successful forecast |
| Tip acknowledgement | PASS; `Got it` removed the tip and persisted both onboarding booleans |
| Online cold start | PASS; Tashkent persisted, the acknowledged tip stayed suppressed, and reported `TotalTime` was 137 ms |
| Offline cached manual refresh | PASS; cached content remained and the saved-weather warning rendered |
| Network recovery and manual refresh | PASS; validated connectivity returned after two seconds and the warning cleared after refresh |
| Process health | PASS; the app remained resumed and alive |

The relevant Nimbo log emitted the expected network-security-configuration line
twice. The bounded log filter found zero `SSLHandshakeException`,
`CertPathValidatorException`, trust-anchor, peer/certificate-chain, fatal-signal,
`FATAL EXCEPTION`, or ANR lines. The empty filter output SHA-256 was
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

## Selected visual evidence

- [Onboarding](evidence/android-api24-current-product-2026-08-29/onboarding.png)
  — SHA-256
  `86647a31f5d2f38ce0c07d4711758783881c0a5355c71a5f1b21c31334fb0265`.
- [Live forecast and first-forecast tip](evidence/android-api24-current-product-2026-08-29/live-tip.png)
  — SHA-256
  `7d41dd7381c7b386ae18d39744931cb415b277acb3e1cfde554ee7bc2f0e9718`.
- [Offline cached forecast](evidence/android-api24-current-product-2026-08-29/offline-cache.png)
  — SHA-256
  `257ab10b7c20e076d09cfaf3c431943f347765896bf9aaa820bda4b482801747`.
- [Recovered live forecast](evidence/android-api24-current-product-2026-08-29/recovered.png)
  — SHA-256
  `b69661411a797990bc4b3bf134588730ea687755439571a40898f8e4fab0324c`.

Only the four reviewed, non-PII screenshots were retained. Raw emulator,
device-state, package, network, and log artifacts remain outside the repository.
The temporary app was uninstalled, network connectivity was restored and
verified, and the emulator was stopped.
