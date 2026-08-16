# Quality strategy

Nimbo’s quality evidence has four layers: deterministic shared tests, actual SQLite migration/retention host tests, cross-platform build gates, and dated manual release QA. A claim belongs in the narrowest layer that proves it.

## Automated pull-request gates

- Repository policy and simple secret-pattern checks for tracked files.
- Local Markdown-link validation.
- Complete resource/type/placeholder parity for 13 app languages and all widget/watch/permission surfaces.
- Store metadata limits and 63 expected production-image dimensions/formats.
- ktlint for Kotlin and Gradle Kotlin scripts.
- 30 unique automated test functions: 28 common and two Android-host persistence/migration tests.
- SQLDelight numbered-migration/schema verification plus a released-v1 SQLite fixture migration.
- R8/resource-shrunk Android phone/tablet and Wear OS bundles.
- Unsigned Release builds for iOS/WidgetKit and watchOS.

See [TESTING.md](TESTING.md) for commands, exact scope, and known automation gaps.

## Runtime and product protections

- Cached database flows are observed before network refresh.
- Primary current/hourly data commits before history and air-quality enrichment.
- Provider responses with no complete required hourly row do not replace usable cached data.
- Foreground refreshes are bounded and deduplicated; platform schedulers control background cadence.
- Weather and forecast-snapshot retention is bounded.
- Insight thresholds and hazard exclusions are explicit and deterministic.
- Coordinates cross the privacy boundary only after two-decimal coarsening.

## Accessibility, adaptive, and RTL evidence

The shared UI provides semantic labels/roles/selected state for timeline hours, reflows unit/theme/hour details at increased font scale, constrains content width, and uses expanded-width composition. Arabic mirrors surrounding layout while the chronological timeline is explicitly left-to-right.

The dated [QA matrix](QA_MATRIX.md) records emulator/simulator and TalkBack evidence. Physical VoiceOver gestures/audio and paired watch/device behavior remain release gates; simulator compilation does not close them.

## Performance evidence

[PERFORMANCE.md](PERFORMANCE.md) records the measured environment, method, and limitations for the August 10 checkpoint. Those numbers are not generalized device or adoption claims. New measurements should preserve environment and method details and should not replace the checkpoint silently.

## Known gaps

- No direct state-holder unit tests.
- No automated Compose UI or screenshot-golden suite.
- No physical-device performance runner in CI.
- No end-to-end live-provider test, by design; unit tests avoid depending on an external service.
- Physical VoiceOver and paired watch handoff remain manual.

These gaps are suitable contribution areas, but they should be addressed because they reduce regression risk—not to manufacture activity or inflate a test count.
