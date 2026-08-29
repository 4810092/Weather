# iOS 15 WidgetKit compatibility — 2026-08-29

Status: **PASS for exact-source compilation, binary minimum version, and
available-simulator host integration; NOT RUN on iOS 15/16 runtimes**.

No archive, signed artifact, device install, TestFlight build, store change, or
public release was created by this check. Crash, signing, physical-device,
provider, and publication gates remain blocked or pending.

## Exact product source

The compatibility implementation is commit
`fc07dd1c26dd11c97d7d66c142ea33a962a1718c`.

- The app and WidgetKit extension both declare iOS `15.0`.
- iOS 15 advertises only `.systemSmall` and `.systemMedium`.
- Accessory families are rendered and registered only inside iOS 16 availability
  checks.
- iOS 17 and later use `containerBackground(for: .widget)`; iOS 15–16 use the
  ordinary color background fallback.
- The current Xcode SDK declares accessory families from iOS 16 and
  `containerBackground` from iOS 17. The source guards follow those declarations
  rather than suppressing compiler availability diagnostics.

The generated Xcode project contains four iOS `15.0` deployment settings: two
project configurations and two WidgetKit target configurations. Repository and
growth-test contracts reject a return to the iOS 17 widget floor or removal of
either availability boundary.

## Exact-source unsigned products

Xcode 26.6 built Release simulator products with signing disabled. UUID output
matched each executable to its generated dSYM.

| Product | Version | Minimum | SHA-256 | UUID |
| --- | --- | --- | --- | --- |
| iOS simulator host | `1.1.0 (6)` | iOS 15.0 | `aba01bcec2552c941983dc053b56c6fd71363777ffd6c41b2bab80a532d29e6e` | `1CFADB06-1771-30AA-9701-D75A50E1E1F2` |
| Embedded WidgetKit extension | `1.1.0 (6)` | iOS 15.0 | `83e1603c5ae4100ca7cd95d3271b0f1ec45bdc98702121867da7c9522c4aa8f4` | `ECF030BD-A813-3B1D-9279-609235F0FE08` |
| watchOS simulator companion | `1.1.0 (6)` | watchOS 10.0 | `c0794ae92a8666d3e5f01387dd333261a7b2f22250dbacf0f711491ee4fe59b5` | `46BE5FC6-9FED-3452-A01B-B1D3544A6662` |

`vtool` independently reported `platform IOSSIMULATOR`, `minos 15.0`, and SDK
26.5 for both the host and embedded widget. The iOS link retained the already
documented warning for the data-only Skiko ICU object marked simulator 18.5;
the final host and widget load commands remain 15.0. This is not treated as an
iOS 15 runtime pass.

## Available-runtime integration smoke

The exact host bundle was installed on newly created, empty simulators and then
launched, allowed to run for four seconds, and terminated normally:

| Runtime | Device | Launch result | Installed-byte check |
| --- | --- | --- | --- |
| iOS 18.1 | iPhone SE (3rd generation) | PID returned; terminate succeeded | Host and embedded widget SHA-256 matched the build products |
| iOS 26.5 | iPhone 17 | PID returned; terminate succeeded | Host and embedded widget SHA-256 matched the build products |

The installed bundles contained the executable WidgetKit extension. The bounded
host DiagnosticReports lookup produced no matching Nimbo report. Both temporary
simulators were deleted after the check.

This smoke proves containing-app installation, launch, and embedded-extension
byte identity on available runtimes. It does **not** prove widget gallery
registration or rendering, snapshot refresh, localization, accessibility, or
behavior on the unavailable iOS 15/16/17 runtimes.

## Verification commands

The relevant checks were:

```sh
python3 -m unittest discover -s scripts/growth/tests
python3 scripts/check_repository.py
python3 scripts/check_release_qa_matrix.py
python3 scripts/check_localizations.py
python3 scripts/check_store_metadata.py
./gradlew :shared:iosSimulatorArm64Test

xcodebuild -project iosApp/Nimbo.xcodeproj -scheme NimboSimulator \
  -configuration Release -sdk iphonesimulator \
  -destination 'generic/platform=iOS Simulator' \
  CODE_SIGNING_ALLOWED=NO ARCHS=arm64 ONLY_ACTIVE_ARCH=YES build

xcodebuild -project iosApp/Nimbo.xcodeproj -scheme NimboWatch \
  -configuration Release -sdk watchsimulator \
  -destination 'generic/platform=watchOS Simulator' \
  CODE_SIGNING_ALLOWED=NO ARCHS=arm64 ONLY_ACTIVE_ARCH=YES build
```

The local result was 126 passing growth tests, a passing repository contract,
passing release-QA/localization/store-metadata checks, passing shared iOS tests,
and successful iOS/widget/watch Release builds.

## Remaining release boundary

An actual iOS 15 runtime must render small and medium widgets; iOS 16 must render
the accessory families; iOS 17 or later must exercise removable container
background behavior. The exact build must then be distribution-signed and pass
the required physical iPhone/iPad/widget matrix. Until that evidence exists,
the compatibility change cannot close the iOS crash, signing, physical QA,
review, rollout, or public-availability gates.
