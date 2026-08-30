# iOS crash gate — 2026-08-28, refreshed 2026-08-30

Status: **BLOCKED**. Do not scale public acquisition or send outreach while this gate is blocked.

## Evidence reviewed

- A fresh authenticated App Store Connect UI review on `2026-08-29` confirmed
  the same single production crash on `2026-08-25` for app version `1.0.1`.
  Grouping the crash metric by device type and platform version exposed only
  suppressed `-` values, so neither dimension can be used as incident evidence.
- Xcode 26.6 Organizer was opened locally for the Nimbo product. Its Crashes
  view reports `Error Downloading Crashes List — A developer account is
  required for downloading crashes list.` No account/authentication change was
  attempted. This is an access blocker, not evidence that the crash is absent;
  the separate current-source private-signing authorization failure is recorded
  in `growth/quality/signing-readiness-2026-08-29.md`.

- App Store Connect Analytics' own read-only time-series request was reproduced
  with `adamId=6799886897`, measure `crashes`, daily frequency, and exact app-
  version option `1.0.1 (4)` for `2026-05-30` through `2026-08-27` UTC. The
  response reports total `1`, `2026-08-25: 1`, and `meetsThreshold=true`.
  It contains no incident/signature ID, device, OS, stack, binary UUID,
  affected-user count, or downloadable diagnostic log.
- The corresponding version-and-device view is `Insufficient data`.
  TestFlight's separate Crash Feedback page reports `No crash reports`; that
  page covers beta feedback and does not contradict the production Analytics
  aggregate.
- A filename and content search found no Nimbo `.ips` or `.crash` report in the repository, `~/Library/Logs/DiagnosticReports`, or the reviewed Xcode crash-file locations.
- App Store Connect shows iOS `1.0.1 (4)` as Ready for Distribution with Apple Watch included. The matching local release archive exists at `../.nimbo-release/ios/1.0.1-4/Nimbo.xcarchive` and identifies `uz.ganikhodjaev.weather` version `1.0.1` build `4`.
- Every shipped build-4 executable has a matching retained dSYM: main app
  arm64 `31368034-EFDC-3A60-80E0-029ACD982BEA`, widget arm64
  `46A67F70-FAA1-37B6-8870-A73D15646F58`, and watch
  arm64_32 `62FEDFDA-C363-3833-9F97-155EB08B4B46` plus arm64
  `01AFDA2B-068C-3D0B-A596-4D04B7C1630F`. The export used
  `uploadSymbols=true`, and its packaging log records all four symbol bundles.
  Symbolication inputs are locally complete, but the aggregate does not reveal
  which process/UUID crashed.
- Older local Nimbo archives also exist, but an older dSYM must not be used unless its UUID matches the missing crash report.

At `2026-08-29 11:03 +05:00`, a broader read-only recovery audit confirmed the
same boundary. `dwarfdump --verify` passed for the app, widget, and watch dSYM
bundles in the retained build-4 archive, and their UUIDs match every shipped
build-4 executable listed above. No production-matching `.ips` or `.crash`
payload was found in the repository, `.nimbo-release`, user or system
DiagnosticReports/CrashReporter locations, Xcode product and cache locations,
the reviewed user-file locations, simulator/CoreDevice log locations, or the
local metadata index. The Nimbo Xcode product cache has no `Crashes/` directory
and contains only older `1.0` build metadata. The separate Organizer archive
for `1.0 (3)` has a different main executable UUID and is not valid evidence for
the build-4 event. Xcode 26.6 provides `atos`; legacy `symbolicatecrash` is not
present. Once an actual diagnostic is recovered, its architecture, image UUID,
load address, and frame addresses can be matched directly to the retained dSYM.

At `2026-08-29 21:45 +05:00`, a second bounded read-only recovery audit still
found no production diagnostic payload:

- There are zero Nimbo `.ips`, `.crash`, or `.xccrashpoint` items in the user
  DiagnosticReports/CrashReporter paths or anywhere under
  `~/Library/Developer/Xcode`. The build-4 archive also contains zero crash
  payloads, while all three retained dSYM bundles continue to pass
  `dwarfdump --verify` and match the four shipped executable UUIDs above.
- The only host-system diagnostic containing a Nimbo process name is a macOS
  memory-pressure `JetsamEvent` from `2026-08-29`. It lists local simulator
  `NimboWidget` and `NimboWatch` processes as active/suspended alongside the
  host process inventory; the largest process is unrelated. Its date, platform,
  process UUIDs, and event class do not match or diagnose the production iOS
  crash from `2026-08-25`, so it was not copied into the repository.
- One paired iOS device is visible to Xcode, but the read-only CoreDevice
  `systemCrashLogs` file-service query failed because the device is locked. No
  device-log absence is inferred from that failed query. Even a successful
  query could only recover diagnostics present on that physical device, not the
  suppressed report from another opted-in production user.
- No App Store Connect API key/configuration or common issuer/key environment
  variable is present in this repository, the usual user configuration paths,
  or the current process environment. A later bounded host-wide audit did find
  an existing maintainer-owned Team/Individual API key outside this repository.
  Its JWT authenticated successfully and resolved app `6799886897`, so the
  earlier repository-local absence is not treated as a host-wide access result.
- Xcode's bundled `altool` and Transporter are present, but the installed
  `altool` command surface covers upload, validation, provider/app listing, and
  metadata transfer rather than production crash download. No separate `asc`,
  `fastlane`, `pilot`, or `deliver` CLI is installed. These tools therefore do
  not provide an already-authorized crash-recovery path on this host.
- At `2026-08-29 22:56 +05:00`, that existing key returned HTTP 200 for Nimbo's
  app, versions, builds, and analytics-report-request inventory. It confirmed
  public version `1.0.1`, build `4`, and no builds newer than `4`; it also showed
  zero existing analytics report requests. The build-detail and documented
  diagnostic-signature requests for build `4` both returned HTTP 403
  `FORBIDDEN_ERROR` for security reasons. The key therefore closes the
  authentication-discovery gap but cannot retrieve the missing signature or
  diagnostic log. No report request, key, role, app, version, build, or store
  state was created or changed during that read-only audit. See Apple's
  [diagnostic-signature endpoint](https://developer.apple.com/documentation/appstoreconnectapi/get-v1-builds-_id_-diagnosticsignatures)
  and [diagnostic-log endpoint](https://developer.apple.com/documentation/appstoreconnectapi/get-v1-diagnosticsignatures-_id_-logs),
  plus the bounded local record in
  `growth/quality/app-store-connect-api-2026-08-29.md`.

The absence of a local report and Apple's low-volume suppression do not mean the
crash is fixed or harmless. The authoritative aggregate pins the event to
production `1.0.1 (4)`, but the crashed app/extension binary UUID and root cause
cannot be proven without the actual diagnostic report. App Store Connect/Xcode
Organizer remains the authority for the missing report and affected binary.

## Current code inheritance and predecessor execution evidence

Current source authority `2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652`
inherits through predecessor `704fd893e59d94d8e9a4971313a773b3fa545ab6`
the reachable UIKit lifecycle, main-actor completion, storage-startup,
saved-location-limit, and long-lived SQL observation hardening from `97c26cb`.
Predecessor commit `9c2dce4200dbba5487c8c458ade4616005fde6e6`
also closed three deterministic storage-failure paths that previously let a
synchronous database exception escape the delete-place or unit-preference UI
callbacks, or escape the reverse-geocode enrichment coroutine. Four
throwing-repository regression tests now preserve the prior UI/location state
and surface a localized nonfatal message where user action is possible.

The executed tests and exact predecessor Release-simulator SHA-256 values below
belong to `9c2dce4`: app
`b7c3ba937658007b07ee9ad8e85ddc892e90f423e7839e0dc112a1070ea04849`,
widget `7191acd40334d4d9fec6062bc5023450fefbb55006fbd92f57109f41eb27a7ff`,
and watch `c310c785750ffa779e5dfdc30384088fca889deddb11417f2b4e8e0e30109728`.
Their binary and dSYM UUIDs match, the shared iOS simulator suite and 18 Apple
surface tests pass, and source-bound Release simulator builds succeed. The code
is inherited by `2cdd438`, but these executed results and binary identities are
non-transferable; neither can be attributed to the suppressed historical crash
without its missing diagnostic.

Historical run `33296238901` for intermediate authority `fb591e3` passed its
ordinary unsigned iOS job in 20m38s, including shared simulator tests, Apple
surface tests, and the unsigned application build. The overall run failed all
three Android UI profiles. This is unsigned predecessor regression evidence,
not a signed or physical result, and it neither diagnoses the suppressed crash
nor transfers to current authority `2cdd438`.

Predecessor exact-source hosted
[run `33297505825`](https://github.com/4810092/Weather/actions/runs/33297505825)
at evidence commit `163ff034c2b93ec302c4c5bee3c49168e0b33ada` passed
the `ios` job in 17m25s, including shared simulator tests (5m20s), Apple
surface tests (2m29s), and an unsigned build (8m37s). This confirms hosted
regression execution for `704fd893e59d94d8e9a4971313a773b3fa545ab6`.
Evidence-head run
[`33299592101`](https://github.com/4810092/Weather/actions/runs/33299592101)
also passed against that same predecessor release-source tree. Both runs are
non-transferable to current authority `2cdd438`.

For exact current bytes, twelve targeted iOS Simulator provider service and
mapping tests pass, including required-row rejection behavior. These bounded
tests do not supply the suppressed crash diagnostic, symbolication, a complete
current hosted Apple run, distribution-signed bytes, or physical reproduction.
The crash gate remains blocked.

The separate 40-cycle cold-launch/terminate record remains historical to source
`df5f82401348a2cca7405feec36c03621af43ea7`; its app and widget hashes are
`d293763bc3dcf0eee73ebac9db1d5f0e4eda7aca7849c6000e3caf714041f5d9` and
`74b6c6af76d5dc01efb61c2cd66c4fa4b28975704b690bc1371ea21579fd533b`.
It had zero launch/terminate failures or matching crash/fatal lines within that
bounded simulator path, but it is not relabelled as current-source evidence.

These are preventive source and simulator results only. The simulator products
are ad-hoc linked, not distribution-signed, and no physical iPhone result
exists. Because the historical production report, stack, incident ID, and
crashed binary UUID remain unavailable, no current change is attributed to the
2026-08-25 event and `ios_crash_gate` remains **BLOCKED**.

## Required close-out evidence

Immediate recovery paths, in priority order:

1. Authenticate the existing developer account in Xcode, including user-handled
   2FA if requested, then refresh Organizer > Crashes for Nimbo and export the
   actual build-4 incident if Apple exposes it.
2. If Apple grants a role/key access path that is permitted to read diagnostics,
   repeat the already-authenticated build `1.0.1 (4)` signature query and
   download any returned anonymized log. The current key is verified for app and
   inventory reads but receives a security 403 for this diagnostic surface.
3. Unlock the paired iOS device and repeat the `systemCrashLogs` lookup only as a
   local-reproduction aid; do not treat that device's result as the missing
   opted-in production report.

1. Export or download the actual crash report from Xcode Organizer/App Store Connect, preserving incident ID, app version/build, OS/device, occurrence window, affected users, and binary image UUIDs.
2. Match every crashed binary UUID to the exact archived dSYM; symbolicate until application frames contain function/file/line information where symbols permit.
3. Classify the root cause and either reproduce it or explain why reproduction is not possible from the evidence.
4. Implement and test a fix in the owning product code when the crash is actionable.
5. Install the corrected release candidate on a physical iPhone, run cold launch and the affected path, and record the result.
6. After rollout, confirm that the crash cluster no longer appears for the corrected build and that the source-defined iOS stability guardrail is at least 99.8%.

Only then change `growth/quality/gates.json` → `ios_crash_gate.status` to `pass`, with a dated evidence note. Do not infer crash-free sessions as `1 - crashes / sessions`.

## Reproduction commands used for local evidence

```sh
rg -l -i 'uz\.ganikhodjaev\.weather|\bNimbo\b' ~/Library/Logs/DiagnosticReports
find ~/Library/Developer/Xcode -type f \( -iname '*.ips' -o -iname '*.crash' \)
dwarfdump --uuid ../.nimbo-release/ios/1.0.1-4/Nimbo.xcarchive/dSYMs/Nimbo.app.dSYM
dwarfdump --uuid ../.nimbo-release/ios/1.0.1-4/Nimbo.xcarchive/Products/Applications/Nimbo.app/Nimbo
dwarfdump --verify ../.nimbo-release/ios/1.0.1-4/Nimbo.xcarchive/dSYMs/Nimbo.app.dSYM
xcrun atos -arch <arch> -o <matching-dSYM-DWARF-binary> -l <image-load-address> <frame-address>
```
