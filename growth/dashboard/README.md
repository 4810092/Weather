# Nimbo UZ growth dashboard

`artifact.json` is the canonical, source-backed dashboard definition. The SQL
files contain the bounded reproducible snapshot queries embedded by the
artifact. `report.html` is generated from that artifact with the packaged Data
Analytics portable-artifact renderer; it must not be edited by hand.

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
reported because the available counts/window do not reproduce it. Google
overview values are carried forward from 2026-08-28. The validated
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
release `379745439` and rechecked their API identities, sizes, and digests.

The committed upload manifest now promotes the exact set atomically to `3/3
verified-current` after a fresh local macOS full-byte pass reopened the draft
assets, safely extracted the closed tree, verified pinned Bundletool 1.18.3,
and returned `byte_verified=true` for phone, Wear, and Apple. The top-level
manifest remains `draft-blocked` because physical QA and internal delivery are
missing. The draft is mutable and the protected hosted macOS repeat is pending
until its workflow executes on `master`; no hosted repeat pass is claimed. The
exact-source API 25 debug phone/widget smoke remains regression evidence;
upload-derived Android
phone/tablet/widget/Wear and TestFlight iPhone/iPad/widget/watch physical
coverage are still missing. The iPad mini 5 is ready at CoreDevice level, the
iPhone 14 Pro is paired but locked/DDI-blocked, the paired Series 5 watch is
visible but offline for runtime queries, and no iOS 15 runtime is available.

Two public iOS `1.0.1 (4)` crashes—August 25 and August 29—still lack
diagnostics and symbolication. The August 29 event maps to iPhone; the earlier
device/OS dimension is suppressed. Google UZ Custom Store Listing
`4834799756935529888` remains an unpublished draft, public Play production
remains `1.0.2 (6)`, and the last authenticated Apple inventory contained no
`1.1.0` version or builds 5/6. Signed run `33381050098` performed no store
upload, processing, build association, internal distribution, review, release,
or publication.

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
4. Rebuild `report.html` with the installed Data Analytics portable-artifact
   renderer:

   ```sh
   NIMBO_DATA_ANALYTICS_PLUGIN_ROOT=/absolute/path/to/data-analytics-plugin
   node "$NIMBO_DATA_ANALYTICS_PLUGIN_ROOT/skills/build-report/scripts/deliver_portable_artifact.mjs" \
     --input growth/dashboard/artifact.json \
     --output growth/dashboard/report.html
   ```

5. Run `python3 scripts/check_dashboard_report.py` to prove every cited SQL/JSON
   input, the canonical artifact, and the embedded report payload agree.
6. Run the repository checks again before a dashboard is published.
