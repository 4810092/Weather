# Android current-product physical smoke — 2026-08-30 (`2cdd438`)

Status: **PASS for the bounded debug/physical API 25 phone scope**.

The run was performed at `2026-08-30 14:07–14:21 +05:00` from the exact
current product authority. It adds physical-phone evidence for normal live
provider decoding, denied-location fallback, ordinary city search, cached
offline behavior, recovery, and the home-screen widget. It is not upload
signing, Play delivery, physical-tablet, Wear OS, review, rollout, or public
availability evidence.

## Identity and source boundary

- Product source: `2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652`.
- Repository evidence HEAD before the run:
  `0b3f8d067b941d14d108e159717b41c855a397c4`. The current source-authority
  verifier resolved that HEAD to the full product source above.
- The debug APK was built in a clean isolated detached clone checked out
  directly at `2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652` with Java 21 and
  `./gradlew --no-daemon :app:assembleDebug`. The main worktree was not used as
  a build tree and no full local CI run was performed.
- Local APK and pulled installed `base.apk` SHA-256:
  `d66c8f0f9b05232cf484bd95223328a44f2a0bddf1d2f76817ef9504f87fe047`.
- Package/version: `uz.ganikhodjaev.weather`, `1.1.0 (8)`, min/target SDK
  `24/36`; APK size `16,125,227` bytes.
- Debug certificate SHA-256:
  `7b112e7dce7a8e61ec85b2187fbc642fa196909a53351d298126ca2e23ffe3f8`.
  `apksigner` verified the APK's v2 signature. This is explicitly not the
  upload certificate.
- Device: dedicated General Mobile 4G Dual `e76fd426`, physical Android
  `7.1.1` / API 25, 720 x 1280 at 320 dpi. Nimbo was absent before the clean
  install. The separate Samsung device and its existing Nimbo state were not
  changed.

## Exercised paths

| Scenario | Result |
| --- | --- |
| Clean install and localized onboarding | PASS; the Russian value-first onboarding rendered quick Uzbekistan cities, ordinary search, and the optional approximate-location path |
| Denied approximate location | PASS; the Android permission dialog was exercised and denied; `ACCESS_COARSE_LOCATION` remained `granted=false` with `USER_SET`, and Nimbo instructed the user to search manually |
| Ordinary city search | PASS; `Bukhara` returned `Бухара, Узбекистан` and selecting it loaded the forecast without a location grant |
| Live Open-Meteo forecast | PASS; Bukhara rendered `42°`, clear conditions, feels-like `40°`, the yesterday comparison, upcoming change, and a localized `20:00–22:00` Best Time recommendation |
| Cached cold start and explicit retry | PASS; an intentionally unreachable loopback proxy preserved the cached forecast after force-stop/cold start; manual refresh showed `Не удалось обновить. Показана сохранённая погода.` |
| Network recovery | PASS; the proxy was reset to the Android no-proxy sentinel and removed, a fresh process plus manual refresh removed the saved-weather warning, and the live forecast remained populated |
| Android home-screen widget | PASS; Google Now Launcher exposed `Nimbo 3 x 2`; widget id `3` bound to `WeatherWidgetProvider` and rendered Bukhara, `42°C`, high/low, precipitation, and `AQI 52` |
| Widget tap | PASS; tapping the populated widget resumed `uz.ganikhodjaev.weather/.MainActivity` with the same Bukhara forecast |
| Process health | PASS within the exercised paths; the retained 49-line post-recovery product log and a final PID-scoped filter contained zero fatal-exception, ANR, SSL-handshake, CertPath, or trust-anchor matches |
| Cleanup | PASS; Nimbo was uninstalled, package and widget/provider references disappeared, the launcher returned to its default page with the pre-existing Ekho VPN icon, `http_proxy` was absent, proxy host/exclusion/PAC values were empty, proxy port remained `0`, and `wifi_on` remained `3` |

The proxy fault was limited to the dedicated test phone. Its global proxy
values were captured before mutation and matched again after recovery and
cleanup. Current-run temporary files were removed from shared storage after
their non-PII copies were retained below.

## Selected evidence

- [Localized onboarding](evidence/android-current-product-physical-2026-08-30-2cdd438/onboarding.png)
  — SHA-256
  `701a3f031ff5ba46d355bb0840bb10945175d0886e614824f9f4323d4ae1e854`.
- [Android approximate-location prompt](evidence/android-current-product-physical-2026-08-30-2cdd438/permission.png)
  — SHA-256
  `44faa576a2ecd01a42c7d4d00cadb508d5d9831821cc248a977341ef4373aab2`.
- [Denied-location fallback](evidence/android-current-product-physical-2026-08-30-2cdd438/after-deny.png)
  — SHA-256
  `8ec18a41550bba3bf658ea6e4572556628b10eac7937bdebdeba5927dc4117d6`.
- [Manual Bukhara search](evidence/android-current-product-physical-2026-08-30-2cdd438/search.png)
  — SHA-256
  `bc279fd52b8c062a793bd122410fe648ea2afd090e99527942537c116ebe9d43`.
- [Live Bukhara forecast](evidence/android-current-product-physical-2026-08-30-2cdd438/forecast.png)
  — SHA-256
  `6ddf7d3503744d7fbb58233e47aac0eb8d5ea400a7c2015264a32828a2739c9e`.
- [Cached forecast after failed manual refresh](evidence/android-current-product-physical-2026-08-30-2cdd438/offline-refresh.png)
  — SHA-256
  `887a5c24befa8922f7034af6f45f57abe56ee30f72b2a486f7b0ced6983ce0a4`.
- [Recovered live forecast](evidence/android-current-product-physical-2026-08-30-2cdd438/recovered.png)
  — SHA-256
  `dbcdd7658a6f2de57bb758eb73b6b13f417715519b789b786537b6a27aec5405`.
- [Populated physical API 25 widget](evidence/android-current-product-physical-2026-08-30-2cdd438/widget.png)
  — SHA-256
  `83d3d0c7a2c2733732f39d4c5b2cf5b442a3d4d4bd459f7774c51d6909119e45`.
- [Forecast after widget tap](evidence/android-current-product-physical-2026-08-30-2cdd438/widget-tap.png)
  — SHA-256
  `a9f7422ae47c7256784fe901e146e811661874e74ea24da07e8f50bde60dcd15`.
- [Post-recovery process log](evidence/android-current-product-physical-2026-08-30-2cdd438/recovered-logcat.txt)
  — SHA-256
  `115004a0959052e8b72fcadca1748dad27dcdf11936697a42f4203b608c2e5c9`.

Matching UIAutomator hierarchies are retained beside the reviewed screenshots
where the platform exposed their content. The widget binding and resumed-
activity assertions were taken from `dumpsys appwidget` and
`dumpsys activity activities`; they are device-state observations, not store
or signing claims.

## Remaining Android gate

The Android physical gate remains blocked. No current upload-signed phone or
Wear artifact exists, the current upload manifest remains `0/3` byte-verified
with all `physical_qa_evidence` fields null, and there is no byte-linked
upload-signed phone/tablet/widget matrix or paired physical Wear OS result.
This report is exact-current debug/API 25 physical regression evidence only and
must not be promoted to a release-candidate or public-store claim.
