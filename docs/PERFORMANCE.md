# Performance checkpoints

## Glass optimization — October 7, 2026

Product source `decc8510c2c554038525b76ee9f17c40a4b702d1` removes per-card backdrop recording, blur and lens processing over the smooth ambience. Cards retain translucent tint, a cached gradient edge, native shadow, clipping, selected/pressed feedback and the existing opaque accessibility fallback. No forecast, recommendation or persistence rules changed. Final local QA APK: `build/glass-optimization-2026-10-07/single-clip.apk`, SHA-256 `a03f0ca5a282336d74e7aeac3369bbdb1b40d670610d56c89e36d84eb99e39ec`; R8/resource-shrunk release, non-debuggable, `.physicalqa`, local debug certificate. This is not a distribution artifact.

### Controlled physical comparison

Same Samsung SM-S908E/Android16, 1440×3088/600dpi, min/peak refresh fixed to60Hz, brightness86/manual, animation scales1, RU/light/font0.9, Bukhara snapshot fetched09:22, provider network disabled during the pair. Android Studio mirroring remained on for both versions. CUA alternated0.2-page up/down movements in the same middle section (selected hour/outside/AQI), after40 warm actions. The position returned to its starting point without triggering pull-to-refresh. Each run collected120seconds; input pauses and frame counts are retained rather than normalized away.

| Matched method | Original `219dd53` | Direct glass, duplicate clip | Final, one clipping layer |
| --- | ---: | ---: | ---: |
| Duration | 120.83s | 120.05s | 120.75s |
| Valid frames | 2670 | 1769 | 2013 |
| Frame p50 | 33.39ms | 11.98ms | 11.90ms |
| Frame p95 | 41.87ms | 18.22ms | 17.53ms |
| Frame p99 | 46.04ms | 21.21ms | 20.60ms |
| Missed frame deadlines | 16.14% | 8.03% | 6.71% |
| Graphics memory after | 255.7MiB | 78.0MiB | 78.0MiB |
| Total PSS after | 329.0MiB | 130.5MiB | 128.9MiB |
| AP temperature, start→end | 32.6→41.2°C | 36.9→40.1°C | 39.4→37.8°C |
| Battery temperature, start→end | 30.4→31.1°C | 31.4→31.4°C | 31.4→31.7°C |
| Skin temperature, start→end | 30.8→32.9°C | 32.9→33.0°C | 32.7→33.2°C |

Thermal status stayed0 in all captures. The temperature ranges overlap, but starts were not temperature-identical. USB charging and mirrored CUA input limit interpretation; these are not unplugged-energy or unmirrored finger-input results. The final p95 improved58.1% and graphics memory about69.5%, but **the requested p95≤16.7ms and deadline misses≤5% target has not passed**. A short or favorable sample must not replace these results.

[scripts/profile_glass.py](../scripts/profile_glass.py) polls `dumpsys gfxinfo framestats` every0.75s, deduplicates IntendedVsync and excludes entries predating the reset. Frame time is `FrameCompleted−IntendedVsync`; misses use each frame's own `FrameDeadline`; percentiles use nearest rank. Nonzero Flags/invalid timestamps are excluded (final55 of2068 entries), never long valid frames. Raw samples, frame CSV, settings, thermal/display/memory captures and summaries are in `build/glass-optimization-2026-10-07/{baseline-fixed-01,direct-fixed-01,single-clip-fixed-01}`. Android histogram GPU overflow buckets at4950ms are not treated as actual multi-second GPU work.

### Attribution and limitations

Earlier120second mixed-scroll pilots produced original p95=43.23/45.72ms, no-lens37.53ms, no-lens/no-blur26.73ms. Those pilots included overscroll/refresh, so they establish effect-cost direction rather than final pure-scroll acceptance. Incomplete `baseline-fixed-range`/`baseline-fixed-final` collectors overlapped a screenshot dialog and are excluded.

The original130second Perfetto trace (`baseline.perfetto-trace`) contains2581 app FrameTimeline frames,177 explicit App Deadline Missed events (6.86%). Most other Late Present entries are Buffer Stuffing and are not counted as app deadline failures. RenderThread consumed18.878 CPU-seconds versus12.747 on the main thread;930 layer flushes averaged7.134ms,2582 Drawing slices averaged8.362ms, and736 recompositions averaged0.569ms. This supports removing per-card effect/layer work over the gradient. No ftrace overruns or frame-token errors were reported;28 unsupported vendor events and absence of GPU busy/call-stack tracks prevent a precise GPU-versus-CPU attribution. FrameTimeline and gfxinfo use different definitions and workloads here and must not be combined as one percentage. See [Perfetto FrameTimeline](https://github.com/google/perfetto/blob/main/docs/data-sources/frametimeline.md) and [Android dumpsys](https://developer.android.com/tools/dumpsys).


### Sustained background resource observation

The optimized QA process remained PID3511 throughout 61 samples from 10:02:56 to 11:06:04 local, with no activity launch after 09:57:57. The first four samples used ordinary `dumpsys meminfo`, which induces GC, and are labelled and excluded from the passive trend. The remaining 57 used `dumpsys meminfo --local`: PSS ranged 29,556–53,730KiB, repeatedly rising and falling, from 30,601KiB initially to 35,886KiB finally. There was no monotonic growth in this observation. Sampled app CPU was 0–0.5%; thermal status remained0 (AP30.0–37.6°C, battery28.3–30.4°C, skin28.7–30.6°C). Inspected logs contained no crash/ANR after the observation cutoff.

The natural 11:00 worker completed with background network traffic and a widget update request; [TESTING.md](TESTING.md#natural-background-observation-and-remaining-acceptance) distinguishes this from the still-unverified visible fresh timestamp. USB power, an active standby bucket, mirroring and concurrent Cooksy QA after10:41 prevent battery-life, Doze or isolated whole-device resource conclusions. This hour-long trace is a bounded stability observation. It does not prove absence of leaks over days. The read-only observer was stopped after capture; temporary refresh/brightness overrides and IDE mirroring were restored.

## Physical Samsung follow-up — October 7, 2026

Samsung Galaxy S22 Ultra SM-S908E, Android16/API36, 1440×3088/600dpi, adaptive refresh and animation scales1.0. The source-proven APK was built from `219dd5324dde095226d73825ed57e860ce135fd3` with release R8/resource shrinking, package suffix `.physicalqa`, and ordinary local Android debug-certificate signing. The installed package is **not debuggable**; it is not a distribution artifact. SHA-256: `c890d17b869dc384861a628da00867b143a250afa0a13b15d29afd5d7a0f8260`. Build receipt, raw diagnostics and screenshots are in `build/samsung-acceptance-2026-10-07`.

| Physical measurement | Result |
| --- | --- |
| Five cached cold launches through the home widget; background PID absence verified before each | 340 / 292 / 271 / 332 / 276 ms; median292 ms |
| Warm vertical scroll, normal glass, 102 frames | Jank29.41%; frame p50/p95 27/36 ms; GPU p50/p95 12/19 ms |
| Same eight CUA scroll actions, high-contrast text/opaque cards, 109 frames | Jank8.26%; frame p50/p95 10/18 ms; GPU p50/p95 5/10 ms |
| Normal glass restored, warmed repeat, 104 frames | Jank25.96%; frame p50/p95 27/36 ms; GPU p50/p95 13/19 ms |

Launch time is Android's `ActivityTaskManager Displayed` proxy, not first network content. These are current-build measurements without a matched earlier-revision baseline. Scroll samples use Android Studio mirroring and mouse-driven CUA input, with small frame counts and adaptive display timing; they do not certify continuous finger-driven60/120fps. The opaque setting changes text rendering as well as card effects. Nevertheless, the repeatable GPU difference is evidence that the glass path deserves optimization/profiling before premium-smoothness acceptance. `nimboGlass` applies backdrop blur, lens shader and shadow; high-contrast text bypasses that path. No speculative product change or visual-baseline replacement was made during this QA pass.

An early mixed-interaction sample was216frames/8.33%jank, p50/p95 8/34ms; a short horizontal sample was only33frames and is excluded from a smoothness claim. One memory snapshot was370230KiB PSS, including301812KiB graphics; this is a point sample, not evidence of a leak. At08:49 thermal status was0, AP34.5°C, battery31.6°C and skin32.2°C. Charging and mirroring were active. Battery percentage, power attribution and sustained unplugged consumption cannot be inferred from this session; package-filtered CPU/wakeup commands did not yield useful app-energy measurements.

The natural hourly worker ran at08:59:17 and returned `SUCCESS`, with the next run scheduled about60minutes later. The app had been backgrounded at08:58; no clock or job forcing was used. The08:06 snapshot was only53minutes old, so the documented60minute freshness gate legitimately republished cache without fetching. At09:00 the home widget advanced10→13°C and AQI31→30 while retaining the08:06 fetch timestamp. This establishes natural scheduling and cached time rollover, not a fresh network fetch, overnight idle reliability or battery life. See [TESTING.md](TESTING.md#physical-samsung-acceptance--october-7-2026) for the physical functional and accessibility scope.

## Simulator follow-up — October 7, 2026

The existing `ForecastPerformanceTest` passed 1/1 on API36 `NimboPhoneApi36`, 1080×2424/420dpi, with the host renderer (`Android Emulator OpenGL ES Translator`, Apple M3 Max; Skia OpenGL). Product source remains equivalent to `b845cfb`; HEAD during this check was `219dd53`. The fixed en-US/light/1× fixture and existing animation scales0 were retained. Raw evidence is `build/premium-quality/simulator-host-gpu-20261007`; command output is `build/simulator-acceptance-2026-10-07/performance-command.log`.

| Measurement | Result |
| --- | --- |
| First Compose render, one sample | 628 ms |
| Refresh rendering, five samples | 326 / 267 / 233 / 233 / 233 ms; median233 ms |
| Synthetic frames | 24 frames; p50/p90/p95 32/48/48 ms; 19 deadline misses |
| GPU percentiles | p50/p90 15/16 ms |

This changes the renderer from the earlier SwiftShader run and overlaps simulator/IDE activity. It is not a matched before/after comparison. The small debug instrumentation sample does not establish 60fps interaction, cold-start improvement, physical-device performance or battery life. No physical devices or distribution signing were used in this follow-up.

## Independent acceptance — October 7, 2026

Acceptance source `90ec87f` contains product fixes from `b845cfb` plus the city-scroll UI test correction. The ordinary Android runtime APK was built at `b845cfb` (SHA-256 `8e83a0a883817d66706338adb2b759be527277b2bd07b3d8c14c0e5c228c376d`); subsequent source changes are tests and release-evidence metadata. Raw current evidence is under `build/acceptance-2026-10-06` (directory date is UTC). These are **emulator debug baselines**, not physical-device or distribution measurements.

| Method and environment | Current result |
| --- | --- |
| Five cached cold activity launches, `am start -S -W`, API36 phone 1080×2424/420dpi, SwiftShader | 1315 / 962 / 1232 / 1204 / 1195 ms; median 1204 ms |
| Fixed-data matrix `ForecastPerformanceTest`, same phone, en-US/light/1×, epoch1725000000, animation scales0 | First Compose render819 ms; refresh588 / 418 / 383 / 333 / 634 ms, median418 ms |
| Same synthetic timeline sequence | 24 frames, p50/p90 69/97 ms, 22 deadline misses |
| Separate manual CUA selection/scroll/return-to-now/refresh, ordinary app | 54 frames, p50/p90 93/200 ms, 54 deadline misses |

Launch evidence is `emulator-cold-starts.txt`; ordinary interaction diagnostics are `emulator-interaction-gfxinfo.txt`; fixed fixture results are `final-matrix/phone-api36-performance-{render.json,frames.txt}`. Launch time excludes any claim about first meaningful network content. The manual sequence is not comparable to the synthetic test. GPU percentile buckets reaching4950ms in SwiftShader are not interpreted as physical GPU timings.

Compared with the October6 fixture sample, current refresh rendering is higher (median418 versus333ms), while initial composition is lower (819 versus1215ms) and frame p50 remains69ms. The host was concurrently running another project's device/build acceptance and several Apple simulators. There is no matched idle-host before sample, so these values establish neither an improvement percentage nor a causal regression. Inspection of the acceptance diff found no added refresh rendering work: the screen key changes only when the city changes, and the restored observer branch runs only after failed activation. The short software-renderer samples do not establish60fps smoothness. A controlled physical run remains necessary.

The connected Samsung SM-S908E/API36 was occupied by another QA session and later locked. Its existing `.debug` signature matched the local package, but no update, foreground takeover or new physical measurement was performed. The physical iPhone was unavailable. A paired iPad mini on26.7.1 had developer-built1.1.0(13), but launch timed out and Device Hub screen sharing requires27+. No usable libimobiledevice transport was present. Current-source physical launch/scroll/refresh, idle power and natural background activity therefore remain open; use a free unlocked test device and a source-proven compatible build. No battery-life claim is made from these simulator or historical short samples.


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
