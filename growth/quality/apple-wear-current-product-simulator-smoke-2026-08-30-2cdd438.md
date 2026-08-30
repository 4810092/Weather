# Exact-current Apple simulator and Wear OS emulator smoke — 2026-08-30 (`2cdd438`)

Status: **PASS FOR THE BOUNDED UNSIGNED/DEBUG SIMULATOR AND EMULATOR SCOPE;
SIGNED AND PHYSICAL GATES REMAIN BLOCKED**.

## Evidence authority

- Product source is
  `2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652`, built from clean detached
  checkouts.
- The private evidence bundles are
  `ios-simulator-2cdd438-2026-08-30`,
  `watch-simulator-2cdd438-2026-08-30`, and
  `wear-os-emulator-2cdd438-2026-08-30.cnxbN2`.
- Their `SHA256SUMS` files have SHA-256
  `4f26340c8db9e6a592e94aacf4099b5c9e8bb20dde993a4ff5d87da6494e7749`,
  `9c5053e38f1a4b47d1714190f83cb0dd806940c16cdac912039866b1cd5b8fdc`,
  and `390070364a149ffb4dda000990b7c21c85cc0d1e39d1790735d07ee3fce08cfa`
  respectively. Every retained file passed its bundle checksum manifest during
  report preparation.

## Artifact identity

- iPhone app executable SHA-256:
  `684cecd53db3b0e9e35eecfc14ebf5ffae9727a883bbfe5109b91949684d578c`;
  embedded widget executable SHA-256:
  `ef5ef71fbf0c834f94480cec00b49ee74574c98575a821252214f7b20d5ad367`.
- Watch executable SHA-256:
  `828feef2e33cacc072c5dd6cec219bc1f63477233c8d187bb8cf7f3f4f803606`;
  binary/dSYM UUID: `C1775BF3-D12B-3A60-BBB9-4CBAC9ADF6F4`.
- Wear debug APK SHA-256:
  `b1f20aa60117c36f5e041777c775dbebabc820f726141bd739a581ef55f35f58`;
  unsigned provenance AAB SHA-256:
  `ad2f1041fae3bc298e31dc09abf5b173142efd88a91382fa3b37b082cc698205`.
  Installed APK bytes matched the retained debug APK exactly.

## Bounded results

| Surface | Exact-current result | Data provenance and boundary |
| --- | --- | --- |
| iPhone Simulator | The unsigned Release iPhone Simulator app and embedded widget carry the full source revision. On iPhone 16 Pro Max / iOS 18.1, EN/RU/UZ each passed `1/1` from reinstall through the real Tashkent quick-city and live-provider flow. Each locale retained 408 hourly, 17 daily, 120 AQI, and 48 snapshot rows; twelve 1320×2868 screenshots were inspected. The app completed `40/40` cold launch/terminate cycles with unique PIDs, zero product-scoped fatal matches, and no new Nimbo crash report. | This is live-provider phone regression and localized-pixel provenance only. Signing was disabled. It does not prove home-screen widget placement, offline behavior, older iOS runtime, a physical iPhone/iPad, TestFlight, review, or availability. |
| watchOS Simulator | The unsigned Release `NimboWatch` build `1.1.0 (6)` carries the full source revision. EN/RU/UZ stale-state rendering was inspected at 416×496; `30/30` cold cycles used unique PIDs with zero fatal-pattern matches and no new Nimbo crash report. | This was **not** a live provider response or fresh phone-to-watch transfer. The unpaired simulator rendered a retained ten-key `UserDefaults.standard` snapshot matching the debug preview-like fixture (`Tashkent`, 24 C, 27/18 C, rain 10%, AQI 42; updated 2026-08-12). Two `com.apple.wcd` nil-context messages per launch are retained as unpaired-environment noise. |
| Wear OS emulator | Exact-source `:wearApp:testDebugUnitTest`, `assembleDebug`, and provenance-only `bundleRelease` passed for debug APK `1.1.0 (1000008)`. EN/RU/UZ fit the 480×480 Wear OS 7 / API 37 round surface. Locale launches and the additional restored-English `10/10` cold loop resumed Nimbo with zero PID-scoped fatal matches. | App-data clear was followed by normal Wear Data Layer rehydration of a cached stale `Mountain View` snapshot (25 C, 25/15 C, rain 0%, AQI 58; updated 2026-08-12). There was no database seed, demo extra, or fresh paired refresh. The retained release AAB is unsigned provenance only, not an upload candidate. |

The Wear AVD was stopped with logical locale, app-locale, font-scale, and
accessibility state restored. Its evidence records the production-image
limitation that materialized raw `persist.sys.locale=en-US` while preserving
the same logical `en-US` locale.

## Gate effect

This replaces predecessor-only freshness uncertainty for these three bounded
simulator/emulator surfaces. It does **not** close source-synced upload signing,
release-certificate physical QA, physical iPhone/iPad/Apple Watch/Wear OS,
fresh paired-watch transfer, TestFlight/Play delivery, review, rollout, or
public-availability gates. The upload manifest, operational gates, and growth
dashboard remain unchanged and fail closed.
