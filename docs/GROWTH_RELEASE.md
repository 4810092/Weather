# Nimbo Uzbekistan growth implementation

Status date: August 31, 2026
Target checkpoint: February 28, 2027
Current decision: **HOLD ACQUISITION**

<!-- release-authority-current:start -->
<!-- source_revision:ba824beae5e72653e42af2b8b78286f61415e3ab -->
<!-- artifact:android_phone;source_sync=verified-current;byte_verified=true;physical_qa_evidence=growth/quality/play-delivered-android-vc9-smoke-2026-09-01.md -->
<!-- artifact:wear_os;source_sync=verified-current;byte_verified=true;physical_qa_evidence=none -->
<!-- artifact:apple;source_sync=verified-current;byte_verified=true;physical_qa_evidence=none -->
<!-- physical_gate:android_physical_smoke=blocked;reason_sha256=068404d1ab6d03570ed2bb2b2aa941a50c67de2c7aeb439046382a852783e645 -->
<!-- physical_gate:ios_physical_smoke=blocked;reason_sha256=cd38593905787c2b212ad2318edeb0027eb30113f541796f61289df25c7d6f71 -->
<!-- release-authority-current:end -->

The machine-validated block is fail-closed for replacement source
`ba824beae5e72653e42af2b8b78286f61415e3ab`: phone vc9, Wear vc1000009, and
Apple build 7 are protected-signed, independently byte-verified, and atomically
`3/3 verified-current`; current-master hosted run `33482814222` repeated the
full verification before store use. Phone vc9 and Wear vc1000009 are now active
on their separate Google Play Internal tracks, and Apple build 7 completed
Transporter delivery and processing. The former vc8/vc1000008/build-6 set remains
historical store/device evidence only and cannot authorize the replacement
release. Build 7 is now Ready to Submit with two invited internal testers, and
phone vc9 has a bounded Play-delivered API-25 pass. TestFlight installation and
the remaining physical QA must still run for the replacement identities.

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
| Apple internal delivery | Replacement `1.1.0 (7)` exact IPA completed processing. App Store Connect lists build ID `baf82ec3-33bc-4df5-898f-b95a5b85ad37` as `Ready to Submit`, attached to the internal group with two invited owner-controlled testers. TestFlight installation remains unverified. Historical build 6 remains `VALID` and `APP_STORE_ELIGIBLE`. |
| Google Play phone/tablet | Nimbo 1.0.2 (6) is active in Production in 177 countries. The version view reports 4 installations. |
| Google Play Wear OS | Nimbo Wear 1.0.2 (1000007) is active in Production in 177 countries, since August 27 at 19:43 Asia/Tashkent. |
| Google Play Internal | Replacement phone `1.1.0 (9)` is active on track `4700083514281298386` and passed a preserved-data Play-delivered physical API-25 update with Google App Signing, branded launcher, live forecast, share, refresh, and widget open. Replacement Wear `1.1.0 (1000009)` is active on track `4699242452771231163` but has no physical install. Production was not changed. |
| Play overview | The August 29 rolling 28-day refresh showed 778 device impressions, 21 installs, 14 first opens, and 11 monthly active devices; D7 and numeric crash/ANR rates remained unavailable. The global rating is 1.000 from one star-only rating and there are zero text reviews. UZ custom listing `4834799756935529888` remains an unpublished draft, without review submission or production change. |
| Store policy | App Store Connect has no open review/compliance action and Google Play Policy status explicitly reports `No issues found`. Play separately warns that production phone 1.0.2 (6) contains deprecated Fragment 1.1.0. |

The versioned baseline, denominator caveats, public-rank snapshot, and gate
state live under [`growth/`](../growth/README.md). The August 31 canonical
public capture places Nimbo at position 40 in the official Apple UZ Weather
chart and position 88 for Apple query `weather`, outside the first 30 Google
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
- Coordinated current source identities are Android phone/tablet `1.1.0 (9)`,
  Wear OS `1.1.0 (1000009)`, and Apple app/widget/watch `1.1.0 (7)` from
  product source `ba824be`. Exact-source CI run `33472603346`, protected
  signing run `33473684554`, and materialization run `33477785531` produced and
  retained exact receipt-bound artifacts in unpublished draft release
  `380257470`. Post-merge CI run `33481183010` passed all five jobs on master
  `18ebcf4`, and protected run `33482814222` then revalidated the mutable draft,
  exact source, signatures, versions, and all three artifact hashes before
  store use. The manifest is atomically `3/3 verified-current` and remains
  `draft-blocked`. Replacement phone vc9 and Wear vc1000009 are active and
  tester-addressable on their separate Play Internal tracks. Exact Apple build
  7 completed Transporter delivery and processing; App Store Connect
  status is Ready to Submit, the internal group is attached, and two
  owner-controlled testers are invited. Phone vc9 has a bounded Play-delivered
  API-25 physical pass; TestFlight installation, physical tablet, and paired
  Wear remain missing. See the
  [source-sync record](../growth/quality/release-artifact-source-sync-2026-09-01-ba824be.md),
  [hosted verification](../growth/quality/release-artifact-full-verification-2026-09-01-hosted.md),
  and [internal delivery record](../growth/quality/internal-store-delivery-2026-09-01-ba824be.md).
  Predecessor source `2cdd438` retains a bounded exact-AAB-derived and
  Play-delivered API 25 phone pass for vc8, including onboarding, live forecast,
  share, offline recovery, large text, TalkBack, natural background networking,
  and widget render/update/open. That evidence does not transfer because vc8
  exposes the Android template launcher icon. Its exact Apple build 6 remains
  historically `VALID` and `APP_STORE_ELIGIBLE`; vc1000008 has an active tester
  track but no physical Wear install. Predecessor source `9c2dce4` has a bounded
  physical API 25 debug pass for
  Russian onboarding, Tashkent without location, live forecast, the truthful
  late-day Best Time boundary, first-tip persistence, cached offline fallback,
  recovery, and product-scoped process health. It also has a fresh no-snapshot
  API 24 emulator pass for live, cold-start, cached-offline, and recovery
  behavior, plus a byte-identical API 36 tablet emulator pass for Uzbek layout,
  live forecast, Best Time, durable-tip persistence, home-screen widget
  render/tap, large text, rotation, and process health. The physical APK uses
  the debug certificate, and the tablet/widget pass is emulator-only. That
  predecessor checkpoint retained an upload-key-signed phone AAB, but there is
  still no replacement upload-derived physical matrix. Exact source
  `2cdd438` has bounded simulator evidence on
  all three remaining watch/phone surfaces: the unsigned iPhone Release
  Simulator passed live-provider EN/RU/UZ capture and `40/40` cold launches;
  unsigned watchOS build 6 rendered an explicitly stale retained preview-like
  `UserDefaults` fixture in EN/RU/UZ and passed `30/30`; and the Wear OS API 37
  debug emulator rendered a stale cached Mountain View Data Layer item in
  EN/RU/UZ and passed the additional `10/10` restored-English loop. Neither
  watch result is a fresh paired transfer. The
  [exact-current simulator/emulator record](../growth/quality/apple-wear-current-product-simulator-smoke-2026-08-30-2cdd438.md)
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
  phone vc9; [source-sync evidence](../growth/quality/release-artifact-source-sync-2026-08-30-2cdd438.md)
  records the boundary.
- Historical Apple `1.1.0 (5)` is archived and exported as a distribution-signed IPA with
  matching app/widget/watch dSYMs. The [Apple artifact evidence](../growth/quality/apple-release-artifacts-2026-08-28.md)
  remains scoped to build 5. Historical Apple build 6 has a retained,
  distribution archive and IPA. That exact IPA completed
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
  on both. Replacement physical tablet and paired Wear OS coverage remains
  required. Source vc9 replaces the API-25 legacy launcher asset, but a
  Play-delivered physical check must confirm the fix before production.
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
  simulator/emulator captures. Separate exact-current watchOS evidence renders
  a stale retained preview-like fixture, while exact-current Wear evidence
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
3. Trusted hosted run `33482814222` completed the required full pinned verifier
   for replacement source `ba824be` and master `18ebcf4`; repeat that protected
   chain before every later artifact reuse. Complete the remaining delivery-
   linked matrix: add physical tablet and paired Wear vc1000009 coverage plus
   post-delivery vitals, install ready build 7 through TestFlight, and complete
   iPhone/iPad/widget/watch QA. The iPad mini
   5 and iPhone 14 Pro are
   paired, booted, and Developer Mode enabled. The iPad has no Nimbo install;
   the iPhone retains public `1.0.1 (4)`. The paired Series 5 watch has
   Developer Mode disabled and its developer tunnel is disconnected. No iOS 15
   runtime is available. Earlier debug/simulator results remain regression
   evidence and cannot satisfy these delivery-linked physical gates.
4. Recheck metadata, privacy/data-safety answers, artwork, accessibility
   declarations, policy status, signing, install/upgrade paths, and the public
   build after propagation.

Current phone vc9, Wear vc1000009, and Apple build 7 are retained and atomically
`verified-current` from source `ba824be`; all earlier release identities remain
non-transferable. The manifest remains `draft-blocked` after the protected
hosted pass and internal store delivery because TestFlight installation and the
remaining exact-artifact physical matrix are still pending.
The [replacement delivery record](../growth/quality/internal-store-delivery-2026-09-01-ba824be.md)
supersedes the predecessor delivery checkpoint without rewriting it. Play
Internal and TestFlight remain bounded QA channels for the exact retained
candidates.
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
