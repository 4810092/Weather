# Apple Watch RU/UZ simulator capture — 2026-08-29

Status: **HISTORICAL BUILD-5 LOCAL SIMULATOR CAPTURE PASSED; NOT BUILD-6,
PHYSICAL-DEVICE, OR STORE-UPLOAD EVIDENCE**.

## Exact runtime and build

- Active pair: Apple Watch Series 11 (46 mm), watchOS 26.5,
  `8485D31E-BAAD-4BDE-B5DD-7BBE000C2CFE`, paired with iPhone 17, iOS 26.5,
  `95DD015B-B4DC-4B20-AECD-1A7FC391E81B`.
- Installed product: `uz.ganikhodjaev.weather.watchkitapp`, version
  `1.1.0 (5)`, `watchsimulator26.5`, minimum watchOS 10.0, companion bundle
  `uz.ganikhodjaev.weather`.
- Current Apple source identity is `1.1.0 (6)`. This capture predates that
  source-sync correction and cannot satisfy build-6 signing or physical QA.
- The installed arm64 simulator executable SHA-256 is
  `b88b89bfbb5c43891732b0b46cc7ab1068c50bda4dc346581c12d53f1d4151fa`,
  exactly matching the executable in the local
  `Release-watchsimulator/NimboWatch.app` input bundle.
- The source checkout was at
  `584f47a83637ce3587ce980a69f392b84a57656b`; no Watch source, shared Watch
  localization, project, or version-setting path changed between the original
  `d593263` 1.1.0 build checkpoint and that checkout.

The simulator product was produced without distribution signing. Its Mach-O
contains an ad-hoc signature, while the bundle has no resource signature
envelope; therefore a strict local bundle `codesign --verify` reports the
missing resource envelope. CoreSimulator nevertheless installed it
successfully, and the installed executable hash matches the input exactly.
This boundary applies only to the unsigned simulator product and does not
replace the separately retained distribution-IPA signature evidence.

## Locale and data provenance

The Watch view localizes `Rain`, `High`, `Low`, and its empty-state instruction
through `String(localized:)`. Captures launched the same installed bundle with
process-scoped locale arguments:

```sh
xcrun simctl launch --terminate-running-process "$WATCH" \
  uz.ganikhodjaev.weather.watchkitapp \
  -AppleLanguages '(ru)' -AppleLocale ru_RU

xcrun simctl launch --terminate-running-process "$WATCH" \
  uz.ganikhodjaev.weather.watchkitapp \
  -AppleLanguages '(uz)' -AppleLocale uz_UZ
```

The rendered weather values were not injected or invented for the screenshots.
The app read an existing, retained simulator `UserDefaults.standard` snapshot,
which the Watch code ordinarily receives through `WCSession` application
context and persists locally. The bounded snapshot contains only:

- location label `Tashkent`;
- 27 °C, daily high 40 °C, daily low 25 °C;
- clear weather code, 0% rain, AQI 63;
- update epoch `1786571654` (`2026-08-13 02:54:14 +0500`).

The retained snapshot is stale and must not be presented as current weather.
It is suitable only as deterministic, previously received simulator data for
showing the real UI. No coordinates, device/user identifier, account data, or
other PII is rendered or recorded in the assets. The location remains
`Tashkent` in both captures because it is payload data, not a localized static
string.

## Final assets

| Locale | Visible localized evidence | Dimensions | SHA-256 |
|---|---|---|---|
| Russian | `Осадки 0%` | 416×496 PNG | `befd7d7939f8b6315e117a0f03a36cbea1041fdc2a15cac15e2d41d7fab1ce76` |
| Uzbek | `Yog‘in 0%` | 416×496 PNG | `b4ae83a6062d515db9074ba4725bf218b719bf96366cd17a2e79514d4a448baa` |

Paths:

- `store/screenshots/app-store/apple-watch-ru-RU/01-current.png`
- `store/screenshots/app-store/apple-watch-uz-UZ/01-current.png`

Both final PNGs were flattened from opaque RGBA to 24-bit RGB with zero visible
pixel differences, decode as 416×496 RGB PNGs, and were inspected individually
at original resolution. They show the active application state with the location,
temperature, daily range, weather symbol, localized rain label, and AQI visible
without clipping. Intermediate frames captured while the simulated watch
display was transitioning or dimmed were rejected; only the complete active
frames above were retained.

The current creative manifest and asset validator register both localized
Apple Watch paths and their RU/UZ Wear OS counterparts. Validation confirms
file provenance, dimensions, and creative use; it does not upgrade historical
build-5 simulator frames into build-6 or physical-watch QA.

## Reproduction commands

```sh
xcrun simctl list pairs
xcrun simctl install "$WATCH" "$WATCH_APP"
xcrun simctl appinfo "$WATCH" uz.ganikhodjaev.weather.watchkitapp
xcrun simctl get_app_container "$WATCH" \
  uz.ganikhodjaev.weather.watchkitapp app
xcrun simctl launch --terminate-running-process "$WATCH" \
  uz.ganikhodjaev.weather.watchkitapp \
  -AppleLanguages '(ru)' -AppleLocale ru_RU
xcrun simctl io "$WATCH" screenshot \
  store/screenshots/app-store/apple-watch-ru-RU/01-current.png
xcrun simctl launch --terminate-running-process "$WATCH" \
  uz.ganikhodjaev.weather.watchkitapp \
  -AppleLanguages '(uz)' -AppleLocale uz_UZ
xcrun simctl io "$WATCH" screenshot \
  store/screenshots/app-store/apple-watch-uz-UZ/01-current.png
```

## Boundary

No physical Apple Watch was used. No store metadata, App Store Connect record,
TestFlight build, review state, or production release was changed. These PNGs
prove only the exact local Watch simulator bundle's RU/UZ rendering with a
retained non-PII snapshot; they do not prove physical-device behavior, current
weather accuracy, current build-6 behavior, App Store asset acceptance,
upload, or public availability.
