# iOS crash gate — 2026-08-28

Status: **BLOCKED**. Do not scale public acquisition or send outreach while this gate is blocked.

## Evidence reviewed

- A read-only App Store Connect recheck shows exactly one crash on 2026-08-25 when filtered to iOS version `1.0.1`. The device breakdown is `Insufficient data`; no stack trace, crash identifier, binary UUID, OS/device, build number, or affected-user detail is exposed.
- A filename and content search found no Nimbo `.ips` or `.crash` report in the repository, `~/Library/Logs/DiagnosticReports`, or the reviewed Xcode crash-file locations.
- App Store Connect shows iOS `1.0.1 (4)` as Ready for Distribution with Apple Watch included. The matching local release archive exists at `../.nimbo-release/ios/1.0.1-4/Nimbo.xcarchive` and identifies `uz.ganikhodjaev.weather` version `1.0.1` build `4`.
- The app binary and dSYM both have arm64 UUID `31368034-EFDC-3A60-80E0-029ACD982BEA`. Symbolication inputs for build 4 are therefore locally consistent.
- Older local Nimbo archives also exist, but an older dSYM must not be used unless its UUID matches the missing crash report.

The absence of a local report and Apple's low-volume suppression do not mean the crash is fixed or harmless. The available version filter suggests build 4, but the binary UUID cannot be proven without the report. App Store Connect/Xcode Organizer remains the authority for the missing report and affected binary.

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
```
