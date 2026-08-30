# Nimbo Uzbekistan growth implementation

Status date: August 30, 2026
Target checkpoint: February 28, 2027
Current decision: **HOLD ACQUISITION**

<!-- release-authority-current:start -->
<!-- source_revision:ed1b791b8d1a059e62409713102740e08d014de2 -->
<!-- artifact:android_phone;source_sync=blocked;byte_verified=false;physical_qa_evidence=none -->
<!-- artifact:wear_os;source_sync=blocked;byte_verified=false;physical_qa_evidence=none -->
<!-- artifact:apple;source_sync=blocked;byte_verified=false;physical_qa_evidence=none -->
<!-- physical_gate:android_physical_smoke=blocked;reason_sha256=4cf27d1e463313f525a43af7ff7699312729ec5afa3192f5a72725f662d00e3a -->
<!-- physical_gate:ios_physical_smoke=blocked;reason_sha256=aa63127a1b36d45d5a73398c0a450df7d77e54e7fe39f20c7f1b592f6692a7af -->
<!-- release-authority-current:end -->

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
| Play overview | The August 29 rolling 28-day refresh showed 778 device impressions, 21 installs, 14 first opens, and 11 monthly active devices; D7 and numeric crash/ANR rates remained unavailable. The global rating is 1.000 from one star-only rating and there are zero text reviews. UZ custom listing `4834799756935529888` remains an unpublished draft, without review submission or production change. |
| Store policy | App Store Connect has no open review/compliance action and Google Play Policy status explicitly reports `No issues found`. Play separately warns that production phone 1.0.2 (6) contains deprecated Fragment 1.1.0. |

The versioned baseline, denominator caveats, public-rank snapshot, and gate
state live under [`growth/`](../growth/README.md). The August 30 canonical
public capture places Nimbo at position 22 in the official Apple UZ Weather
chart and position 87 for Apple query `weather`, outside the first 30 Google
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
- Coordinated current source identities are assigned: Android phone/tablet
  `1.1.0 (8)`, Wear OS `1.1.0 (1000008)`, and Apple app/widget/watch
  `1.1.0 (6)`. Every number is newer than the corresponding live store build.
  Current product/build source is `ed1b791`; it keeps fail-closed
  `NimboSourceRevision` plumbing, assigns a distinct App Store profile to each
  Apple product, pins 1,716 hosted-Linux Android and macOS/`iosArm64`
  dependency artifacts including Linux AAPT2 and Kotlin/Native host payloads, and
  seals actual source bytes in the hosted candidate workflow. It has no
  retained signed candidate or physical QA. Exact predecessor `65b2eb9`
  regression hashes do not transfer. Public GitHub Actions run `33291750686`
  is green for release-source-equivalent evidence commit `409949e`: Android job
  `99204520470` passed on `ubuntu-24.04` and iOS job `99204520540` passed on
  `macos-26`. This is hosted CI proof, not signed-artifact or physical-QA proof.
  Predecessor source `9c2dce4` has a bounded
  physical API 25 debug pass for
  Russian onboarding, Tashkent without location, live forecast, the truthful
  late-day Best Time boundary, first-tip persistence, cached offline fallback,
  recovery, and product-scoped process health. It also has a fresh no-snapshot
  API 24 emulator pass for live, cold-start, cached-offline, and recovery
  behavior, plus a byte-identical API 36 tablet emulator pass for Uzbek layout,
  live forecast, Best Time, durable-tip persistence, home-screen widget
  render/tap, large text, rotation, and process health. The physical APK uses
  the debug certificate, and the tablet/widget pass is emulator-only: there is
  still no upload-signed current phone artifact or matching release-certificate
  physical matrix. Apple build 6 has predecessor Release-simulator hashes, and its
  localized iPhone phone capture set contains twelve source-bound
  `9c2dce4` simulator sources across four real states per locale. The attempted
  Apple offline transition was not captured and is not claimed. That proves
  localized phone screenshot provenance only; Apple Watch sources remain
  historical build-5 simulator evidence. It has no
  distribution-signed archive or physical result. None of this evidence is an
  uploadable artifact.
- The unreleased Android candidates pin `androidx.fragment:fragment:1.9.0`
  across phone, shared Android, and Wear OS. Release dependency manifests no
  longer contain Fragment 1.1.0 as the selected version.
- The retained upload-signed Wear `1.1.0 (1000008)` artifact embeds revision
  `4d9492a`, so it is historical rather than source-current. The predecessor
  Wear output embeds revision `9c2dce4` but is unsigned. The signed phone
  `1.1.0 (7)` universal APK is likewise a preserved
  historical candidate; it passed physical API 25 clean install, live and
  cold-start forecasts, denied-location/manual-search flow, share sheet, 150%
  text, TalkBack, cached-network fallback/recovery, and contextual review-prompt
  dismissal/no immediate repeat. Those results do not transfer to current
  phone vc8; [source-sync evidence](../growth/quality/release-artifact-source-sync-2026-08-30-ed1b791.md)
  records the boundary.
- Historical Apple `1.1.0 (5)` is archived and exported as a distribution-signed IPA with
  matching app/widget/watch dSYMs. The [Apple artifact evidence](../growth/quality/apple-release-artifacts-2026-08-28.md)
  remains scoped to build 5. Current Apple build 6 has no distribution-signed
  archive or physical runtime result. Its exact-product ad-hoc simulator hash and
  [localized screenshot provenance](../growth/quality/apple-localized-current-product-capture-2026-08-30.md)
  do not imply the current `ed1b791` binary, App Store Connect, or TestFlight upload.
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
  on both. Upload-signed physical tablet/widget and paired Wear OS coverage
  remain required.
- Metadata schema v2, an Uzbek Google custom listing persisted as unpublished
  Console draft `4834799756935529888`, separate Russian copy, an
  Uzbek-oriented Apple Custom Product Page draft, 36 deterministic EN/RU/UZ
  creatives, and localized EN/RU/UZ Play feature graphics. Real EN/RU/UZ
  Android captures prove Best Time, 10-day/AQI, and offline claims. Apple
  Twelve EN/RU/UZ iPhone phone sources from source-bound predecessor `9c2dce4`
  build-6 simulator app cover overview, recent comparison, selected timeline,
  and details states per locale. They prove localized live product pixels for
  the phone creative pack, not signing, physical QA, TestFlight, or store state.
  The attempted Apple offline transition was not captured and is not claimed.
  The watch story uses locale-matched simulator/emulator captures. The Apple
  Watch capture is build-5 UI evidence and cannot satisfy build-6 QA; neither
  platform capture is physical-watch QA. The draft was not submitted for review
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

These changes are the versioned `1.1.0` source candidate. Repository versioning
and historical or locally built artifacts do not imply TestFlight, Play Internal,
review, approval, rollout, or public availability; each external state must be
recorded only after direct store evidence.

## Gates before public acquisition or production rollout

1. Obtain the iOS 1.0.1 crash report from Xcode Organizer/App Store Connect,
   symbolicate it against the retained build-4 archive and dSYM, reproduce where
   possible, fix it, and demonstrate the crash-free-session guardrail. Absence of
   a downloadable report is not a pass.
2. Preserve the 2026-08-29 OpenMeteo GmbH written clearance for the exact free,
   non-monetized and unpaid-organic scope. Reopen the provider decision before
   any monetization, paid promotion, attribution removal, or material usage
   change. A paid/customer credential must never be embedded in a mobile client.
3. Produce source-synced signed phone vc8, Wear vc1000008, and Apple build-6
   artifacts, then complete the remaining physical matrix. Historical phone
   vc7 passes General
   Mobile clean/live/cold-start, denied-location/manual-search, share,
   large-text, TalkBack, cached-network recovery, and review-prompt paths and was
   removed after QA. A naturally scheduled background refresh passed on the
   earlier debug candidate. Historical Apple `1.1.0 (5)` installed on the iPad
   but could not launch while the device was locked and was removed; the older
   bounded `1.0.1 (4)` iPad runtime pass remains separately scoped. Full
   signed-artifact physical QA for current phone `1.1.0 (8)` and Apple
   `1.1.0 (6)`, plus Android
   tablet/Wear/widget and the unavailable iPhone/watch matrix remains. At the
   latest read-only check the iPad was discoverable and paired in both CoreDevice
   and `xcdevice`, but it was locked; lock-state and no-auto-mount DDI queries
   failed before current DDI readiness could be read. The iPad is therefore not
   action-ready, and no exact-current distribution-signed Apple build exists to
   install. The predecessor phone debug APK separately passed the bounded API
   25 onboarding/live/Best Time/tip/offline/recovery/process-health scope, but
   its debug certificate cannot satisfy this signed-artifact matrix. Its
   byte-identical API 36 tablet/widget emulator pass likewise does not replace
   physical-tablet or signed-candidate QA.
4. Recheck metadata, privacy/data-safety answers, artwork, accessibility
   declarations, policy status, signing, install/upgrade paths, and the public
   build after propagation.

No retained signed artifact is source-current: signed phone vc7, signed Wear
vc1000008, and Apple build 5 all embed or represent historical source. Current
phone vc8, Wear vc1000008, and Apple build 6 are blocked before exact-current
signing and physical QA. The current host's App Store
Connect upload account is unavailable, and its Google credential lacks
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
