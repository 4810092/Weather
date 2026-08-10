# Nimbo product specification

Nimbo answers three questions quickly: what the weather is now, what will change over the next few hours, and how today compares with weather the user recently experienced.

## v1 promise

With cached data, the main weather view is meaningful immediately. With a first-run network request, current and hourly data take priority over historical enrichment. The core timeline spans 24 hours before and after now. Recent comparisons cover yesterday through seven days ago without becoming a calendar product.

## Information hierarchy

1. Active place, current temperature, condition, and feels-like temperature.
2. One or two deterministic insights, including a recent-weather comparison.
3. A continuous -24h to +24h timeline with temperature, precipitation, wind, a clear now marker, and an accessible selected-hour detail.
4. A safe, explainable best-time-outside window.
5. Secondary details and forecast-versus-observation history.

## Core flows

- First run explains location value before requesting foreground permission; manual city search is always available.
- Returning users see cached weather first, then a background refresh.
- Denied/unavailable location degrades to city search, never to a dead end.
- Offline users see the last known data with an explicit age and stale state.
- Settings are limited to location, automatic/metric/imperial units, system/light/dark theme, language where supported by the OS, about, privacy, licenses, and data attribution.

## Product constraints

- One active location in v1.
- No account, ads, analytics, background location, or AI/LLM dependency.
- Outdoor guidance is informational and suppressed for dangerous conditions.
- Partial trustworthy weather is preferable to a full-screen error.

## Success criteria

- Cached time to meaningful weather UI is effectively immediate on supported devices.
- Current/hourly failures never erase usable cached data.
- Time calculations use the selected location's IANA timezone.
- English, Russian, Arabic, Spanish, French, German, Portuguese, Simplified Chinese, Japanese, Korean, Hindi, Turkish, and Uzbek ship in v1.
- TalkBack, VoiceOver, large text, reduced motion, RTL, phones, and tablets are release gates.

