# Performance checkpoints


## Premium UI comparison — October 6, 2026

The fixed-clock `ForecastPerformanceTest` uses the same 49-hour data, en-US, 1× text, light theme, debug test package and API36 arm64 phone AVD (1080×2424, 420dpi, SwiftShader, animation scales zero) before and after the UI changes. Raw data is in `build/premium-quality/{before,after}`. These are local rendering proxies, not release/device benchmarks or provider-latency measurements.

| Same-scenario measurement | Before | After |
| --- | --- | --- |
| First Compose render (one sample) | 1195 ms | 1215 ms |
| Refresh state → usable UI, median of 5 | 366 ms | 333 ms |
| Synthetic scroll frames | 25 | 25 |
| Frame p50 / p90 | 77 / 97 ms | 69 / 89 ms |

The 1.7% first-render difference is too small to establish a regression from one sample. Refresh rendering improved 9%; frame percentiles improved, but the software renderer still misses most frame deadlines (84% before, 96% after). Eight virtual-time test gestures generate only 25 real frames, so neither the deadline fraction nor these samples establishes smooth 60fps interaction. A separate real-time ADB gesture diagnostic of the current debug app produced 103 frames, p50/p90 77/125ms on SwiftShader; software GPU draw commands dominated. It is deliberately not compared to the synthetic sequence.

The first cold-start baseline accidentally used an older preinstalled release package, whereas the after sample used the current debug package. They are not comparable and are excluded from the before/after conclusion. Current debug cold activity launch was 762–1071ms, median 829ms; it is an `am start -W` proxy, not first meaningful forecast. A future release-device benchmark must capture both revisions with matched build and cache states.

An isolated test package also ran on a physical Samsung SM-S908E / Android16, 1440×3088 at 600dpi, existing animator scale 1.0. No device preferences or personal app data changed. First Compose render 886ms, refresh median 350ms, synthetic scroll 30 frames p50/p90 65/133ms. The physical renderer’s GPU p50/p90 was 6/9ms. This is a debug instrumentation sample without a physical before baseline; it does not validate distribution-build frame pacing, battery drain, background scheduling, or screen-reader speech.

Reproduce fixed-data measurements with `ANDROID_SERIAL=<test-device> scripts/measure_forecast_rendering.sh <label>`. Keep the same device, build type, animation/thermal state and cache; the script records environment and never changes device settings.

## Historical checkpoint — August 10, 2026

Measured on 2026-08-10. These numbers are engineering evidence, not device-wide product claims.

## Android

Environment: arm64 API 36 `Nimbo_API_36` emulator, 1080×2400 at 420 dpi, running on an Apple M3 Max host. The APK was the R8- and resource-shrunk `release` output, locally signed with the Android debug certificate only for installation. It is not a store artifact.

| Measurement | Result |
| --- | --- |
| Shrunk APK size | 1.7 MiB |
| Cached cold activity start, 5 runs | 149–243 ms; median 218 ms |
| Warm task foreground, 5 runs | 14–104 ms wait; median 22 ms |
| First meaningful network UI after location tap | 6,178 ms conservative bound |
| Process memory after cached render | 41 MiB total PSS; 143 MiB total RSS |
| Timeline scripted scroll | 153 frames; p50 17 ms, p90 18 ms, p99 19 ms |
| Scroll frame diagnostics | 10 deadline misses (6.54%); 0 missed-vsync; 0 slow-UI-thread frames |

The network figure starts immediately before the location action and ends when UIAutomator first observes a semantic hourly weather button. It includes polling overhead, location lookup, provider latency, persistence, and rendering, so it is deliberately a conservative upper bound. Cached launch uses `am start -W`; it is a launch proxy rather than a frame-timeline measurement.

The release database captured after normal use was 224 KiB with 648 weather rows and 351 forecast snapshots. SQLite used the primary-key index for the timeline range query (`location_id`, `epoch_seconds`) rather than a table scan. Retention still enforces the documented weather and snapshot windows.

The scroll run used synthetic input, which reported high input latency from the injection mechanism. Rendering itself showed no slow UI-thread frames or missed vsync. A physical-device Macrobenchmark would be more representative. An app-specific Baseline Profile module was not added at this checkpoint: the measured cached launch is already small, while the repository has no stable physical/managed-device performance runner. The release APK does include dependency-provided ART profile metadata.

## iOS

Debug simulator builds were exercised on iPhone 16 Pro and iPad Pro 11-inch (M4), iOS 18.1. Host RSS after the cached main screen stabilized was about 185 MiB on iPhone and 157 MiB on iPad. `simctl launch` returned in 0.20–0.68 seconds, but that command does not measure first frame and is recorded only as a diagnostic.

Timeline interaction, rotation, Dynamic Type at `accessibility-extra-large`, and Increase Contrast remained responsive in manual simulator passes. No network or database work was observed blocking interaction after the cached screen appeared. Instruments measurements on a distribution-signed physical build remain part of TestFlight QA.

## Architecture protections

- Cached state is read from SQLDelight before refresh.
- Primary current/hourly data is committed before history enrichment starts.
- Seven-day history and insight computations are secondary work and do not gate the first meaningful weather screen.
- The timeline uses lazy visible drawing from regular Compose nodes and has no continuously running animation.
- R8, resource shrinking, and release lint run in the release gate.
