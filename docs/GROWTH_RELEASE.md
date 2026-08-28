# Nimbo Uzbekistan growth implementation

Status date: August 29, 2026
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
| Store policy | App Store Connect has no open review/compliance action and Google Play Policy status explicitly reports `No issues found`. Play separately warns that production phone 1.0.2 (6) contains deprecated Fragment 1.1.0. |

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
- A coordinated, uploadable growth identity is assigned: Android phone/tablet
  `1.1.0 (7)`, Wear OS `1.1.0 (1000008)`, and Apple app/widget/watch
  `1.1.0 (5)`. Every number is newer than the corresponding live store build.
- The unreleased Android candidates pin `androidx.fragment:fragment:1.9.0`
  across phone, shared Android, and Wear OS. Release dependency manifests no
  longer contain Fragment 1.1.0 as the selected version.
- Phone and Wear `1.1.0` AABs are upload-signed and Bundletool-validated. The
  signed phone universal APK passed physical API 25 clean install, live and
  cold-start forecasts, denied-location/manual-search flow, share sheet, 150%
  text, TalkBack, cached-network fallback/recovery, and contextual review-prompt
  dismissal/no immediate repeat; [artifact evidence](../growth/quality/android-release-artifacts-2026-08-28.md)
  is local only and does not imply a store upload.
- Apple `1.1.0 (5)` is archived and exported as a distribution-signed IPA with
  matching app/widget/watch dSYMs. The [Apple artifact evidence](../growth/quality/apple-release-artifacts-2026-08-28.md)
  is local only and does not imply App Store Connect or TestFlight upload.
- Phone/tablet support lowered from API 26 to the planned API 24 floor; Wear OS
  remains API 30. The post-Fragment debug candidate passes API 24 quick-city/
  live/cold/cache/recovery and API 36 Arabic RTL quick-city/live. An earlier
  candidate passed API 36 English denied-location/search/cold-start. The exact
  signed phone release passes the expanded physical API 25 matrix listed above;
  the naturally scheduled background refresh passed on the post-Fragment debug
  candidate. Physical tablet, widget, and paired Wear OS coverage remain
  required.
- Metadata schema v2, an Uzbek Google custom listing, separate Russian copy, an
  Uzbek-oriented Apple Custom Product Page draft, 36 deterministic EN/RU/UZ
  creatives, and a new Play feature graphic. Real EN/RU/UZ Android captures now
  prove Best Time, 10-day/AQI, and offline claims; the uncaptured home-screen
  widget story remains excluded.
- Uzbek/Russian/English landing, press kit, privacy, support, store links, and a
  source-backed growth dashboard. GitHub Pages is deployed and configured for
  `nimbo.uz`; future site/dashboard changes on `master` deploy automatically.
  Public DNS/TLS remain unavailable while the `.uz` registry has not published
  the registrar's Cloudflare delegation.
- Daily public rank capture, weekly console import, KPI/guardrail evaluation,
  crash/provider gates, a provider clarification draft, and outreach materials.
  Scripts do not log in, publish, send, purchase, or alter provider endpoints.
- An active Codex heartbeat temporarily runs hourly while checking domain
  activation, Pages health, and the existing same-day rank snapshot. After the
  domain is healthy it returns to daily 06:15 operation; on Mondays it
  conditionally imports a valid supplied seven-day console CSV. The repository's
  launchd template remains uninstalled so there is no duplicate scheduler.

These changes are the versioned `1.1.0` growth release candidate. Repository
versioning and locally built artifacts do not imply TestFlight, Play Internal,
review, approval, rollout, or public availability; each external state must be
recorded only after direct store evidence.

## Gates before public acquisition or production rollout

1. Obtain the iOS 1.0.1 crash report from Xcode Organizer/App Store Connect,
   symbolicate it against the retained build-4 archive and dSYM, reproduce where
   possible, fix it, and demonstrate the crash-free-session guardrail. Absence of
   a downloadable report is not a pass.
2. Send the prepared Open-Meteo clarification through an authenticated sender
   and record an unambiguous written response. Promotion stays paused while the
   answer is missing. A paid/customer credential must never be embedded in a
   mobile client.
3. Complete the remaining physical matrix. The signed phone RC passes General
   Mobile clean/live/cold-start, denied-location/manual-search, share,
   large-text, TalkBack, cached-network recovery, and review-prompt paths and was
   removed after QA. A naturally scheduled background refresh passed on the
   debug candidate. The exact Apple `1.1.0 (5)` archive installed on the iPad
   but could not launch while the device was locked and was removed; the older
   bounded `1.0.1 (4)` iPad runtime pass remains separately scoped. Physical
   Android tablet/Wear/widget and the unavailable, previously DDI-blocked iPhone
   matrix remain.
4. Recheck metadata, privacy/data-safety answers, artwork, accessibility
   declarations, policy status, signing, install/upgrade paths, and the public
   build after propagation.

Signed Android and Apple artifacts are locally available. The current host's
App Store Connect upload account is unavailable, and its Google credential lacks
the Android Publisher scope; [upload readiness evidence](../growth/quality/internal-track-upload-2026-08-28.md)
records that neither internal track was changed. Play Internal and TestFlight
remain bounded QA channels once an authenticated upload path is available.
Production rollout and public acquisition remain fail-closed until the crash,
provider, physical-device, and console guardrails pass.

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
