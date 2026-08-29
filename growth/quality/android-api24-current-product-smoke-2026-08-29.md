# Android API 24 current-product smoke — 2026-08-29

Status: **PASS for exact product source
`9c2dce4200dbba5487c8c458ade4616005fde6e6` on an API 24 emulator**.

The rerun was performed at `2026-08-29 22:08–22:15 +05:00` after the
forecast-storage failure hardening landed.

This is compatibility and regression evidence for the supported Android floor.
It is not an upload-signed release, physical-device, tablet, widget, Wear OS,
Play delivery, review, rollout, or public-availability result. The Android
release and physical-device gates remain blocked.

## Identity and source boundary

- Repository HEAD at test time and tested standalone product source:
  `9c2dce4200dbba5487c8c458ade4616005fde6e6`, tree
  `6c23f88dd5f36b428bee6921e30a0cdde6cbea89`.
- The build ran in a full standalone clone with its own `.git` directory under
  an external `mktemp` path. It was detached at the exact commit, had an empty
  `git status --porcelain`, and was not a registered worktree of this checkout.
- `./gradlew --no-daemon --rerun-tasks :app:assembleDebug` passed with 62 of 62
  tasks executed.
- The debug APK contains AGP `9.3.1` app metadata but no
  `META-INF/version-control-info.textproto` and no embedded commit bytes. Its
  exact-source identity is therefore bounded by the clean standalone checkout,
  build command, and artifact hash; this report does not claim an embedded VCS
  revision for the APK.
- Installed package: `uz.ganikhodjaev.weather`, `1.1.0 (8)`, min/target SDK
  `24/36`.
- Built APK and `adb exec-out` streamed installed bytes SHA-256:
  `168bb6acdb95453a8dfd141947edbcb9292b756fd3429fffa56fc4baf125dbec`.
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
| Fresh uninstall/install and empty app data | PASS; a stale preflight package entry was removed, package absence was confirmed, and the final installed bytes matched the standalone APK |
| Localized onboarding | PASS |
| Quick-city Tashkent without runtime location permission | PASS; location grants remained empty |
| Clean-cache live Open-Meteo forecast | PASS; forecast comparison and Best Time Outside rendered |
| First-forecast activation tip | PASS; the tip rendered after the successful forecast |
| Tip acknowledgement | PASS; `Got it` removed the tip and the acknowledged state persisted across cold start |
| Online cold start | PASS; Tashkent persisted, the acknowledged tip stayed suppressed, and reported `TotalTime` was 127 ms |
| Offline cached manual refresh | PASS; the emulator data transport was disabled, Open-Meteo DNS resolution failed, cached content remained, and `Couldn’t refresh. Showing saved weather.` rendered |
| Network recovery and manual refresh | PASS; data transport, DNS/connectivity, and the Open-Meteo host ping recovered on the first check, then the warning cleared after refresh |
| Process health | PASS; the app remained resumed and alive |

The relevant Nimbo log emitted the expected network-security-configuration line
twice. The product-scoped bounded filter found zero `SSLHandshakeException`,
`CertPathValidatorException`, trust-anchor, peer/certificate-chain, Nimbo-PID
fatal-signal/`FATAL EXCEPTION`, Nimbo process marker, or Nimbo ANR lines. The
empty filter output SHA-256 was
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

A broader raw-log search also found two `FATAL EXCEPTION IN SYSTEM PROCESS`
lines. Both were test-harness command processes, PIDs `3644` and `4094`, whose
stack traces begin at `com.android.commands.svc.Svc` and end in
`SecurityException: WifiService: Neither user 2000 nor current process has
android.permission.CHANGE_WIFI_STATE`. They were caused by the unsupported
`adb shell svc wifi` probes, not by Nimbo; Nimbo used PIDs `3405` and `3577`,
remained alive/resumed, and its offline state was independently established by
the disabled data transport and failed DNS lookup. The distinction is retained
here rather than relabelling the broad filter as empty.

## Selected visual evidence

- [Onboarding](evidence/android-api24-current-product-2026-08-29/onboarding.png)
  — SHA-256
  `a7e216c3add08f237ac872f3a1787db0de14342598c082294a6e926f00d8cf53`.
- [Live forecast and first-forecast tip](evidence/android-api24-current-product-2026-08-29/live-tip.png)
  — SHA-256
  `29dbdebf2a652c7f43c3bbadc9e146bd23f2439cd8c5c266069a0964423f09e3`.
- [Offline cached forecast](evidence/android-api24-current-product-2026-08-29/offline-cache.png)
  — SHA-256
  `18093aac61a0d747922708c3180bb675ef14ab9647006b9d9ece5f725e5a9eb9`.
- [Recovered live forecast](evidence/android-api24-current-product-2026-08-29/recovered.png)
  — SHA-256
  `f48a419a4cbcb806aa73824b696407d08b3501ce2d896a6ee93e771939592de6`.

Only the four reviewed, non-PII screenshots were retained. Raw emulator,
device-state, package, network, and log artifacts remain outside the repository.
The temporary app was uninstalled, network connectivity was restored and
verified, and the emulator was stopped.
