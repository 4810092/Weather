# Android provider-throttle physical smoke — 2026-08-29

## Verdict

**PASS within the bounded debug/source scope** on a physical General Mobile
4G Dual running Android 7.1.1 / API 25. The exact post-throttle commit
`2004e4f237ce4f176a106d465ecc21b2dc36d741` completed clean onboarding, a live
Tashkent forecast, a provider-blocked fresh-cache cold start without an
automatic refresh failure, an explicit manual-refresh failure, recovery, and
device cleanup.

This is not a release-artifact pass. The APK is debuggable and signed with the
Android debug certificate. Current upload-signed vc8, a release-certificate
physical pass, tablet/widget coverage, and paired Wear OS coverage remain
missing, so `android_physical_smoke` and `release_artifact_source_sync` remain
blocked.

## Artifact and device

| Field | Value |
|---|---|
| Source commit | `2004e4f237ce4f176a106d465ecc21b2dc36d741` |
| Local APK | `app/build/outputs/apk/debug/app-debug.apk` |
| APK SHA-256 | `1d3ade497395c349d0fda77e72f76e494da230933d9aa011ac71bb475f48a31e` |
| Package / version | `uz.ganikhodjaev.weather` / `1.1.0 (8)` |
| APK signature | v2, `C=US, O=Android, CN=Android Debug` |
| Debug certificate SHA-256 | `7b112e7dce7a8e61ec85b2187fbc642fa196909a53351d298126ca2e23ffe3f8` |
| Device | General Mobile 4G Dual (`gm4g_sprout`, serial `e76fd426`) |
| OS / display / locale | Android 7.1.1 / API 25; 720 x 1280; Russian |
| Execution window | `2026-08-29 04:09–04:15 +05:00` |

## Scenarios

| Scenario | Result | Evidence observed |
|---|---|---|
| Clean install and launch | PASS | `adb install` returned `Success`; package state reported vc8, `1.1.0`, minSdk 24, targetSdk 36, and `DEBUGGABLE` |
| Onboarding and live forecast | PASS | Russian onboarding exposed quick cities and search; selecting `Ташкент` rendered `Ташкент, Узбекистан`, 25°, `Ясно`, comparison text, the first-forecast tip, and localized controls |
| Fresh-cache automatic gate | PASS | With the system proxy temporarily set to unreachable `127.0.0.1:9`, force-stop plus cold launch immediately rendered the saved forecast; no saved-weather warning and no Nimbo network-failure, TLS, or fatal-process log appeared |
| Manual bypass | PASS | Tapping `Обновить` while the proxy remained blocked preserved cached content, rendered `Не удалось обновить. Показана сохранённая погода.`, and logged the expected `ConnectException` |
| Recovery | PASS | After clearing the proxy through the platform no-proxy state and reconnecting Wi-Fi, a new process plus explicit refresh retained normal live content with no failure warning or Nimbo network error |
| Cleanup | PASS | The temporary package and device-side UI dumps were removed; proxy host/port returned to absent, airplane mode remained `0`, Wi-Fi remained `1`, locale remained `ru-RU`, package absence was verified, and external ping succeeded |

The fresh-cache check is direct runtime evidence for the new automatic gate,
not a measured provider billing claim. Automated tests remain the source of
truth for exact one-hour boundaries, cross-path single-flight, clock rollback,
cache-read fail-closed behavior, and per-location attempt cooldown.

## Boundary

The Samsung API 36 phone retains public Nimbo `1.0.1 (5)` and was only inspected
read-only; it was not launched, cleared, or reinstalled. No store build was
signed, uploaded, submitted, or published by this smoke.
