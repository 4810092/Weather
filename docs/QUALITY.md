# Quality strategy

Nimbo’s quality evidence has four layers: deterministic shared tests, actual SQLite migration/retention host tests, cross-platform build gates, and dated manual release QA. A claim belongs in the narrowest layer that proves it.

## Local automated gates

- Repository policy, workflow integrity, dependency checksums, and simple
  secret-pattern checks for tracked files.
- Local Markdown-link validation.
- Complete resource/type/placeholder parity for 13 app languages and all widget/watch/permission surfaces.
- Store metadata limits and 123 expected versioned delivery-image dimensions/formats.
- ktlint for Kotlin and Gradle Kotlin scripts.
- 53 unique Kotlin test functions: 49 common and four Android-host platform,
  persistence, and migration tests; plus the repository's complete Python
  growth/release/security regression suite.
- SQLDelight numbered-migration/schema verification plus a released-v1 SQLite fixture migration.
- Deterministic Compose UI device tests on local API 24 phone, API 36
  phone, and API 36 tablet emulators.
- R8/resource-shrunk Android phone/tablet and Wear OS bundles.
- Unsigned Release builds for iOS/WidgetKit and watchOS.

See [TESTING.md](TESTING.md) for commands, exact scope, and known automation gaps.

## Dated CI evidence — 2026-08-29

GitHub Actions run `33243395554` succeeded on exact commit
`79290c6e7cfd3c1ef5e31a557ac7b09840cc72aa` in `13m38s`.
`android-and-shared` completed in `1m49s`; `ios` completed in `13m33s`. The run
retained `android-release-unsigned`, `wear-release-unsigned`, and
`ios-simulator-test-results`. These prove the automated workflow only: the
Android/Wear bundles are unsigned and the iOS artifact is test output, so this
is not signing, store upload, review, publication, or public-availability
evidence.

The separate manual `Signed release candidate` workflow is intentionally not a
normal CI path. An isolated no-secret job builds exact-source unsigned inputs;
a fresh `release-signing` runner receives only that checksummed package and
step-scoped encrypted secrets. Every action uses a reviewed full commit SHA,
and repository policy binds the complete workflow, action blocks, run bodies,
shells, secret environments, and final upload paths. Only a receipt-bound
candidate tarball plus its receipt can be retained for seven days. It has no
store or repository write permission. A green run proves signed candidate
bytes only; it does not close physical-device, crash, upload, review, rollout,
or public-availability gates.

The dated hosted run above and the protected release workflow use reviewed
full-commit action pins. Routine validation now runs locally. Gradle verifies
the official wrapper checksum and the SHA-256 inventory for 1,700+ resolved
dependency artifacts. Generated checksum metadata is reviewed as a supply-chain
allowlist; it is not a claim that every upstream artifact has independent PGP
provenance.

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

The Compose device-test suite covers deterministic onboarding, retry,
large-text, LTR/RTL, and forecast-header semantics on local emulators.
It does not yet assert selected-hour state or prove clipping-free expanded
tablet composition. The dated [QA matrix](QA_MATRIX.md) separately records
historical emulator/simulator and TalkBack evidence. Physical VoiceOver/
TalkBack gestures/audio and paired watch/device behavior remain release gates;
emulator automation does not close them.

## Performance evidence

[PERFORMANCE.md](PERFORMANCE.md) records the measured environment, method, and limitations for the August 10 checkpoint. Those numbers are not generalized device or adoption claims. New measurements should preserve environment and method details and should not replace the checkpoint silently.

## Known gaps

- No screenshot-golden suite.
- No automated physical-device performance gate.
- No end-to-end live-provider test, by design; unit tests avoid depending on an external service.
- Physical VoiceOver and paired watch handoff remain manual.

These gaps are suitable contribution areas, but they should be addressed because they reduce regression risk—not to manufacture activity or inflate a test count.
