# Local premium source boundary — October 6, 2026

Product source: `9d09fb0a2ff6425bf3da2e337954caff8ecd9bf0`. The premium forecast/UI work is local only. Source-current Android phone, Wear OS and Apple distribution artifacts are **blocked**, with no current hashes or signing/runtime evidence. Build identities are unchanged for local development; a separately authorized future release must allocate new identities before delivery.

The previous atomic set from `44d3f7862b61ef95bf2b686820cfba3fc05a7b25` remains preserved in the manifest's historical candidates and `signed-candidate-run-37322319203.md`. “Historical-superseded” refers only to correspondence with local product source, not cancellation, replacement, review or public state in either store. The build13 delivery record `release13-store-submission-2026-10-05.md` is untouched.

Local UI, domain, migration and performance evidence is documented in `docs/TESTING.md`, `docs/INSIGHT_ENGINE.md`, `docs/PERFORMANCE.md` and `qa/visual`. These checks do not establish store-signed runtime, natural widget/background completion, battery performance, or screen-reader speech. No external action was performed.
