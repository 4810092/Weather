# Nimbo Uzbekistan growth implementation

Status date: August 28, 2026
Target checkpoint: February 28, 2027
Current decision: **HOLD ACQUISITION**

This document separates implementation readiness from device QA, store review,
and public-release readiness. The repository now contains the product changes,
store package, measurement system, public-site source, provider question, and
outreach drafts required by the six-month Uzbekistan growth programme. None of
those files proves a Top-10 result, closes the remaining quality gates, or
authorizes an external action.

## Live store checkpoint

The following values were rechecked read-only in App Store Connect and Play
Console on August 28. They are console observations, not attached raw exports,
and their overview populations are not claimed to be UZ-only.

| Surface | Verified state |
| --- | --- |
| App Store | iOS/iPadOS 1.0.1 build 4 is `Ready for Distribution`; Apple Watch is included. The overview shows 206 impressions, 5 product-page views, 5 first downloads, 1 redownload, 3 updates, and 4.05% reported conversion. |
| iOS quality | One crash is shown on August 25 under version 1.0.1. Device detail is suppressed as insufficient data and no crash report or stack trace is exposed, so the crash gate remains blocked. |
| Google Play phone/tablet | Nimbo 1.0.2 (6) is active in Production in 177 countries. The version view reports 4 installations. |
| Google Play Wear OS | Nimbo Wear 1.0.2 (1000007) is active in Production in 177 countries, since August 27 at 19:43 Asia/Tashkent. |
| Play overview | The 28-day view shows 21 installations, 14 first launches, and 11 MAU. Ratings and Android vitals are suppressed as insufficient data; there are no unpublished Play changes. |

The versioned baseline, denominator caveats, public-rank snapshot, and gate
state live under [`growth/`](../growth/README.md). The first fixed public capture
places Nimbo outside the first 100 entries of the Apple UZ Weather chart, at
position 81 for Apple query `weather`, outside the observed Google Weather
category slices on all three fixed profiles, and outside the observed Google
search result slices for all five generic queries. A bounded absence means only
“below the captured slice”; it is never converted to a synthetic rank.

## Implemented, not published

- Uzbek-first first-run city selection with seven major Uzbekistan cities,
  optional current location, and ordinary city search without a permission
  requirement.
- One contextual saved-place/widget tip after the first successful forecast;
  no forced tutorial.
- Local review state requiring at least three successful foreground forecasts
  across two local days. A platform request is recorded once per app version
  only after its launch flow completes; a launch failure remains retryable.
- Localized share CTA with a canonical platform store link and no coordinates,
  identifiers, or analytics parameters.
- Android background retry for transient failures, with permanent and no-work
  outcomes kept distinct.
- Phone/tablet support lowered from API 26 to the planned API 24 floor; Wear OS
  remains API 30. The final APK passes localized quick-city/live/cold-start paths
  on API 24/36 emulators and physical API 25, plus physical city search. Broader
  denied-location/offline recovery was exercised on the immediately preceding
  runtime-identical candidate; the signed full matrix remains required.
- Metadata schema v2, an Uzbek Google custom listing, separate Russian copy, an
  Uzbek-oriented Apple Custom Product Page draft, 36 deterministic EN/RU/UZ
  creatives, and a new Play feature graphic. Real EN/RU/UZ Android captures now
  prove Best Time, 10-day/AQI, and offline claims; the uncaptured home-screen
  widget story remains excluded.
- Uzbek/Russian/English landing, press kit, privacy, support, store links, and a
  source-backed growth dashboard. The GitHub Pages workflow is manual-only and
  has not been dispatched.
- Daily public rank capture, weekly console import, KPI/guardrail evaluation,
  crash/provider gates, a provider clarification draft, and outreach materials.
  Scripts do not log in, publish, send, purchase, or alter provider endpoints.
- An active Codex heartbeat runs the public monitor and evaluator daily at
  06:15; on Mondays it conditionally imports a valid user-supplied seven-day
  console CSV. The repository's launchd template remains uninstalled so there
  is no duplicate scheduler.

These changes remain an unnumbered growth release candidate. A marketing
version/build number and external TestFlight or Play Internal upload should be
assigned only when an upload is actually authorized, so the checked-in version
still matches the currently distributed binaries.

## Gates before any campaign or external build

1. Obtain the iOS 1.0.1 crash report from Xcode Organizer/App Store Connect,
   symbolicate it against the retained build-4 archive and dSYM, reproduce where
   possible, fix it, and demonstrate the crash-free-session guardrail. Absence of
   a downloadable report is not a pass.
2. Send the prepared Open-Meteo clarification only after explicit approval and
   record an unambiguous written response. Promotion stays paused while the
   answer is missing. A paid/customer credential must never be embedded in a
   mobile client.
3. Complete the remaining physical matrix. A General Mobile API 25 passes
   Android live/search/cold-start and a signed Release passes bounded physical
   iPad provider/cache/cold-start paths; both QA installs were removed. The
   required iPhone is paired but DDI-blocked. Denied location, cached/offline
   content, share output, review-policy eligibility, background retry, large
   text, TalkBack/VoiceOver, and watch/widget UI still require the versioned RC.
4. Recheck metadata, privacy/data-safety answers, artwork, accessibility
   declarations, policy status, signing, install/upgrade paths, and the public
   build after propagation.

Only after those gates pass should a versioned build be uploaded to
TestFlight/Play Internal. Production submission, Pages deployment, provider or
media email, promotional-content submission, and any spend remain separate
action-time approvals.

## Operating cadence

- Daily: capture Apple UZ Weather plus Apple and three logged-out Google UZ
  category/search profiles, then recompute the consecutive Top-10 streak.
- Weekly: import seven complete UZ console days with country/source/device/version
  definitions and review the generated decision record.
- Every 4–6 weeks: ship only a verified product improvement or fix; never create
  a version solely to influence rank.
- After 500 weekly store visitors: change one creative element at a time and
  accept only a platform-confirmed winner.
- On November 26, 2026: apply the fail-closed 90-day rule in
  [`growth/kpi-framework.json`](../growth/kpi-framework.json). A paid pilot may be
  costed but not purchased without new approval.

The success condition remains seven consecutive complete days with Top-10 on
both required category surfaces and Top-10 for at least two generic Google
queries under the fixed profile quorum. Algorithms cannot make this outcome a
guarantee.
