# iOS crash gate — 2026-08-28, refreshed 2026-08-29

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
build-4 executable listed above. No matching `.ips` or `.crash` payload was
found in the repository, `.nimbo-release`, user or system
DiagnosticReports/CrashReporter locations, Xcode product and cache locations,
the reviewed user-file locations, simulator/CoreDevice log locations, or the
local metadata index. The Nimbo Xcode product cache has no `Crashes/` directory
and contains only older `1.0` build metadata. The separate Organizer archive
for `1.0 (3)` has a different main executable UUID and is not valid evidence for
the build-4 event. Xcode 26.6 provides `atos`; legacy `symbolicatecrash` is not
present. Once an actual diagnostic is recovered, its architecture, image UUID,
load address, and frame addresses can be matched directly to the retained dSYM.

The absence of a local report and Apple's low-volume suppression do not mean the
crash is fixed or harmless. The authoritative aggregate pins the event to
production `1.0.1 (4)`, but the crashed app/extension binary UUID and root cause
cannot be proven without the actual diagnostic report. App Store Connect/Xcode
Organizer remains the authority for the missing report and affected binary.

## Current-source hardening evidence — does not close the gate

Exact product commit `97c26cbec570468b4971daa7779e3839aa4c48ce`
hardens reachable UIKit lifecycle, main-actor completion, storage-startup,
saved-location-limit, and long-lived SQL observation failure paths. Focused
tests, a clean full Gradle gate, and exact Release simulator builds passed.

The exact `1.1.0 (6)` simulator app executable SHA-256 is
`e6a43119ff23a1ffd3fb0da600bfad9334b94f3ce7a15d244afa9744d853c539`;
the embedded widget SHA-256 is
`0df017e7e3f01e04acdba3b7cbb304e442318b2fad4e2ca68b1fba0a391afa94`.
The app completed 40 cold-launch/terminate cycles with zero launch or terminate
failures, new matching diagnostics, scene-lifecycle faults, unexpected-executor
faults, or matching crash/fatal lines in the bounded log.

These are preventive source and simulator results only. The simulator products
are ad-hoc linked, not distribution-signed, and no physical iPhone result
exists. Because the historical production report, stack, incident ID, and
crashed binary UUID remain unavailable, no current change is attributed to the
2026-08-25 event and `ios_crash_gate` remains **BLOCKED**.

## Required close-out evidence

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
