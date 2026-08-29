# Android first-forecast tip physical smoke — 2026-08-29

## Verdict

**PASS within the exact-source debug scope** for product commit
`9342824db7c0dcadfc4bdfe11f580377c108d968`.

On a clean physical Android 7.1.1 / API 25 install, the first successful
Tashkent forecast displayed the localized Russian first-forecast tip and its
`Добавить ещё один город` action. The action opened the normal location picker,
kept the existing Tashkent location available, acknowledged the tip only after
that explicit action, and did not re-display the tip after a force-stop/cold
launch. The stored acknowledgement contained both
expected `true` values. No matching fatal exception, app ANR, process-death,
activity-start, or SQLite failure appeared in the exercised logcat window.

This result is not upload signing, a release-candidate pass, a complete Android
device matrix, or evidence of production behavior. The Android physical and
release/source gates remain blocked until the source-current upload-signed
candidate passes the required phone, tablet, widget, and Wear OS matrix.

## Exact artifact and device

| Field | Value |
| --- | --- |
| Product commit | `9342824db7c0dcadfc4bdfe11f580377c108d968` |
| APK | `app/build/outputs/apk/debug/app-debug.apk` |
| APK SHA-256 | `40f3d15d9eed33761c4e53c86ed91ac26411817811fb93792e1eb65ef0a69227` |
| Installed bytes SHA-256 | `40f3d15d9eed33761c4e53c86ed91ac26411817811fb93792e1eb65ef0a69227` |
| Package / version | `uz.ganikhodjaev.weather` / `1.1.0 (8)` |
| Signing boundary | APK Signature Scheme v2; Android debug certificate SHA-256 `7b112e7dce7a8e61ec85b2187fbc642fa196909a53351d298126ca2e23ffe3f8` |
| Device | General Mobile 4G Dual (`gm4g_sprout`) |
| OS / display / locale | Android 7.1.1, API 25, 720 x 1280, Russian |

The build command was:

```sh
./gradlew :shared:allTests :app:testDebugUnitTest :app:assembleDebug
```

Gradle completed successfully. The installed `base.apk` was pulled before
cleanup and matched the local APK byte-for-byte by SHA-256.

## Scenarios

| Scenario | Result | Exact observation |
| --- | --- | --- |
| Clean activation | PASS | A clean install opened the value-led Russian onboarding and selected Tashkent without requesting location permission |
| Tip visibility | PASS | The first successful live forecast rendered `Прогноз готов`, the explanatory copy, `Добавить ещё один город`, and `Понятно` below the primary Best Time card |
| Action routing | PASS | Tapping `Добавить ещё один город` opened `Сменить место`; Tashkent remained in saved places and quick cities |
| Picker stability | PASS within exercised path | The picker remained visible during an eight-second observation window instead of being replaced by a weather refresh |
| Explicit acknowledgement | PASS | `nimbo_preferences.xml` stored `onboarding_completed_first_forecast=true` and `onboarding_acknowledged_first_forecast_tip=true` only after the CTA action |
| Cold-start suppression | PASS | Force-stop and launcher start restored cached weather without the acknowledged tip |
| Process stability | PASS within exercised paths | Filtered logcat contained zero matching fatal, ANR, process-death, activity-start, or SQLite failure lines |
| Cleanup | PASS | The debug package was uninstalled; locale remained `ru-RU` and `font_scale` remained `1.0` |

## Captured evidence

| File | SHA-256 |
| --- | --- |
| `tip-visible.png` | `d5d114ae8a2969d45764f8c5209a9674accff4e4b5c9d7e7b1e8b9bc8b3956bb` |
| `tip-visible.xml` | `80820a20352c4e6b0bd2f61f6d81262083f245d5514544dc54611c26ed587192` |
| `location-picker.png` | `87fac34b98d9c8b80dbc41bac2766f6ff667e98b552c6fef4add0e20474cf294` |
| `location-picker.xml` | `57fe405f44fd5a9af2d56b92cf0759e8ee958def134ff074153b38cb6cd2af0c` |
| `cold-start.png` | `c931460ab27ac0522c74740d8cc2b6d592f6ec935afc9d2c775e243221d06e1c` |
| `cold-start.xml` | `e4ca9a72b0c58e1f88abbe828c7647ff1d0aaffa257ba203f7742fcb79367980` |

The files are retained under
`growth/quality/evidence/android-first-tip-9342824-api25/`.

## Boundary

This smoke proves the new durable/actionable tip behavior on one exact debug APK
and one physical phone. It does not prove upload signing, Play processing,
production availability, tablet or widget layout, paired Wear behavior,
retention lift, conversion lift, or ranking impact.
