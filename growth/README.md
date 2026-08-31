# Nimbo growth operations

<!-- release-authority-current:start -->
<!-- source_revision:2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652 -->
<!-- artifact:android_phone;source_sync=blocked;byte_verified=false;physical_qa_evidence=none -->
<!-- artifact:wear_os;source_sync=blocked;byte_verified=false;physical_qa_evidence=none -->
<!-- artifact:apple;source_sync=blocked;byte_verified=false;physical_qa_evidence=none -->
<!-- physical_gate:android_physical_smoke=blocked;reason_sha256=22d9bb52c84463b30bd48f7d1200d2ad699b7db52d0b21fd85d7e8aaf95e6de6 -->
<!-- physical_gate:ios_physical_smoke=blocked;reason_sha256=3a05412a933038f96a51086a59f7ddd789b6d6fa534d75445c79fc3c8d3cceb2 -->
<!-- release-authority-current:end -->

The machine field `byte_verified=false` refers to the upload-manifest entry.
Protected-run candidate bytes are verified; durable CI re-verification and
`verified-current` promotion are still blocked.

Current verdict (2026-08-31): **HOLD ACQUISITION**. The canonical 00:00 +05:00
snapshot places Nimbo at `#40` in Apple's official UZ Weather chart and `#88`
for Apple `weather`; all three fixed Google UZ category profiles remain outside
the first 30 and `0/5` generic queries qualify. One auxiliary Apple
`Toshkent ob-havo` result is incomplete, but all required goal surfaces are
decisive and fail, so the verified Top-10 streak remains `0/7`.

Product/build source `2cdd438` passed exact-source ordinary hosted CI
[`#117`](https://github.com/4810092/Weather/actions/runs/33300967788).
Protected signing
[run `33381050098`](https://github.com/4810092/Weather/actions/runs/33381050098)
then passed both jobs with all 8/8 signing inputs and produced retained,
independently verified candidates for phone `1.1.0 (8)`, Wear
`1.1.0 (1000008)`, and Apple `1.1.0 (6)`. This is `3/3
candidate-verified`, not `verified-current`: the committed upload manifest
remains fail-closed at `0/3` because public CI has no durable materialization
route to the private retained package. A receipt-only promotion is prohibited.
The exact-source API 25 debug phone/widget pass remains valid regression
evidence, but upload-derived Android phone/tablet/widget/Wear and TestFlight
iPhone/iPad/widget/watch coverage are missing. The iPhone is currently locked,
the paired watch is offline for runtime queries, and no iOS 15 runtime is
available. No store upload, processing, internal distribution, review, release,
or availability is claimed.

OpenMeteo GmbH has confirmed the exact unpaid, non-monetized organic-promotion
scope for the non-commercial API. Two public iOS `1.0.1 (4)` crashes remain
without diagnostic or symbolication, exact weekly retention and vitals remain
insufficient, and acquisition stays held. A signed candidate, Pages deployment,
or historical device result does not close those independent gates.

## Evidence model

| Evidence | Path | Meaning |
| --- | --- | --- |
| Reported baseline | [baseline/2026-08-28.md](baseline/2026-08-28.md) | User-provided console values, preserved with missing definitions and breakdowns |
| Public rank/search | [data/public-rank](data/public-rank) | Fixed, unauthenticated daily observations with response hashes and bounded absences |
| Console aggregates | [data/weekly](data/weekly) | Validated long-format weekly imports from named App Store Connect / Play Console paths |
| KPI contract | [kpi-framework.json](kpi-framework.json) | Targets, guardrails, seven-day goal, and fail-closed 90-day rules |
| Metric contract | [metric-definitions.md](metric-definitions.md) | Denominators, populations, source caveats, and current official references |
| Operational gates | [quality/gates.json](quality/gates.json) | Provider, crash, device-smoke, and policy state; unknown is not pass |
| Signed artifact byte gate | [quality/release-artifact-byte-verifier-2026-08-30.md](quality/release-artifact-byte-verifier-2026-08-30.md) | Full action-time verifier contract; manifest remains 0/3 verified-current until hosted CI can reopen the retained bytes |
| Successful signed candidate | [quality/signed-candidate-run-33381050098.md](quality/signed-candidate-run-33381050098.md) and [receipt](quality/receipts/signed-candidate-33381050098.json) | Protected run, exact artifact/package/tree hashes, Apple profile bindings, independent verification, durable private retention, and no-upload/no-physical boundary |
| GitHub-hosted signed-candidate readiness | [quality/github-hosted-signed-candidate-readiness-2026-08-30.md](quality/github-hosted-signed-candidate-readiness-2026-08-30.md) | Dated pre-execution design snapshot: two isolated manual master-only hosted jobs, closed-tree verification, the then-current 4/8-secret blocker, and the no-store-upload boundary; the successful run outcome is recorded separately above |
| GitHub release-signing environment | [quality/github-release-signing-environment-2026-08-30.md](quality/github-release-signing-environment-2026-08-30.md) | Dated environment-creation snapshot with the then-current 4/8-secret inventory and no-run/no-signing boundary; current protected-run evidence is recorded by the successful signed-candidate entry above |
| Current release source authority | [quality/release-artifact-source-sync-2026-08-31-2cdd438.md](quality/release-artifact-source-sync-2026-08-31-2cdd438.md) | Exact `2cdd438` identity, successful ordinary and protected hosted runs, 3/3 candidate-verified versus 0/3 manifest-verified boundary, and remaining physical/store gates |
| Review inbox | [reviews/README.md](reviews/README.md) and [reviews/review-inbox.csv](reviews/review-inbox.csv) | Daily non-PII aggregate ratings/review check, 48-hour substantive-response policy, notification boundary, and machine-validated action/SLA state |
| Provider clarification | [legal/open-meteo-clarification-email.md](legal/open-meteo-clarification-email.md) | Exact written Free/non-commercial API permission scope and the material-change boundary |
| Seasonal content backlog | [content/articles.json](content/articles.json) and [content/calendar.csv](content/calendar.csv) | Two source-backed UZ/RU/EN draft articles per month from September through November 2026; every route remains draft-blocked until all publication gates pass |
| Provider capacity | [legal/open-meteo-capacity-contingency-2026-08-29.md](legal/open-meteo-capacity-contingency-2026-08-29.md) | Source-derived request model, implemented cache gate, official limits, and the no-key-in-client boundary |
| Android emulator QA | [quality/android-emulator-smoke-2026-08-28.md](quality/android-emulator-smoke-2026-08-28.md) | API 24/36 live, denied-location, search, offline/error, recovery, and cold-start evidence |
| Android exact-product API 24 QA | [quality/android-api24-current-product-smoke-2026-08-29.md](quality/android-api24-current-product-smoke-2026-08-29.md) | Exact `9c2dce4` no-snapshot API 24 live, activation-tip, cold-start, cached-offline, recovery, byte-identity, and explicit unsigned/emulator boundary |
| Android exact-product physical QA | [quality/android-current-product-physical-smoke-2026-08-29.md](quality/android-current-product-physical-smoke-2026-08-29.md) | Exact `9c2dce4` debug-certificate API 25 onboarding/live/late-day Best Time/tip/offline/recovery/process-health pass; explicitly not upload-signed, tablet/widget, or Wear evidence |
| Android current-authority physical QA | [quality/android-current-product-physical-smoke-2026-08-30-2cdd438.md](quality/android-current-product-physical-smoke-2026-08-30-2cdd438.md) | Exact `2cdd438` debug-certificate physical API 25 denied-location/search/live/cache/recovery/widget/process-health pass; explicitly not upload-signed, physical-tablet, or Wear evidence |
| Exact-current Apple/Wear simulator/emulator QA | [quality/apple-wear-current-product-simulator-smoke-2026-08-30-2cdd438.md](quality/apple-wear-current-product-simulator-smoke-2026-08-30-2cdd438.md) | Exact `2cdd438` iPhone live-provider EN/RU/UZ plus 40-loop evidence, watchOS retained preview-like stale fixture plus 30-loop evidence, and Wear OS cached stale Data Layer plus 10-loop evidence; explicitly unsigned/debug, unpaired, and non-physical |
| Android exact-product tablet/widget QA | [quality/android-current-product-tablet-widget-smoke-2026-08-29.md](quality/android-current-product-tablet-widget-smoke-2026-08-29.md) | Byte-identical exact `9c2dce4` debug APK on an API 36 tablet emulator: Uzbek layout, live forecast, Best Time, durable tip, widget render/tap, large text, rotation, process health, and explicit non-physical/non-upload boundary |
| Historical signed Android physical QA | [quality/android-physical-smoke-2026-08-28.md](quality/android-physical-smoke-2026-08-28.md) | Historical phone vc7 clean API 25 live/search/cold-start evidence and uninstall boundary |
| Trust and feedback QA | [quality/android-trust-feedback-smoke-2026-08-29.md](quality/android-trust-feedback-smoke-2026-08-29.md) | Exact-commit API 25 fresh-install plus API 36 preserved-data update, support/rate destinations, byte identity, and cleanup boundary |
| Public ASO deployment gap | [quality/public-store-deployment-gap-2026-08-29.md](quality/public-store-deployment-gap-2026-08-29.md) | Dated public-store proof plus the authenticated unpublished Google UZ draft boundary |
| Google UZ public-claims parity | [quality/google-play-uz-public-claims-parity-2026-08-30.md](quality/google-play-uz-public-claims-parity-2026-08-30.md) | Exact preserved phone vc6 and Wear 1000007 AAB-derived runtime/structure audit, candidate-only exclusions, creative provenance boundary, and fail-closed listing/assets drift guard; claim parity passes while Console submission remains held by independent gates |
| Google UZ title opportunity | [reports/google-play-uz-title-opportunity-2026-08-30.md](reports/google-play-uz-title-opportunity-2026-08-30.md) | Bounded current rank evidence for replacing the unpublished Uzbek fallback title with `Nimbo Weather: Ob-havo`; no rank guarantee and no Console mutation |
| Apple UZ metadata opportunity | [reports/apple-uz-subtitle-opportunity-2026-08-30.md](reports/apple-uz-subtitle-opportunity-2026-08-30.md) | Explicit `en-GB` routing for Apple's documented UZ default plus the unpublished English subtitle `Best time to go outside`; conversion hypothesis only, with no App Store Connect mutation |
| UZ competitor ASO audit | [reports/aso-competitor-audit-2026-08-29.md](reports/aso-competitor-audit-2026-08-29.md) | Bounded official-store term evidence and the resulting truthful Apple/Google metadata revisions |
| Provider-throttle physical QA | [quality/android-provider-throttle-smoke-2026-08-29.md](quality/android-provider-throttle-smoke-2026-08-29.md) | Pinned source `2004e4f` API 25 fresh-cache skip, manual bypass, recovery, and cleanup evidence |
| Apple runtime QA | [quality/apple-runtime-smoke-2026-08-28.md](quality/apple-runtime-smoke-2026-08-28.md) | Simulator and bounded iPad proof plus the explicit iPhone DDI blocker |
| Apple screenshot provenance | [quality/apple-localized-current-product-capture-2026-08-30.md](quality/apple-localized-current-product-capture-2026-08-30.md) | Twelve source-bound `9c2dce4` build-6 simulator EN/RU/UZ iPhone phone sources across four real states per locale; predecessor evidence for current `2cdd438`, with explicit non-signing/non-physical scope |
| iOS 15 widget compatibility | [quality/ios-widget-compatibility-2026-08-29.md](quality/ios-widget-compatibility-2026-08-29.md) | Pinned implementation source `fc07dd1` minOS/UUID/hash proof plus available-runtime host integration and the explicit missing iOS 15/16 runtime boundary |

The public monitor does not log in, use cookies, bypass access controls, or claim to reproduce personalized store UI. Google results remain sensitive to IP, compatibility, experiments, and server behavior. An absent target is recorded only as `> observed_count`.

## Daily public monitor

The canonical unattended capture is
[`.github/workflows/uz-rank-monitor.yml`](../.github/workflows/uz-rank-monitor.yml).
GitHub schedules it at `19:05 UTC`, which is `00:05` in fixed-offset
`Asia/Tashkent`, and it also supports a bounded manual dispatch from `master`.
The capture job is read-only. A separate job receives `contents: write` only
after a hash-bound snapshot/evaluation bundle has been built, and can push only
the reviewed three-file state transition to the dedicated
`growth-observations` branch.

For a deliberate local diagnostic run:

```sh
python3 scripts/growth/monitor_public_rank.py
python3 scripts/growth/evaluate_growth.py --replace
```

The first command writes `growth/data/public-rank/YYYY-MM-DD.json`. It returns
zero when the required goal evidence is decisive, whether the result is pass or
fail, and non-zero only when that result remains unknown. Auxiliary diagnostic
incompleteness does not fail a decisive goal snapshot. It refuses to silently
overwrite a day unless `--replace` is provided. The second command writes the
current decision record in `growth/reports/`.

For hourly visibility after the canonical daily file already exists, use
`--check-current` for a compact non-writing JSON result or
`--append-intraday` for an append-only local observation. Intraday files are
explicitly ineligible for streak calculation and are ignored by Git; they do
not replace or supplement the one canonical daily result. `--stdout` emits the
full current capture without writing a file. See
[data/public-rank/README.md](data/public-rank/README.md) for the exact contract.

The hosted branch is the unattended rank authority; the workflow never pushes
to protected `master`, publishes Pages, changes store state, sends outreach, or
imports authenticated console data. A reviewed merge may promote its exact
snapshot and evaluation bytes to `master`, after which the existing dashboard
and Pages checks run normally. Until that merge, the public dashboard is
honestly older than the hosted observation branch. The optional macOS launchd
template in [automation](automation) remains uninstalled and must not run in
parallel with the hosted canonical capture. Review-inbox and weekly authenticated
console operations remain separate because they require signed-in evidence and
are not rank-monitor responsibilities.

## Weekly console import

1. In App Store Connect, select the same seven complete days, territory `UZ`, and the needed source/device/version cuts. Capture acquisition, downloads, usage/retention, ratings, crashes, and current policy state. Preserve unique versus total labels.
2. In Play Console, select the same seven days and `UZ`. Capture store-listing visitors/install clicks, installations/first launches, retention, active users, ratings, Android vitals (including worst relevant device models), user loss, and policy state.
3. Copy [imports/templates/weekly_metrics.csv](imports/templates/weekly_metrics.csv). Add one row per metric and dimension. Use `source_scope=summary`, `device=all`, and `app_version=all` only for an actual all-up UZ summary; keep breakdown rows separate.
   The two app-global policy-state metrics are the exception: import them with
   `storefront=ALL`, and require both Apple and Google before the combined
   policy guardrail can pass.
4. Remove unavailable metrics rather than entering zero. Every row needs a human-readable console path in `source_ref`, an evidence date, and the catalogue's exact unit.
5. Validate and normalize:

```sh
python3 scripts/growth/import_weekly.py /path/to/weekly_metrics.csv
python3 scripts/growth/evaluate_growth.py --replace
python3 scripts/growth/generate_weekly_report.py \
  growth/reports/evaluation-YYYY-MM-DD.json
```

The importer rejects unknown metrics, wrong units, negative/non-finite values, duplicate scopes, non-seven-day windows, and stale `source_as_of` dates. Derived rates are calculated only inside an identical platform/storefront/source/device/version scope. The report generator writes `growth/reports/weekly-YYYY-MM-DD.md`, accepts only a schema-valid same-date public-rank snapshot and the exact seven-day weekly period referenced by the evaluation, and cross-checks current ranks, derived ratios, KPI actuals, ratings, and quality guardrails before displaying a result. Missing, rejected, or conflicting linked evidence is rendered as `UNKNOWN` or `CONFLICT`, never as a pass. It is deterministic, offline, and uses an atomic no-clobber write unless `--replace` is explicitly supplied. Raw exports/screenshots should stay in approved private storage; this repository needs only aggregate, non-PII evidence.

The generated report follows [reports/weekly-template.md](reports/weekly-template.md) for the operating review. Do not average store percentages across breakdowns or interpret privacy-thresholded missing rows as zeros.

## 90-day rule and action boundary

The checkpoint is 2026-11-26. The evaluator applies rules in this order:

1. Any critical gate/guardrail failed or unknown → hold acquisition and fix the gate.
2. Sufficient conversion or retention data below target → iterate product and listing.
3. Quality passes and at least one exact comparable primary surface improves by 20+ positions → continue organic work.
4. Quality passes and comparable improvement is below 20 → prepare a paid-pilot/provider-cost proposal only.
5. Non-comparable or insufficient evidence → continue measurement; no paid decision.

No script publishes store changes, sends email/outreach, buys ads, changes the Open-Meteo endpoint, or authorizes spend. Those remain explicit human approvals.

## Verification

All parser and metric tests use local fixtures and do not require network access:

```sh
python3 -m unittest discover -s scripts/growth/tests -v
python3 -m compileall -q scripts/growth
```
