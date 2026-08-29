# Android current-product tablet/widget smoke — 2026-08-29

Status: **PASS for the bounded debug/API 36 emulator scope**.

The run was performed at `2026-08-29 23:28–23:33 +05:00` with the same
exact-current debug APK used for the physical API 25 phone smoke. It closes the
stale-product-source gap for tablet layout and the Android home-screen widget,
but it is not upload-signing, Play delivery, physical-tablet, Wear OS, review,
rollout, accessibility-declaration, or public-availability evidence.

## Identity and source boundary

- Product source: `9c2dce4200dbba5487c8c458ade4616005fde6e6`.
- Package/version: `uz.ganikhodjaev.weather`, `1.1.0 (8)`, min/target SDK
  `24/36`.
- Local APK and pulled installed `base.apk` SHA-256:
  `52146b883a04e4c2d272ea4e3ecc9b1277a8c78c117b547a121de3a7d90c3730`.
  This is the byte-identical debug artifact already bounded to the clean
  current-product checkout in
  `android-current-product-physical-smoke-2026-08-29.md`; it was not rebuilt or
  relabelled as an upload candidate for this run.
- Device: fresh full-boot `Cooksy_Pixel_Tablet_API_36` AVD, Android API 36,
  `sdk_gphone64_arm64`, 2560 x 1600 at 320 dpi, 4 GB RAM, SwiftShader, no
  snapshot load/save, Uzbek per-app locale. The package was absent before the
  run.
- The dedicated API 36 emulator ran on port `5556`. The existing API 24
  emulator and both attached physical phones were not changed.

## Exercised paths

| Scenario | Result |
| --- | --- |
| Clean install and Uzbek tablet onboarding | PASS; the value-first screen, seven Uzbekistan quick cities, ordinary search, optional approximate-location path, and disclosure rendered without clipping in landscape |
| Tashkent without location permission | PASS; selecting the quick city rendered fresh Open-Meteo conditions without granting location access |
| Forecast value and context | PASS; current/apparent temperature, yesterday comparison, upcoming change, the 48-hour timeline, air quality, and 10-day forecast rendered |
| Best Time Outside boundary | PASS; the initial late-day state truthfully reported insufficient suitable hours; a later fresh forecast rendered the `00:00–02:00` recommendation with localized reasons |
| First-forecast tip | PASS; the contextual tip appeared after the successful forecast, `Tushunarli` removed it, and it stayed suppressed on restart |
| Android home-screen widget | PASS; `WeatherWidgetProvider` was discoverable, widget id `5` rendered Tashkent, `27°C`, high/low, precipitation, and AQI in Uzbek, and tapping it opened `MainActivity` |
| Large text and rotation | PASS; at `font_scale=1.3`, the live view remained readable without overlap in landscape and portrait; Best Time, timeline, hourly detail, AQI, and 10-day content remained reachable |
| Process health | PASS within the exercised paths; the complete captured log contained zero Nimbo fatal exception, ANR, SSL handshake, CertPath, or trust-anchor matches |
| Cleanup | PASS; Nimbo was uninstalled, its widget/provider state disappeared, font scale returned to `1.0`, auto-rotation and natural orientation were restored, all three animation scales returned to `1`, and the no-snapshot emulator exited normally |

## Selected evidence

- [Uzbek tablet onboarding](evidence/android-current-product-tablet-widget-2026-08-29/onboarding-landscape.png)
  — SHA-256
  `044a7a02b6279732360d0b4f873ea09bf3dfca2ca8562907008af0cc54549c2e`.
- [Live landscape forecast and first-tip state](evidence/android-current-product-tablet-widget-2026-08-29/live-landscape.png)
  — SHA-256
  `020239a011fc51d39ff37b841f34f4798e453958cf135ab3a189489a362f9214`.
- [Uzbek Android widget](evidence/android-current-product-tablet-widget-2026-08-29/widget-landscape.png)
  — SHA-256
  `417e4a8ab0972a16327e365a1b3cdd97e37d88bc87fa7341562760e873023505`.
- [Large-text landscape forecast](evidence/android-current-product-tablet-widget-2026-08-29/large-text-landscape.png)
  — SHA-256
  `e33aad1004b31372ca2584308cf388487784cb5f10c45e98582a30ec42e5612d`.
- [Large-text portrait forecast](evidence/android-current-product-tablet-widget-2026-08-29/large-text-portrait.png)
  — SHA-256
  `74b7e0c29284214bf1108ec51cb5df7eb062a7de1db50c7999365de256960186`.

Matching UIAutomator hierarchies are retained beside the five visually
reviewed, non-PII PNGs.

## Remaining Android gate

The Android physical release gate remains blocked. The exact-current phone and
Wear AABs are unsigned, this tablet/widget result used the debug certificate on
an emulator, and there is still no upload-signed physical phone/tablet/widget
rerun or paired physical Wear OS result. This report is exact-current
regression evidence only and is not promoted to a release or store claim.
