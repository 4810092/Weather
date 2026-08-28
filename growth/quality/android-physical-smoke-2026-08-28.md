# Android physical-device smoke — 2026-08-28

## Verdict

- **PASS** on a General Mobile 4G Dual running Android 7.1 / API 25 for clean first launch, Russian quick-city localization, quick-city selection, live Open-Meteo weather, location-free Toshkent search, saved-place cold start, and process stability on the final APK.
- The tested installed APK was byte-for-byte identical to the final host debug APK.
- The Samsung device carrying the existing public Nimbo `1.0.1 (5)` installation was inspected only to confirm its version and was not modified, launched, cleared, or reinstalled.
- The General Mobile debug package was installed by this QA run, contained no pre-existing user data, and was uninstalled after evidence capture.

## Artifact and device

| Field | Value |
|---|---|
| APK | `app/build/outputs/apk/debug/app-debug.apk` |
| SHA-256 | `7cb445efd4e7fbc9454a451ea6ad80ad84f4381fcececac0198cf20071ba5e10` |
| Package / version | `uz.ganikhodjaev.weather` / `1.0.2 (6)` |
| Device | General Mobile 4G Dual (`gm4g_sprout`) |
| Android | API 25 |
| Security patch | `2017-05-05` |
| Display | 720 × 1280 at 320 dpi |
| Network | Validated Wi-Fi |
| System locale exercised | Russian |

The pulled installed `base.apk` and the host APK both produced the SHA-256 above.

## Scenarios

| Scenario | Result | Evidence |
|---|---|---|
| Clean launch after `pm clear` | PASS | Russian onboarding showed `Ташкент`, `Самарканд`, and `Наманган`; stable city IDs/coordinates remain separate from localized display names |
| Select `Ташкент` without requesting location | PASS | Persisted `Ташкент, Узбекистан`; live 29°C forecast, yesterday comparison, and first-forecast tip rendered |
| Search `Toshkent` | PASS | Results included localized `Ташкент, Узбекистан`; no location permission was needed |
| Select searched `Ташкент, Узбекистан` | PASS | Live forecast and localized timeline rendered |
| Saved-place cold start | PASS | Force-stop plus explicit start reopened live `Ташкент, Узбекистан`; `TotalTime: 1215 ms` |
| TLS and process stability | PASS within tested paths | No Nimbo fatal process, `SSLHandshakeException`, `CertPath`, or certificate exception appeared in filtered logcat |
| Cleanup | PASS | `adb uninstall uz.ganikhodjaev.weather` returned `Success`; `pm path` confirmed removal |

Evidence:

- [Toshkent live screenshot](evidence/android-physical-2026-08-28-api25-live.png) · [UI tree](evidence/android-physical-2026-08-28-api25-live.xml)
- [Bukhara live screenshot](evidence/android-physical-2026-08-28-api25-bukhara.png) · [UI tree](evidence/android-physical-2026-08-28-api25-bukhara.xml)
- [Saved Bukhara cold-start UI tree](evidence/android-physical-2026-08-28-api25-cold.xml)
- [Final localized onboarding](evidence/android-physical-2026-08-28-api25-final-localized-onboarding.png) · [UI tree](evidence/android-physical-2026-08-28-api25-final-localized-onboarding.xml)
- [Final localized quick-city forecast](evidence/android-physical-2026-08-28-api25-final-localized-tashkent.png) · [UI tree](evidence/android-physical-2026-08-28-api25-final-localized-tashkent.xml) · [cold-start UI tree](evidence/android-physical-2026-08-28-api25-final-localized-cold.xml)
- [Final Toshkent search results](evidence/android-physical-2026-08-28-api25-final-search-results.xml) · [selected live screenshot](evidence/android-physical-2026-08-28-api25-final-search-live.png) · [UI tree](evidence/android-physical-2026-08-28-api25-final-search-live.xml)

## Boundary

This is a narrow physical smoke, not a full matrix. Physical Android tablet,
TalkBack, RTL, widget, Wear OS, and forced-offline scenarios remain separate.
Offline recovery was exercised on API 24 emulator with the same APK hash and is
documented in `android-emulator-smoke-2026-08-28.md`.
