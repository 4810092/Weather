# Roadmap

Last reviewed: August 16, 2026.

This is a small-maintainer direction of travel, not a promise of dates or a device-support commitment. Completed 1.0 work belongs in [CHANGELOG.md](../CHANGELOG.md); dated store status belongs in [RELEASE_CANDIDATE.md](RELEASE_CANDIDATE.md).

## Near term

- Add direct tests for `WeatherStateHolder` onboarding, cache/refresh failure, search cancellation, and location changes.
- Add more provider robustness fixtures for malformed/truncated daily and air-quality payloads without introducing live-provider CI tests.
- Complete physical-device VoiceOver/TalkBack and paired phone/watch smoke checks for future releases.
- Keep Open-Meteo terms, privacy declarations, dependencies, and store release evidence current.
- Improve contributor-facing source links and examples when an external question exposes a real documentation gap.

## Later, when justified by evidence

- Add stable Compose UI or screenshot regression coverage if it can run reliably on both platform workflows.
- Revisit shared-module boundaries if build performance or independent feature ownership makes extraction worthwhile.
- Add a provider abstraction/fallback only if deployment terms, reliability evidence, or commercial requirements justify the maintenance cost.
- Consider a deliberately synthetic demo-data path if first-run learning/testing remains materially harder than city search.

## Explicit non-goals

- Turning Nimbo into a weather framework or SDK.
- Adding OpenAI or another AI dependency to the weather product for program eligibility.
- Adding telemetry, accounts, ads, or background location without a separate product/privacy decision.
- Publishing roadmap issues, releases, or discussions merely to simulate project activity.
