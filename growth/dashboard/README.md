# Nimbo UZ growth dashboard

`artifact.json` is the canonical, source-backed dashboard definition. The SQL
files contain the bounded reproducible snapshot queries embedded by the
artifact. `report.html` retains the legacy packaged Data Analytics runtime and
must not be edited by hand. The repo-owned synchronizer deterministically
refreshes both the canonical gzip-base64 artifact consumed by the JavaScript
reader and a compact semantic no-JavaScript fallback from the same manifest,
datasets, blocks, tables, access issues, and source summaries.

The dashboard is intentionally `blocked`, with scale status `hold`.
The canonical `2026-08-31T02:51:00+05:00` capture places Nimbo at `#88`
for Apple `weather` and `#40` in the official Apple UZ Weather chart.
All three fixed Google category profiles remain outside the first 30 and
`0/5` generic Google queries qualify. The incomplete auxiliary Apple
`Toshkent ob-havo` result is not a required goal surface; required evidence
is decisive and failed, so the verified Top-10 streak remains `0/7`.

The current App Store Connect overview reports 300 impressions, 23 product-page
views, 8 first downloads, 1 redownload, 3 updates, and 4.86% reported
conversion, with insufficient retention. That conversion is preserved as
reported because the available counts/window do not reproduce it. The current
global Play last-28-days dashboard reports 25 installs, 18 device first
launches, and 13 monthly active devices. The directional `18 / 25 = 72%` is
not treated as a reconciled cohort rate. Play impressions, listing conversion,
and ratings remain carried forward from 2026-08-28. The validated
2026-08-18..2026-08-24 Play export has 26 all-country visitors and 11 unique
install clicks, while UZ has 0 visitors and 0 clicks; UZ conversion is
`UNKNOWN`, not zero.

Product/build source
`2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652` passed exact-source ordinary
GitHub Actions run
[`33300967788`](https://github.com/4810092/Weather/actions/runs/33300967788).
Protected run
[`33381050098`](https://github.com/4810092/Weather/actions/runs/33381050098)
then passed both jobs with all 8/8 signing inputs and produced retained,
independently byte-verified phone AAB `d4a90676…`, Wear AAB `e76d685b…`,
and Apple IPA `7466afb1…`. The schema-v3 receipt, hosted package, exact
profiles, independent verifier result, GitHub metadata, extracted bytes, and
complete checksums are retained privately outside Git; the non-secret receipt
and evidence are committed. Hosted materialization run
[`33392732428`](https://github.com/4810092/Weather/actions/runs/33392732428)
stored the exact package and receipt as hash-bound assets in unpublished draft
release `379745439` and rechecked their API identities, sizes, and digests. The
latest protected current-`master` chain
[`33405849102`](https://github.com/4810092/Weather/actions/runs/33405849102)
completed both staging and read-only verification, reopening the mutable draft
and producing a fresh trusted receipt; no hosted repeat is pending.

The committed upload manifest now promotes the exact set atomically to `3/3
verified-current` after a fresh local macOS full-byte pass reopened the draft
assets, safely extracted the closed tree, verified pinned Bundletool 1.18.3,
and returned `byte_verified=true` for phone, Wear, and Apple. The top-level
manifest remains `draft-blocked` because authorized tester access, TestFlight
beta distribution, and store-delivered physical QA are missing. The draft is
mutable, so every successful current-`master` CI run must
pass protected no-checkout staging and the separate read-only hosted macOS
verifier before Pages or later artifact use. The exact upload-key-signed phone
AAB was converted to an APK set without rebuilding; its universal APK matched
the installed package byte-for-byte and passed clean API 25 phone smoke,
including onboarding, live forecast, share, offline cache/error, recovery, and
process-log checks. Evidence is retained in
`growth/quality/android-phone-vc8-physical-smoke-2026-08-31.md`. Play-delivered
phone validation and physical tablet/widget/Wear coverage remain blocked, as
does the TestFlight iPhone/iPad/widget/watch matrix. The iPhone 14 Pro and iPad
mini 5 are paired, booted, and have Developer Mode enabled. The paired Series 5
watch has Developer Mode disabled and its developer tunnel is disconnected; no
iOS 15 runtime is available.

Two public iOS `1.0.1 (4)` crashes—August 25 and August 29—still lack
diagnostics and symbolication. The August 29 event maps to iPhone; the earlier
device/OS dimension is suppressed. Google review request `14` contains only
the UZ Custom Store Listing `4834799756935529888` en-US and ru-RU store data
and is under review; it is not yet approved or published. Public Play
production remains `1.0.2 (6)`. Exact phone `1.1.0 (8)` and Wear
`1.1.0 (1000008)` are on
their separate Play Internal tracks, but the phone invite is unaccepted and the
Wear track has no tester group. Authenticated App Store Connect inventory now
reports exact Apple build `1.1.0 (6)` as `VALID` and `APP_STORE_ELIGIBLE`;
TestFlight beta distribution/install remains unverified. No production review,
rollout, public availability, or rank follows from these internal states.

OpenMeteo GmbH's written clearance passes only for the exact free,
non-monetized app and unpaid organic-promotion scope. The `nimbo.uz` DNS,
TLS, redirects, localized routes, and metadata checks pass. All eight critical
metric guardrails remain `unknown`, independently blocking scale; the
point-in-time app-global policy gate remains separate from numeric vitals and
retention evidence.

Refresh order:

1. Run the public rank monitor and import the latest store exports.
2. Reconcile every numerator, denominator, window, country, device, and version.
3. Update the bounded SQL and artifact snapshot.
4. Refresh the canonical embedded payload and semantic static fallback:

   ```sh
   python3 scripts/growth/sync_dashboard_report_payload.py
   ```

   This fail-closed operation requires exactly one valid `gzip-base64` artifact
   template and one fallback `<main>`, replaces the payload with deterministic
   gzip output (`mtime=0`, platform-neutral OS header), and rebuilds the fallback
   only from the canonical artifact while leaving the reader runtime untouched.
5. Run `python3 scripts/check_dashboard_report.py` to prove every cited SQL/JSON
   input, the canonical artifact, embedded reader payload, and fallback freshness
   marker agree.
6. Run the repository checks again before a dashboard is published.
