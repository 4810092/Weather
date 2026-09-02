# Android phone vc11 physical smoke — 2026-09-02

Status: **PASS for the bounded exact-current upload-signed API 25 phone and
widget scope**. The complete Android release gate remains blocked because this
was not a Google Play-delivered install and no current physical tablet, paired
Wear OS vc1000011, or conclusive post-delivery UZ Vitals result exists.

All times are `Asia/Tashkent` (`UTC+05:00`). The run binds its result to product
authority `052d12c7dfa6411428d85205d9568462d20ff87d` and exact phone AAB
`nimbo-phone-1.1.0-vc11.aab`, SHA-256
`034aa0a732e0a671c341e6714162a2d22c95d06435aa327bd17b1d7b3da2f9ac`.

## Artifact and install identity

- The AAB was recovered from unpublished draft release `381212810`, whose
  package and receipt hashes were rechecked before use. No release was
  published and no Play track was changed.
- Pinned Bundletool `1.18.3`, SHA-256
  `a099cfa1543f55593bc2ed16a70a7c67fe54b1747bb7301f37fdfd6d91028e29`,
  generated one universal APK. Keystore and key passwords were read from the
  existing macOS Keychain and passed through mode-600 named FIFOs; they were
  never placed in argv, an ordinary file, Git, or command output.
- Generated APKS SHA-256:
  `f76278227c8faaaca5bb146983e36c209862b2cd870d58b1e3c419df3e3a8a75`.
- Universal APK SHA-256:
  `16491370bee480e500be2660880729b79867d30658ed9261fe923d0cdf80f9c5`.
  The pulled installed `base.apk` had the same hash byte-for-byte.
- `apksigner` verified v2/v3 signing and upload-certificate SHA-256
  `431548a4871c9c090eee808ac3a34898f5d78602d9e747dfe81e228415aac252`.
- Package identity was `uz.ganikhodjaev.weather`, `1.1.0 (11)`, min/target SDK
  `24/36`.
- Target was the dedicated General Mobile 4G Dual `e76fd426`, physical Android
  7.1.1 / API 25. The separate Samsung API-36 device containing user data was
  not modified.

The target initially contained a Play-delivered vc10 split install. Because the
Google Play delivery signer differs from the upload signer, only Nimbo was
uninstalled from this dedicated QA phone before the clean vc11 install. This
run does not claim that the prior Play state was restored.

## Bounded physical result

| Scenario | Result |
| --- | --- |
| Clean install and cold launch | PASS; Package Manager reported vc11 and the pulled installed APK matched the generated universal APK byte-for-byte |
| Localized onboarding | PASS; Russian onboarding rendered the value proposition, Uzbekistan quick cities, ordinary search, and optional approximate-location path |
| Live provider path | PASS; selecting Tashkent rendered current temperature, conditions, feels-like, yesterday comparison, future context, and Best Time content from the existing Open-Meteo scope |
| Native Share | PASS; the localized Share action opened Android's native resolver titled `Поделиться с помощью:`; no destination was selected and the Nimbo PID remained alive |
| Manual refresh | PASS; refresh returned to the populated Tashkent forecast without a saved-weather or update error |
| Home-screen widget | PASS; Google Now Launcher exposed `Nimbo 3 x 2`; widget id `5` bound to `WeatherWidgetProvider` and rendered Tashkent, `24°C`, high/low, precipitation, and AQI |
| Widget tap | PASS; tapping the populated widget resumed `uz.ganikhodjaev.weather/.MainActivity` with the populated Tashkent forecast |
| Process health | PASS within the exercised paths; bounded log filters contained zero Nimbo fatal exception, ANR, process death, SSL handshake, CertPath, or trust-anchor match |
| Cleanup | PASS; the QA install was removed, package and widget/provider references disappeared, no global proxy was configured, and Wi-Fi remained enabled |

An unrelated system dialog reported that the old Google Play app had crashed
immediately after the first launch. It was dismissed without changing Google
Play, and the logs and process checks showed Nimbo had started and remained
healthy. It is not counted as a Nimbo failure or as Play-delivery evidence.

## Selected evidence

- [Native Android Share chooser](evidence/android-phone-vc11-physical-2026-09-02/share-chooser.png)
  — SHA-256
  `1abc0f0c85031478c30419a137087e40c51888fe06cd4dffec9f8d78ea35666c`.
- [Populated physical API 25 widget](evidence/android-phone-vc11-physical-2026-09-02/widget.png)
  — SHA-256
  `25d377138e238421e84a598836bdbfed2d561e503d74821b79a40e4b7fded0f7`.
- [Forecast after widget tap](evidence/android-phone-vc11-physical-2026-09-02/widget-tap.png)
  — SHA-256
  `c6d537955d8cf32d22d06d0da3d3e1ca2c0bb34cff5c6a1962f50ceb9a882c31`.

The reviewed screenshots contain no account, notification, location-coordinate,
or message content. UIAutomator and `dumpsys` observations were retained only in
the temporary bounded QA workspace and were not promoted as store evidence.

## Remaining gate boundary

This proves an exact-current upload-signed clean install and bounded phone/share/
refresh/widget runtime path on one physical API-25 device. It does **not** prove
Google Play delivery, an update over a current Play-signed install, a physical
tablet, rotation/large-text/TalkBack coverage on vc11, paired Wear OS vc1000011,
post-delivery Android Vitals, production rollout, public availability, or rank.
Those missing requirements keep `android_physical_smoke` blocked.
