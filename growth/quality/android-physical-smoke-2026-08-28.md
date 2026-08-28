# Android physical-device smoke — 2026-08-28

## Verdict

- **PASS** on a General Mobile 4G Dual running Android 7.1 / API 25 for a clean install of the exact signed phone release candidate `1.1.0 (7)`, Russian onboarding, quick-city selection, live Open-Meteo weather, saved-place cold start, matching installed artifact/signing identity, and process stability.
- The post-Fragment debug runtime candidate separately passed Android share-sheet launch, 150% system text, TalkBack focus/semantics, and a naturally scheduled background refresh that updated weather, daily, and air-quality caches. These checks are not relabelled as signed-release executions.
- An earlier candidate passed location-free Toshkent search on the same device. AndroidX Fragment 1.9.0 is explicitly selected in every Android target.
- The Samsung device carrying the existing public Nimbo `1.0.1 (5)` installation was inspected only to confirm its version and was not modified, launched, cleared, or reinstalled.
- All General Mobile packages were installed by this QA run and contained no pre-existing Nimbo user data. The signed release candidate was removed after the final cold-start check.

## Artifact and device

| Field | Value |
|---|---|
| APK | `/Users/khasan/work/ganikhodjaev/.nimbo-release/android/1.1.0-internal/nimbo-phone-1.1.0-vc7-universal.apk` |
| SHA-256 | `2067f4b06b3c857f2aa86b5284447b3db7a1f1d91c58a9f1d666573e84be48d6` |
| Package / version | `uz.ganikhodjaev.weather` / `1.1.0 (7)` |
| Signer SHA-256 | `431548a4871c9c090eee808ac3a34898f5d78602d9e747dfe81e228415aac252` |
| Device | General Mobile 4G Dual (`gm4g_sprout`) |
| Android | API 25 |
| Security patch | `2017-05-05` |
| Display | 720 × 1280 at 320 dpi |
| Network | Validated Wi-Fi |
| System locale exercised | Russian |

The pulled installed `base.apk` and the immutable universal APK both produced
the SHA-256 above. `apksigner` verified v2/v3 signatures and the exact upload
certificate fingerprint. Full AAB and APK evidence is recorded in
`android-release-artifacts-2026-08-28.md`.

The separate debug accessibility/share/background artifact was
`uz.ganikhodjaev.weather` `1.0.2 (6)`, SHA-256
`4fdb6cea767694e3e43233728851ff358ab26f68a166a6cc1f9d6e4c810ac131`.

## Scenarios

| Scenario | Result | Evidence |
|---|---|---|
| Clean signed install and first launch | PASS, signed `1.1.0 (7)` | Russian onboarding showed `Ташкент`, `Самарканд`, and `Наманган`; installed APK hash, version, and signer matched the release artifact |
| Select `Ташкент` without requesting location | PASS, signed `1.1.0 (7)` | Persisted `Ташкент, Узбекистан`; live forecast, yesterday comparison, first-forecast tip, and timeline rendered |
| Saved-place cold start | PASS, signed `1.1.0 (7)` | Force-stop plus explicit start reopened live `Ташкент, Узбекистан`; `TotalTime: 924 ms` |
| Android share sheet | PASS, debug hash `4fdb6cea…` | Share action opened the native chooser with system targets. Payload/link policy is covered separately by automated tests; the chooser capture does not expose the payload |
| 150% system text | PASS, debug hash `4fdb6cea…` | Live weather remained readable and scrollable with no visible clipping; `font_scale` was restored from `1.5` to the original `1.0` after capture |
| TalkBack | PASS, debug hash `4fdb6cea…` | TalkBack was the active spoken accessibility service with touch exploration enabled; linear navigation produced a visible focus ring, and the UI tree exposed localized descriptions for Share, Refresh, Change place, and hourly conditions |
| Scheduled background refresh | PASS, debug hash `4fdb6cea…` | WorkManager's naturally due run returned `SUCCESS` and advanced all weather/daily/AQI cache timestamps; an early forced trigger was correctly rescheduled |
| Search `Toshkent` | PASS, predecessor hash | Results included localized `Ташкент, Узбекистан`; no location permission was needed |
| Select searched `Ташкент, Узбекистан` | PASS, predecessor hash | Live forecast and localized timeline rendered |
| TLS and process stability | PASS within tested paths | No Nimbo fatal process, `SSLHandshakeException`, `CertPath`, or certificate exception appeared in filtered logcat |
| Device-setting restoration | PASS | TalkBack/accessibility returned to disabled with no enabled service; `font_scale=1.0`; forced-RTL debug property returned to `0` and the global override is absent |

Evidence:

- [Toshkent live screenshot](evidence/android-physical-2026-08-28-api25-live.png) · [UI tree](evidence/android-physical-2026-08-28-api25-live.xml)
- [Bukhara live screenshot](evidence/android-physical-2026-08-28-api25-bukhara.png) · [UI tree](evidence/android-physical-2026-08-28-api25-bukhara.xml)
- [Saved Bukhara cold-start UI tree](evidence/android-physical-2026-08-28-api25-cold.xml)
- [Final localized onboarding](evidence/android-physical-2026-08-28-api25-final-localized-onboarding.png) · [UI tree](evidence/android-physical-2026-08-28-api25-final-localized-onboarding.xml)
- [Final localized quick-city forecast](evidence/android-physical-2026-08-28-api25-final-localized-tashkent.png) · [UI tree](evidence/android-physical-2026-08-28-api25-final-localized-tashkent.xml) · [cold-start UI tree](evidence/android-physical-2026-08-28-api25-final-localized-cold.xml)
- [Final Toshkent search results](evidence/android-physical-2026-08-28-api25-final-search-results.xml) · [selected live screenshot](evidence/android-physical-2026-08-28-api25-final-search-live.png) · [UI tree](evidence/android-physical-2026-08-28-api25-final-search-live.xml)
- [Post-Fragment-fix onboarding](evidence/android-physical-2026-08-28-api25-fragment-onboarding.png) · [UI tree](evidence/android-physical-2026-08-28-api25-fragment-onboarding.xml)
- [Post-Fragment-fix live forecast](evidence/android-physical-2026-08-28-api25-fragment-live.png) · [UI tree](evidence/android-physical-2026-08-28-api25-fragment-live.xml)
- [Native share sheet](evidence/android-physical-2026-08-28-api25-share-sheet.png) · [UI tree](evidence/android-physical-2026-08-28-api25-share-sheet.xml)
- [150% text](evidence/android-physical-2026-08-28-api25-large-text.png) · [UI tree](evidence/android-physical-2026-08-28-api25-large-text.xml)
- [TalkBack active](evidence/android-physical-2026-08-28-api25-talkback.png) · [UI tree](evidence/android-physical-2026-08-28-api25-talkback.xml) · [linear-focus screenshot](evidence/android-physical-2026-08-28-api25-talkback-focus.png) · [UI tree](evidence/android-physical-2026-08-28-api25-talkback-focus.xml)
- [Signed 1.1.0 onboarding](evidence/android-physical-2026-08-28-api25-signed-vc7-onboarding.png) · [UI tree](evidence/android-physical-2026-08-28-api25-signed-vc7-onboarding.xml)
- [Signed 1.1.0 live forecast](evidence/android-physical-2026-08-28-api25-signed-vc7-live.png) · [UI tree](evidence/android-physical-2026-08-28-api25-signed-vc7-live.xml)
- [Signed 1.1.0 cold start](evidence/android-physical-2026-08-28-api25-signed-vc7-cold.png) · [UI tree](evidence/android-physical-2026-08-28-api25-signed-vc7-cold.xml)
- [Naturally scheduled background refresh](evidence/android-physical-2026-08-28-api25-background-refresh.txt)

## Boundary

This is a phone smoke, not a full matrix. Physical Android tablet, widget, and
Wear OS remain separate. True RTL was exercised on an API 36 emulator in an
`ar_EG/ldrtl` configuration; the physical device's developer force-RTL flag did
not apply a genuine RTL configuration and is not counted as a pass. Offline
recovery was exercised on API 24 emulator and is documented in
`android-emulator-smoke-2026-08-28.md`. After QA, the General Mobile package was
absent, accessibility was disabled with no enabled service, and `font_scale`
was restored to `1.0`; the Samsung remained at public `1.0.1 (5)`.
