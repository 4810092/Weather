# Wear OS localized store capture — 2026-08-29

Status: **PASS for emulator screenshot provenance only**. This is not a
physical-watch, paired-phone, Data Layer, store-upload, or production-rollout
pass.

## Capture identity

- Time: `2026-08-29 01:00 +05:00`.
- AVD: `Wear_OS_XL_Round`, Wear OS 7.0 / API 37, ARM64, physical framebuffer
  `480 x 480` at 320 dpi.
- Installed artifact: retained signed universal Wear APK
  `nimbo-wear-1.1.0-vc1000008-universal.apk`.
- APK SHA-256:
  `88445c1ea472ec7677499fb8bb7f93e081cf540171ba7a7bbd8e1e6c826696bf`.
- Package identity: `uz.ganikhodjaev.weather`, version `1.1.0 (1000008)`,
  min SDK 30, target SDK 36.
- Signer SHA-256:
  `431548a4871c9c090eee808ac3a34898f5d78602d9e747dfe81e228415aac252`.
- The emulator reported zero configured accounts. Device locale remained
  `en-US`; only the installed app locale was changed for each capture.

## Procedure and verified UI

The APK was clean-installed and launched through the exported production
`WearWeatherActivity`. Its existing `demo` intent path populated deterministic,
non-personal test weather for Tashkent: 27 C, daily range 31/19 C, rain 10%,
and AQI 42. No UI was generated or retouched. UI Automator confirmed the
following localized production text before each screenshot:

- `ru-RU`: `Ташкент`, `27°C`, `↑31° ↓19°`, `Осадки 10% · AQI 42`.
- `uz-UZ`: `Toshkent`, `27°C`, `↑31° ↓19°`, `Yog‘in 10% · AQI 42`.

Both screenshots were captured from the 480 x 480 framebuffer, converted only
from opaque RGBA to 24-bit RGB PNG with zero pixel differences, and inspected
visually. Filtered logcat contained no Nimbo fatal exception or ANR.

## Outputs

- `store/screenshots/google-play/wear-os-ru-RU/01-current.png` — 480 x 480,
  opaque RGB PNG, SHA-256
  `60944c367cfdf41c47226cf3f60dfa8b918827a4674e33db531abb67a03cfc47`.
- `store/screenshots/google-play/wear-os-uz-UZ/01-current.png` — 480 x 480,
  opaque RGB PNG, SHA-256
  `76d79459e88830f2f39000fda34ca1ddd15877eba29bd143fe7a1a07c80c714c`.

The app locale was cleared, the package was removed from the emulator, and the
headless AVD was stopped after capture.
