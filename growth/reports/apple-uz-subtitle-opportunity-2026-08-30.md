# App Store UZ English metadata opportunity — 2026-08-30

Status: **APPLIED TO REPOSITORY DRAFT; NOT SAVED OR PUBLISHED IN APP STORE
CONNECT**.

## Decision

Add an explicit `en-GB` App Store localization for Uzbekistan's documented
default store language and align the unpublished English subtitles:

- before: `Local forecast, made familiar`
- `en-GB` after: `Best time to go outside`
- `en-US` after: `Best time to go outside`

The default App Store listing keeps `Nimbo Weather` for both English locales.
The UZ Custom Product Page mapping moves its Uzbek-audience fallback from
`en-US` to `en-GB`; the separate Russian payload remains unchanged. Google Play
locale routing is not changed. The upload manifest explicitly aliases the
default `en-GB` visual payload to the existing `en-US` English assets so the
handoff does not depend on implicit screenshot inheritance.

The new subtitle is 23 characters, within Apple's 30-character limit. It is
the exact English label of an implemented Nimbo feature and the first story in
the checked-in benefit-led creative set. It makes no accuracy, safety, ranking,
or outcome guarantee.

## Evidence and hypothesis

Apple's current localization reference lists English (U.K.) as Uzbekistan's
default App Store language and notes that displayed metadata can also depend on
device language, configured localizations, and the app's primary language.
Therefore an `en-US`-only hypothesis was not treated as sufficient UZ routing:
the upload payload now includes the explicit `en-GB` base localization and CPP
mapping. At `2026-08-30 02:01 +05:00`, the public UZ product page still returned
HTTP 200 and the existing `Weather made familiar` subtitle; the `en-GB`,
`en-US`, and `ru` URL variants returned byte-identical HTML with SHA-256
`a7d32a5173169daf502016a62ddb155c8c2c669e5e6d97ad58ee69563c560cbe`.
This proves the public page is unchanged, not that the repository draft has
been deployed.

The canonical public UZ capture at `2026-08-30T00:00:25+05:00` placed Nimbo at
`#22` in Apple's official Weather chart and `#87` for the public `weather`
search. That versioned daily observation is the decision input; append-only
intraday checks remain local diagnostics and are ineligible for the seven-day
goal streak.

The bounded competitor audit inspected 26 unique visible Apple titles and 18
returned subtitles. None of the inspected competitor title/subtitle surfaces
used Nimbo's best-time-outside or recent-weather-comparison proposition. The
generic term remains present in the App Store title `Nimbo Weather`, while the
base keyword field still contains `weather` and `forecast`. The subtitle can
therefore state the differentiated, truthful benefit instead of repeating a
generic forecast phrase.

The reported August 28 baseline included a 4.05% App Store conversion value,
but its source denominator and storefront were not captured and the supplied
counts do not reproduce it. It is directional context only, not statistically
sufficient evidence and not a baseline that can decide a winner. This change
is a single conversion/relevance hypothesis for the next real release; it is
not an A/B-test result or evidence that metadata alone changes category rank.

This decision supersedes only the English-subtitle and UZ English-fallback
choices in the bounded August 29 competitor audit. Its original rationale
remains preserved below the dated supersession note. The Russian
override keeps the title `Nimbo: Погода и прогноз` and the subtitle
`Лучшее время для прогулки`; the UZ Custom Product Page plan also does not
change.

## Sources and operational boundary

- Canonical rank capture:
  `growth/data/public-rank/2026-08-30.json`
- Canonical capture SHA-256:
  `aa9028a53caa546886517ec6ea93951e19473a17b70f9a1d63f2ce9d38f0f75d`
- Competitor evidence:
  `growth/reports/aso-competitor-audit-2026-08-29.md`
- Product label:
  `shared/src/commonMain/composeResources/values/strings.xml`
- Creative claim evidence:
  `store/creative-sets/growth-2026-08.json`
- Baseline definition caveat:
  `growth/baseline/2026-08-28.md`
- Apple App Store localization routing and UZ default language:
  <https://developer.apple.com/help/app-store-connect/reference/app-information/app-store-localizations>
- Apple subtitle limit and primary-language definition:
  <https://developer.apple.com/help/app-store-connect/reference/app-information/app-information/>

The metadata remains repository input. The current App Store Connect key can
read bounded inventory but cannot create the 1.1.0 draft, and no Console field,
Custom Product Page, screenshot, build, submission, review, or public listing
was changed. The exact primary-language state must be rechecked with a
write-capable App Store Connect session before submission; the explicit
`en-GB` payload removes reliance on an undocumented `en-US` UZ fallback but
does not predict every device-language outcome. Publication remains blocked by
the independent crash,
source-signed-artifact and physical-device gates plus the separately recorded
store-access boundary.
