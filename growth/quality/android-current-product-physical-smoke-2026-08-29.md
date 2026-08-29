# Android current-product physical smoke — 2026-08-29

Status: **PASS for the bounded debug/physical API 25 scope**.

The run was performed at `2026-08-29 23:03–23:10 +05:00` after the
forecast-storage failure hardening landed. It closes the stale-product-source
gap for a physical Android phone, but it is not upload-signing, Play delivery,
tablet, widget, Wear OS, review, rollout, or public-availability evidence.

## Identity and source boundary

- Product source: `9c2dce4200dbba5487c8c458ade4616005fde6e6`.
- Repository HEAD at build time: `01c29096c451c1a45ec070f089a62387a2174faa`.
  Every path changed after the product commit was limited to workflows,
  documentation, growth evidence/dashboard inputs, and the store upload
  manifest; no app, Wear, shared, iOS, resource, Gradle, or product source path
  differed.
- The worktree was clean when `./gradlew --no-daemon :app:assembleDebug`
  passed. The APK contains no embedded VCS record, so source identity is bounded
  by that clean checkout, the product-path comparison above, the build command,
  and the artifact hash rather than a claimed in-APK revision.
- Local APK and streamed installed `base.apk` SHA-256:
  `52146b883a04e4c2d272ea4e3ecc9b1277a8c78c117b547a121de3a7d90c3730`.
- Package/version: `uz.ganikhodjaev.weather`, `1.1.0 (8)`, min/target SDK
  `24/36`.
- Debug certificate SHA-256:
  `7b112e7dce7a8e61ec85b2187fbc642fa196909a53351d298126ca2e23ffe3f8`.
- Device: dedicated General Mobile 4G Dual, physical Android 7.1.1 / API 25,
  720 x 1280 at 320 dpi, Russian locale. The package was absent before the run.

## Exercised paths

| Scenario | Result |
| --- | --- |
| Clean install and localized onboarding | PASS; Russian value-first onboarding rendered Tashkent, Samarkand, Namangan, ordinary search, and optional approximate-location disclosure |
| Tashkent without location permission | PASS; selecting the quick city rendered live Open-Meteo conditions without granting location access |
| Forecast value and context | PASS; current/apparent temperature, yesterday comparison, upcoming change, Best Time Outside state, and the `24 hours ago / now / 24 hours ahead` timeline rendered |
| Late-day Best Time boundary | PASS; at about 23:04 Tashkent time the engine truthfully reported insufficient same-local-day future hours rather than fabricating a two-hour recommendation, while the cross-midnight hourly timeline remained populated |
| First-forecast tip | PASS; the contextual tip appeared after the successful forecast, `Got it` removed it, and it stayed suppressed after force-stop/cold start |
| Cached offline fallback | PASS; an intentionally unreachable system proxy caused manual refresh to retain the full cached forecast and show the localized saved-weather warning |
| Network recovery | PASS; the proxy was cleared, Wi-Fi was recycled to invalidate the legacy platform proxy cache, DNS/network reachability returned, and a fresh process plus manual refresh removed the warning |
| Process health | PASS within the exercised paths; the post-recovery product-scoped log filter contained zero Nimbo fatal exception, ANR, SSL handshake, CertPath, or trust-anchor matches |
| Cleanup | PASS; the test package and its newly created app data were uninstalled, proxy keys were absent, airplane mode was off, Wi-Fi and external reachability passed, locale/font/accessibility settings matched preflight, and the separate Samsung installation remained untouched |

The offline probe initially demonstrated a useful platform-specific testing
detail: deleting the Android 7 global proxy setting did not immediately clear
the framework's in-memory proxy. The first attempted recovery therefore
continued to fail with `ConnectException` and was not counted. Setting the
proxy to the platform's no-proxy sentinel, recycling Wi-Fi, deleting the
setting, starting a fresh process, and then refreshing produced the passing
recovery state. This was test-environment cleanup, not a product workaround.

## Selected evidence

- [Localized onboarding](evidence/android-current-product-physical-2026-08-29/onboarding.png)
  — SHA-256
  `79d1019cbfbb991d9066bf3c8c0e7eb97c790ba192801f3406d733126b543069`.
- [Live Tashkent forecast](evidence/android-current-product-physical-2026-08-29/tashkent-live.png)
  — SHA-256
  `212059f530878c4af6862e739fc96f995d221e27a9cf7d4551b9518935de12e2`.
- [Timeline and contextual tip](evidence/android-current-product-physical-2026-08-29/timeline.png)
  — SHA-256
  `c2724f65accb6d43917221bdcb112cf9d5d655cc90c51f6bf5f6a2e7cdda1179`.
- [Offline cached forecast](evidence/android-current-product-physical-2026-08-29/offline-cache.png)
  — SHA-256
  `a13906d1f7a579f82f4366058e3fac127e4ff9ffd8fd3bc8afa98e3cd90b067c`.
- [Recovered live forecast](evidence/android-current-product-physical-2026-08-29/recovered.png)
  — SHA-256
  `4438fd3bde09bd3f0a98197894d8fd49dcfa56842d663f0a8129cdc26c831773`.

Matching UIAutomator hierarchies are retained beside the five reviewed,
non-PII PNGs. The cold-start hierarchy proves the tip remained absent without
retaining an additional redundant screenshot.

## Remaining Android gate

The Android physical gate remains blocked because the exact-current phone and
Wear AABs are unsigned, there is no upload-signed physical rerun, no physical
tablet/widget result, and no paired physical Wear OS result. This report is
current-product physical regression evidence only and is not promoted to a
release or store claim.
