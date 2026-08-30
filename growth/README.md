# Nimbo growth operations

<!-- release-authority-current:start -->
<!-- source_revision:6f72e70fff6eb7566e06dd862e1fad09055343a4 -->
<!-- artifact:android_phone;source_sync=blocked;byte_verified=false;physical_qa_evidence=none -->
<!-- artifact:wear_os;source_sync=blocked;byte_verified=false;physical_qa_evidence=none -->
<!-- artifact:apple;source_sync=blocked;byte_verified=false;physical_qa_evidence=none -->
<!-- physical_gate:android_physical_smoke=blocked;reason_sha256=d8312c034ebd47c24ea6f06f3726d825635916eac85c1af59406a546352b9e3f -->
<!-- physical_gate:ios_physical_smoke=blocked;reason_sha256=48e3d7d79c7932dd280b399d01da63d74762dc35360a43dcf665061ba60ad223 -->
<!-- release-authority-current:end -->

Current verdict (2026-08-30): **HOLD ACQUISITION**. The canonical 00:00 +05:00
public snapshot places Nimbo at `#22` in Apple's official UZ Weather chart and
`#87` for Apple `weather`; all three fixed Google UZ category profiles remain
outside the first 30 and `0/5` generic queries qualify. One auxiliary Apple
`Toshkent ob-havo` search returned only one unique app, but every goal surface
is decisive and fails, so the verified Top-10 streak remains `0/7`. Current
phone vc8, Wear vc1000008, and Apple build 6 have no source-synced signed
artifact or matching release-certificate physical QA. Current product/build
source `6f72e70` keeps fail-closed Apple source-revision plumbing, assigns
bundle-specific App Store profiles to the app, widget, and watch, pins 1,758
dependency artifacts, and adds deterministic Compose UI coverage with API 24
core-library desugaring. Standard GitHub-hosted CI now contains API 24/API 36
phone and tablet jobs plus the existing Android/iOS jobs; their first run for
this authority is pending. A protected, manual GitHub-hosted workflow
implements exact-source signing and pre-manifest byte verification. All prior
compile and hosted results, including run `33291750686` for `ed1b791`, do not
transfer. Its
branch-restricted `release-signing` environment now exists, but its eight
required secrets have not been provisioned and it has not produced a signed
candidate. Local Keychain authorization still rejects Android password
reads and Apple private-key use, so the authoritative result remains `0/3`
byte-verified. The prior `9c2dce4` debug API 24/API 25/
API 36, Apple simulator, and localized capture results remain historical
regression evidence and do not transfer to `6f72e70`. None closes signing,
physical-device, TestFlight, store-state, or the release matrix.
Signed phone vc7 and Apple build 5 are historical evidence only. OpenMeteo GmbH
has confirmed
the exact unpaid, non-monetized organic-promotion scope for the non-commercial
API. The iOS crash diagnostic, complete device matrix, and reconciled console
exports are still missing. A build, a Pages
deployment, or historical device evidence does not close those gates.

## Evidence model

| Evidence | Path | Meaning |
| --- | --- | --- |
| Reported baseline | [baseline/2026-08-28.md](baseline/2026-08-28.md) | User-provided console values, preserved with missing definitions and breakdowns |
| Public rank/search | [data/public-rank](data/public-rank) | Fixed, unauthenticated daily observations with response hashes and bounded absences |
| Console aggregates | [data/weekly](data/weekly) | Validated long-format weekly imports from named App Store Connect / Play Console paths |
| KPI contract | [kpi-framework.json](kpi-framework.json) | Targets, guardrails, seven-day goal, and fail-closed 90-day rules |
| Metric contract | [metric-definitions.md](metric-definitions.md) | Denominators, populations, source caveats, and current official references |
| Operational gates | [quality/gates.json](quality/gates.json) | Provider, crash, device-smoke, and policy state; unknown is not pass |
| Signed artifact byte gate | [quality/release-artifact-byte-verifier-2026-08-30.md](quality/release-artifact-byte-verifier-2026-08-30.md) | Real-byte, signing, identity, source-drift, schema, and evidence checks; current result remains 0/3 verified |
| GitHub-hosted signed-candidate readiness | [quality/github-hosted-signed-candidate-readiness-2026-08-30.md](quality/github-hosted-signed-candidate-readiness-2026-08-30.md) | Two isolated manual master-only hosted jobs, no-secret exact-source build, protected signing, closed-tree receipt/tar verification, missing-secret/Keychain blocker, and explicit no-store-upload boundary |
| GitHub release-signing environment | [quality/github-release-signing-environment-2026-08-30.md](quality/github-release-signing-environment-2026-08-30.md) | Authenticated creation of the branch-restricted environment, public proof that master is protected, explicit 0/8-secret state, and no-run/no-signing boundary |
| Current release source authority | [quality/release-artifact-source-sync-2026-08-30-6f72e70.md](quality/release-artifact-source-sync-2026-08-30-6f72e70.md) | Exact `6f72e70` product/build identity, hosted API 24/API 36 UI matrix, pending-run boundary, non-upload export contract, and explicit non-transferability of every earlier artifact/device result |
| Review inbox | [reviews/README.md](reviews/README.md) and [reviews/review-inbox.csv](reviews/review-inbox.csv) | Daily non-PII aggregate ratings/review check, 48-hour substantive-response policy, notification boundary, and machine-validated action/SLA state |
| Provider clarification | [legal/open-meteo-clarification-email.md](legal/open-meteo-clarification-email.md) | Exact written Free/non-commercial API permission scope and the material-change boundary |
| Seasonal content backlog | [content/articles.json](content/articles.json) and [content/calendar.csv](content/calendar.csv) | Two source-backed UZ/RU/EN draft articles per month from September through November 2026; every route remains draft-blocked until all publication gates pass |
| Provider capacity | [legal/open-meteo-capacity-contingency-2026-08-29.md](legal/open-meteo-capacity-contingency-2026-08-29.md) | Source-derived request model, implemented cache gate, official limits, and the no-key-in-client boundary |
| Android emulator QA | [quality/android-emulator-smoke-2026-08-28.md](quality/android-emulator-smoke-2026-08-28.md) | API 24/36 live, denied-location, search, offline/error, recovery, and cold-start evidence |
| Android exact-product API 24 QA | [quality/android-api24-current-product-smoke-2026-08-29.md](quality/android-api24-current-product-smoke-2026-08-29.md) | Exact `9c2dce4` no-snapshot API 24 live, activation-tip, cold-start, cached-offline, recovery, byte-identity, and explicit unsigned/emulator boundary |
| Android exact-product physical QA | [quality/android-current-product-physical-smoke-2026-08-29.md](quality/android-current-product-physical-smoke-2026-08-29.md) | Exact `9c2dce4` debug-certificate API 25 onboarding/live/late-day Best Time/tip/offline/recovery/process-health pass; explicitly not upload-signed, tablet/widget, or Wear evidence |
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
| Apple screenshot provenance | [quality/apple-localized-current-product-capture-2026-08-30.md](quality/apple-localized-current-product-capture-2026-08-30.md) | Twelve source-bound `9c2dce4` build-6 simulator EN/RU/UZ iPhone phone sources across four real states per locale; now predecessor evidence after `6f72e70`, with explicit non-signing/non-physical scope |
| iOS 15 widget compatibility | [quality/ios-widget-compatibility-2026-08-29.md](quality/ios-widget-compatibility-2026-08-29.md) | Pinned implementation source `fc07dd1` minOS/UUID/hash proof plus available-runtime host integration and the explicit missing iOS 15/16 runtime boundary |

The public monitor does not log in, use cookies, bypass access controls, or claim to reproduce personalized store UI. Google results remain sensitive to IP, compatibility, experiments, and server behavior. An absent target is recorded only as `> observed_count`.

## Daily public monitor

Run once per day while the host timezone is `Asia/Tashkent`:

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

The Codex task has an active local heartbeat named
`Nimbo UZ rank and domain monitor` on a temporary hourly cadence while crash
and release-access blockers are unresolved. It refreshes the public
rank/evaluation state when needed and may append a local intraday observation
without changing the canonical daily streak input; on
Mondays it also imports a new user-supplied, valid seven-day console CSV when
one is present. It never bypasses authentication or 2FA. The optional macOS launchd template in
[automation](automation) remains uninstalled, avoiding a duplicate machine
scheduler.

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
