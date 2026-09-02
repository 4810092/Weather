# Nimbo Uzbekistan growth implementation

Status date: September 1, 2026
Target checkpoint: February 28, 2027
Current decision: **HOLD ACQUISITION**

<!-- release-authority-current:start -->
<!-- source_revision:052d12c7dfa6411428d85205d9568462d20ff87d -->
<!-- artifact:android_phone;source_sync=verified-current;byte_verified=true;physical_qa_evidence=none -->
<!-- artifact:wear_os;source_sync=verified-current;byte_verified=true;physical_qa_evidence=none -->
<!-- artifact:apple;source_sync=verified-current;byte_verified=true;physical_qa_evidence=none -->
<!-- physical_gate:android_physical_smoke=blocked;reason_sha256=a127c5322265cf07561c59077cc2e8577cf43aff6d5278f6aa7335453c61f075 -->
<!-- physical_gate:ios_physical_smoke=blocked;reason_sha256=06d5da4898d4797f937404e416a7003e8e0741aa887f62f6d4276ecab5e4afc6 -->
<!-- release-authority-current:end -->

The machine-validated block binds source
`052d12c7dfa6411428d85205d9568462d20ff87d` to phone vc11, Wear vc1000011,
and Apple build 9. Protected run `33616952267` signed and candidate-byte-
verified the exact set, and run `33626711140` durably materialized those exact
bytes. Trusted run `33629490609` independently reverified every artifact, and
all three manifest entries are atomically `verified-current`. The prior vc10/vc1000010/build-8 set is
historical-only because build 8 crashes on the iPad Share path; none of its
internal delivery or physical evidence transfers to the successor.

This document separates implementation readiness from device QA, store review,
and public-release readiness. The repository now contains the product changes,
store package, measurement system, public-site source, provider question, and
outreach drafts required by the six-month Uzbekistan growth programme. None of
those files proves a Top-10 result, closes the remaining quality gates, or
authorizes an external action.

## Live store checkpoint

The following values were rechecked read-only in App Store Connect and Play
Console on the dates stated in each row. They are console observations, not
attached raw exports, and their overview populations are not claimed to be
UZ-only.

| Surface | Verified state |
| --- | --- |
| App Store | iOS/iPadOS 1.0.1 build 4 is `Ready for Distribution`; Apple Watch is included. The August 31 overview shows 300 impressions, 23 product-page views, 8 first downloads, 1 redownload, 3 updates, and 4.86% reported conversion; the available counts/window do not reproduce that console-reported rate. |
| iOS quality | As of August 31, two crashes are shown under version 1.0.1: August 25 and August 29. The August 29 event maps to iPhone; the older device/OS dimension is suppressed. Neither event exposes a diagnostic, stack, incident/signature ID, or binary UUID, so the crash gate remains blocked. |
| Apple internal delivery | Historical `1.1.0 (8)` completed Transporter processing and TestFlight delivery. It passed bounded iPhone QA but reproduced two iPad Share crashes. Successor build 9 is protected-signed and trusted-byte-verified, but not yet TestFlight-delivered or physically passed. |
| Google Play phone/tablet | Nimbo 1.0.2 (6) is active in Production in 177 countries. The version view reports 4 installations. |
| Google Play Wear OS | Nimbo Wear 1.0.2 (1000007) is active in Production in 177 countries, since August 27 at 19:43 Asia/Tashkent. |
| Google Play Internal | Historical phone `1.1.0 (10)` and Wear `1.1.0 (1000010)` remain on separate Internal tracks; vc10 passed bounded API-25 phone QA. Successor vc11/vc1000011 are protected-signed and trusted-byte-verified, but not yet delivered. Production was not changed. |
| Play overview | The August 29 rolling 28-day refresh showed 778 device impressions, 21 installs, 14 first opens, and 11 monthly active devices; D7 and numeric crash/ANR rates remained unavailable. The global rating is 1.000 from one star-only rating and there are zero text reviews. UZ custom listing `4834799756935529888` remains an unpublished draft, without review submission or production change. |
| Store policy | App Store Connect has no open review/compliance action and Google Play Policy status explicitly reports `No issues found`. Play separately warns that production phone 1.0.2 (6) contains deprecated Fragment 1.1.0. |

The versioned baseline, denominator caveats, public-rank snapshot, and gate
state live under [`growth/`](../growth/README.md). The September 1 canonical
public capture places Nimbo at position 66 in the official Apple UZ Weather
chart and below the first 192 results for Apple query `weather`, outside the first 30 Google
Weather category results on all three fixed profiles, and at Top-10 for none of
the five generic Google queries. One auxiliary Apple `Toshkent ob-havo` search
returned only one unique result, but every goal surface was decisive. The
verified streak therefore remains `0/7`. A bounded absence means only “below
the captured slice”; it is never converted to a synthetic rank.

## Implemented, not published

- Uzbek-first first-run city selection with seven major Uzbekistan cities,
  optional current location, and ordinary city search without a permission
  requirement.
- One contextual saved-place/widget tip after the first successful forecast;
  no forced tutorial.
- Local review state requiring at least three successful foreground forecasts
  across two local days. Platform bookkeeping is fail-closed: Android records a
  version only after both Play request and launch tasks complete successfully,
  using a durable success write. iOS prefers `requestReview(in:)` with a
  foreground-active `UIWindowScene`; the app's legacy AppDelegate lifecycle can
  fall back to `requestReview()` only while the application is active and has a
  key window. Request failure or a missing active presentation surface remains
  retryable. Apple and Google still decide whether any review dialog is
  displayed; invocation is not claimed as display.
- Localized share CTA with a canonical platform store link and no coordinates,
  identifiers, or analytics parameters.
- A user-initiated Help and feedback path opens the canonical Nimbo support
  page, and a separate neutral Rate Nimbo action opens the platform store
  listing/review surface. Both are localized across all 13 app languages and
  contain no tracking parameters, incentives, sentiment gating, or change to
  the contextual automatic review policy.
- Android background retry for transient failures, with permanent and no-work
  outcomes kept distinct. A durable retry-pending state preserves WorkManager
  backoff without making another provider call before the one-hour cooldown.
- Automatic provider refreshes are cache-gated to one hour per location across
  foreground activation, foreground checks, Android/iOS background work, and
  failed attempts. Cooldown/retry state survives cold starts; cross-path
  requests coalesce per process; manual refresh and a first uncached location
  remain immediate.
- Coordinated current identities are Android phone/tablet `1.1.0 (11)`, Wear OS
  `1.1.0 (1000011)`, and Apple app/widget/watch `1.1.0 (9)` from source
  `052d12c7dfa6411428d85205d9568462d20ff87d`. The source anchors the native
  share controller for iPad popover presentation. Protected run `33616952267`
  signed and candidate-byte-verified all three exact artifacts. Their manifest
  entries are atomically `verified-current` after durable materialization and
  trusted run `33629490609`; delivery and physical QA remain separate gates.
- Historical coordinated checkpoint identities were Android phone/tablet
  `1.1.0 (8)`, Wear OS `1.1.0 (1000008)`, and Apple app/widget/watch
  `1.1.0 (6)`. Every number is newer than the corresponding live store build.
  Historical product/build source `2cdd438` inherited fail-closed
  `NimboSourceRevision` plumbing, distinct Apple profiles, the pinned dependency
  graph, deterministic Compose UI tests, API 24 desugaring, and standard hosted
  API 24/API 36 phone/tablet jobs. It adds tolerant optional Open-Meteo decoding
  while keeping required weather/time inputs fail-closed. Exact-source ordinary
  hosted CI
  [run #117](https://github.com/4810092/Weather/actions/runs/33300967788)
  passed all five jobs. Protected signing
  [run `33381050098`](https://github.com/4810092/Weather/actions/runs/33381050098)
  then passed with all 8/8 signing inputs and produced retained,
  independently byte-verified phone, Wear, and Apple candidates. The exact
  hashes and schema-v3 receipt are recorded in the
  [signed-candidate evidence](../growth/quality/signed-candidate-run-33381050098.md).
  Hosted materialization run
  [`33392732428`](https://github.com/4810092/Weather/actions/runs/33392732428)
  then stored the exact package and receipt as hash-bound assets in unpublished
  draft release `379745439` and rechecked their API sizes and digests. A fresh
  local macOS full-verifier run then downloaded those exact assets, safely
  extracted the closed tree, checked pinned Bundletool 1.18.3, and returned
  `byte_verified=true` for the exact phone, Wear, and Apple outputs. The
  manifest at that checkpoint promoted the set atomically to `3/3 verified-current` while its
  top-level status remains `draft-blocked`. Because the draft is mutable, every
  successful matching-`master` CI run had to pass the protected no-checkout
  staging job and separate read-only hosted macOS verifier before Pages or
  later artifact use. Exact
  source `2cdd438` now also has a bounded exact-AAB-derived physical phone pass.
  Pinned Bundletool produced an upload-key-signed universal APK directly from
  phone AAB `d4a90676…`; its installed bytes matched SHA-256 `e970352d…` and
  passed clean API 25 onboarding, Tashkent live forecast, share chooser,
  proven-offline cache/fallback, online recovery, and PID-scoped health checks.
  The exact phone and Wear AABs are now accepted on their separate Play
  Internal tracks. Google Play delivered phone vc8 to the dedicated API 25
  target and the bounded cold/live/share/process-health, large-text, and
  system-UI-proven offline/cache/recovery paths succeed. Active system-TalkBack
  focus/TTS traversal also reaches the forecast and all three primary controls;
  the original incompatible TalkBack update was restored byte-for-byte. The
  natural hourly background-network run and physical phone widget render/update/
  open path now pass. The Wear License testers group is attached and that track
  is active, but physical tablet and paired Wear results remain absent. The
  API-25 launcher still exposes the Android template legacy icon, so vc8 cannot
  be promoted. Exact Apple build 6 also completed App Store Connect
  processing as `VALID` and `APP_STORE_ELIGIBLE`, but TestFlight beta-group and
  runtime coverage remain unverified. The iOS crash diagnosis remains blocked.
  See the
  [exact phone physical record](../growth/quality/android-phone-vc8-physical-smoke-2026-08-31.md),
  the earlier [debug regression record](../growth/quality/android-current-product-physical-smoke-2026-08-30-2cdd438.md),
  and [historical source-sync record](../growth/quality/release-artifact-source-sync-2026-08-31-2cdd438.md).
  Predecessor source `9c2dce4` has a bounded
  physical API 25 debug pass for
  Russian onboarding, Tashkent without location, live forecast, the truthful
  late-day Best Time boundary, first-tip persistence, cached offline fallback,
  recovery, and product-scoped process health. It also has a fresh no-snapshot
  API 24 emulator pass for live, cold-start, cached-offline, and recovery
  behavior, plus a byte-identical API 36 tablet emulator pass for Uzbek layout,
  live forecast, Best Time, durable-tip persistence, home-screen widget
  render/tap, large text, rotation, and process health. The physical APK uses
  the debug certificate, and the tablet/widget pass is emulator-only. A then-current
  upload-key-signed phone AAB is retained and `verified-current`, but there is
  still no upload-derived, release-certificate physical matrix. Exact source
  `2cdd438` now has bounded simulator evidence on
  all three remaining watch/phone surfaces: the unsigned iPhone Release
  Simulator passed live-provider EN/RU/UZ capture and `40/40` cold launches;
  unsigned watchOS build 6 rendered an explicitly stale retained preview-like
  `UserDefaults` fixture in EN/RU/UZ and passed `30/30`; and the Wear OS API 37
  debug emulator rendered a stale cached Mountain View Data Layer item in
  EN/RU/UZ and passed the additional `10/10` restored-English loop. Neither
  watch result is a fresh paired transfer. The
  [historical simulator/emulator record](../growth/quality/apple-wear-current-product-simulator-smoke-2026-08-30-2cdd438.md)
  is unsigned/debug and non-physical; none of it is an uploadable artifact or a
  gate closure.
- The 1.1.0 Android candidates pin `androidx.fragment:fragment:1.9.0`
  across phone, shared Android, and Wear OS. Release dependency manifests no
  longer contain Fragment 1.1.0 as the selected version.
- A historical retained upload-signed Wear `1.1.0 (1000008)` artifact embeds revision
  `4d9492a`, so it is historical rather than source-current. The predecessor
  Wear output embeds revision `9c2dce4` but is unsigned. The signed phone
  `1.1.0 (7)` universal APK is likewise a preserved
  historical candidate; it passed physical API 25 clean install, live and
  cold-start forecasts, denied-location/manual-search flow, share sheet, 150%
  text, TalkBack, cached-network fallback/recovery, and contextual review-prompt
  dismissal/no immediate repeat. Those results do not transfer to current
  phone vc10; [source-sync evidence](../growth/quality/release-artifact-source-sync-2026-08-30-2cdd438.md)
  records the boundary.
- Historical Apple `1.1.0 (5)` is archived and exported as a distribution-signed IPA with
  matching app/widget/watch dSYMs. The [Apple artifact evidence](../growth/quality/apple-release-artifacts-2026-08-28.md)
  remains scoped to build 5. Historical Apple build 6 has a retained,
  formerly verified distribution archive and IPA. That exact IPA completed
  Transporter delivery and App Store Connect processing as build 6, `VALID` and
  `APP_STORE_ELIGIBLE`, but no TestFlight beta distribution or physical runtime
  result exists. The exact `2cdd438` unsigned Simulator evidence is historical
  regression proof only. The checked-in
  [localized screenshot provenance](../growth/quality/apple-localized-current-product-capture-2026-08-30.md)
  remains predecessor `9c2dce4` creative evidence; it does not prove TestFlight
  distribution or runtime installation.
- Phone/tablet support lowered from API 26 to the planned API 24 floor; Wear OS
  remains API 30. Predecessor product source `9c2dce4` passes a clean, no-snapshot API
  24 debug run covering no-permission quick-city, live weather, first-forecast
  tip acknowledgement, online cold start, cached-offline refresh, recovery, and
  process health; built and pulled-installed bytes match. The
  [predecessor API 24 evidence](../growth/quality/android-api24-current-product-smoke-2026-08-29.md)
  remains explicitly unsigned and emulator-only. The byte-identical predecessor
  debug APK also passes the bounded API 36 tablet/widget emulator scope in
  [predecessor tablet/widget evidence](../growth/quality/android-current-product-tablet-widget-smoke-2026-08-29.md).
  This closes the stale-product tablet-layout/widget emulator gap only; it is
  not a physical-tablet or upload-signed result. Earlier candidates
  passed API 36 Arabic RTL quick-city/live and English denied-location/search/
  cold-start. The exact
  historical signed phone vc7 passes the expanded physical API 25 matrix listed above;
  the exact post-throttle source `2004e4f` debug APK separately passes API 25 live,
  provider-blocked fresh-cache cold start, manual bypass, recovery, and cleanup.
  Exact `df5f824` debug bytes additionally pass fresh API 25 no-location
  onboarding, live weather, and support/Play destination smoke plus a
  same-certificate preserved-data update on physical API 36; pulled bytes match
  on both. Physical tablet and paired Wear OS coverage remains required, and
  the API-25 legacy launcher icon requires a replacement phone version code
  before production.
- Metadata schema v2, an Uzbek Google custom listing persisted as unpublished
  Console draft `4834799756935529888`, separate Russian copy, an
  Uzbek-oriented Apple Custom Product Page draft, 36 deterministic EN/RU/UZ
  creatives, and localized EN/RU/UZ Play feature graphics. Real EN/RU/UZ
  Android captures prove Best Time, 10-day/AQI, and offline claims. The twelve
  checked-in EN/RU/UZ iPhone phone sources from predecessor `9c2dce4`
  build-6 simulator app cover overview, recent comparison, selected timeline,
  and details states per locale. They prove localized live product pixels for
  the phone creative pack, not signing, physical QA, TestFlight, or store state.
  The attempted Apple offline transition was not captured and is not claimed.
  A separate private exact `2cdd438` set proves the same bounded iPhone states
  against the live provider, but does not silently replace checked-in assets.
  The checked-in watch story still uses locale-matched historical
  simulator/emulator captures. Separate historical watchOS evidence renders
  a stale retained preview-like fixture, while historical Wear evidence
  renders a stale cached Mountain View Data Layer item; neither is a fresh
  paired transfer or physical-watch QA. The draft was not submitted for review
  or published.
  The uncaptured home-screen widget story remains excluded.
- Uzbek/Russian/English landing, press kit, privacy, support, store links, and a
  source-backed growth dashboard. GitHub Pages is deployed and configured for
  `nimbo.uz`; future site/dashboard changes on `master` deploy automatically.
  Public Cloudflare delegation, DNS, Let's Encrypt TLS, redirects, canonicals,
  and the localized production routes have passed the dated launch gate.
- Daily public rank capture, weekly console import, KPI/guardrail evaluation,
  crash/provider gates, a provider clarification draft, and outreach materials.
  Scripts do not log in, publish, send, purchase, or alter provider endpoints.
- An active Codex heartbeat temporarily runs hourly while provider, crash,
  signing, and release-access blockers remain unresolved. It checks Pages and
  the same-day rank snapshot; on Mondays it conditionally imports only a valid
  seven-day console CSV. The repository's launchd template remains uninstalled
  so there is no duplicate scheduler.

These changes are the versioned `1.1.0` source candidate. Direct evidence now
records Apple delivery/processing and both Play Internal assignments. Repository
versioning and historical or locally built artifacts still do not imply tester
access, installation, review, approval, production rollout, or public
availability; each external state must be recorded separately.

## Gates before public acquisition or production rollout

1. Obtain the iOS 1.0.1 crash report from Xcode Organizer/App Store Connect,
   symbolicate it against the retained build-4 archive and dSYM, reproduce where
   possible, fix it, and demonstrate the crash-free-session guardrail. Absence of
   a downloadable report is not a pass.
2. Preserve the 2026-08-29 OpenMeteo GmbH written clearance for the exact free,
   non-monetized and unpaid-organic scope. Reopen the provider decision before
   any monetization, paid promotion, attribution removal, or material usage
   change. A paid/customer credential must never be embedded in a mobile client.
3. Require the protected hosted verifier to recheck the exact mutable draft
   before every later artifact use, then deliver vc10, vc1000010, and build 8
   to Internal/TestFlight. Repeat the
   physical phone/tablet/widget/Wear and iPhone/iPad/widget/watch matrices,
   including the exact copied share payload, iOS 15 coverage where available,
   and post-delivery vitals. Historical build-7 and vc9 results remain
   regression evidence only.
4. Recheck metadata, privacy/data-safety answers, artwork, accessibility
   declarations, policy status, signing, install/upgrade paths, and the public
   build after propagation.

Current vc10, vc1000010, and build 8 are atomically `3/3 verified-current` and
remain `draft-blocked`. The [historical build-7 delivery record](../growth/quality/internal-store-delivery-2026-09-01-ba824be.md)
and its physical evidence document what happened, but cannot close successor
trusted verification, delivery, or runtime gates. Play Internal and TestFlight remain bounded
QA channels for exact source-current candidates.
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
  [`growth/kpi-framework.json`](../growth/kpi-framework.json). Continue bounded
  organic iteration; paid acquisition is outside the approved program.

The success condition remains seven consecutive complete days with Top-10 in
Apple's UZ Weather chart and in Google Play's UZ Weather category across all
three fixed language profiles. Generic Google queries remain ASO diagnostics
and do not advance or break the category streak. Algorithms cannot guarantee
the outcome.
