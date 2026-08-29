# Apple localized current-product capture — 2026-08-29

Status: **PASS for App Store screenshot provenance only**.

This record does not satisfy Apple signing, physical-device, crash,
TestFlight, review, rollout, or public-availability gates. It proves that the
three UZ-growth phone sources are localized pixels from the exact current
product simulator build and that the rendered creative set remains based on
real application UI.

## Exact build and environment

- Product source:
  `9342824db7c0dcadfc4bdfe11f580377c108d968`.
- Release simulator app: `NimboSimulator` `1.1.0 (6)`, bundle
  `uz.ganikhodjaev.weather`, minimum iOS `15.0`.
- Executable SHA-256:
  `0db3db757a7c0c497f7712c565a9b40e71edf271505cf0d0887c0ff3d59c0a76`.
- Runtime: iPhone 16 Pro Max, iOS 18.1, 1320 x 2868 framebuffer.

The simulator container was seeded only with the product's checked-in Tashkent
quick-city identity and exact coordinates (`quick:uz:tashkent`, 41.2995,
69.2401, `Asia/Tashkent`). Nimbo then fetched the forecast from the normal live
provider path. The database contained 408 weather-hour, 17 daily-forecast, and
120 air-quality rows for that exact location before capture. No weather value,
condition, recommendation, or UI pixel was invented or retouched.

The location label was changed between launches only to the product's English,
Russian, and Uzbek localized Tashkent/Uzbekistan names. The app was launched
with the corresponding Apple language and UZ locale. The first-forecast tip is
visible because it is a real current `1.1.0` product state.

## Versioned phone sources

| Locale | Source | SHA-256 |
| --- | --- | --- |
| English | [`iphone-6.9-en/01-current.png`](../../store/screenshots/app-store/iphone-6.9-en/01-current.png) | `6c8af5018c298a1238e0c93a10d6ef818c90c60dffcdf2db02dbeedf9c4b39ab` |
| Russian | [`iphone-6.9-ru-RU/01-current.png`](../../store/screenshots/app-store/iphone-6.9-ru-RU/01-current.png) | `79fe25419364a76c75d452d328a86e2b7b2a3e8afb72025b2bc1fc95341afd73` |
| Uzbek | [`iphone-6.9-uz-UZ/01-current.png`](../../store/screenshots/app-store/iphone-6.9-uz-UZ/01-current.png) | `8150e5ccdb71d1bd2c2044d88beb96395206c7a2bdecbaed09ffaa8d6792ac61` |

The raw simulator screenshots were converted losslessly from opaque RGBA to
RGB PNG so they satisfy the store alpha policy; dimensions and visible pixels
were preserved.

## Creative-set contract

The first five App Store stories now use distinct source/focus compositions:
full Best Time, upper comparison, a timeline-visible lower focus, nearly full
details, and the nearly full privacy composition. The renderer still only
crops, scales, frames, and captions these versioned production pixels. A
repository validator now fails if the first five stories collapse back to the
same source/focus pair or if either platform declares an out-of-domain focus.

This is an honest improvement over the previous pack, where stories one
through five reused the exact same framing. It does not claim a conversion lift
or replace the future goal of capturing dedicated scrolled iOS states for
10-day/AQI and offline cache.

The temporary simulator app was terminated, uninstalled, and the simulator was
shut down after the source files were verified.
