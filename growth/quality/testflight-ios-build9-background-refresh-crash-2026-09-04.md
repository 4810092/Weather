# TestFlight iOS build 9 background-refresh crash — 2026-09-04

Status: **FAIL — DO NOT RELEASE APPLE BUILD 9**.

Two device system crash reports recovered read-only from the paired iPad prove
that exact TestFlight `Nimbo Weather 1.1.0 (9)` crashes while completing a
background weather refresh. The widget extension is not the crashed process;
iOS launched the main Nimbo process in the background, which explains why the
system alert can appear even when the user did not open the app.

No raw `.ips` report, device identifier, container path, incident identifier,
or tester/account data is retained in Git. After the bounded facts and hashes
were recorded, all four temporary raw crash-log copies were overwritten to
zero bytes and moved to the local Trash; the source logs on the device were not
deleted.

## Exact affected identity

- Bundle: `uz.ganikhodjaev.weather`.
- Version/build: `1.1.0 (9)`.
- Distribution: TestFlight.
- Exact uploaded IPA SHA-256:
  `a57674d7d467474a0697fb39c834a9829f53e68ddb9d4480168bf2dcf3f7ac29`.
- App Mach-O UUID:
  `86A2A899-D90D-3820-B9FF-E4F35D0C19BF` (`arm64`).
- The UUID of the retained build-9 app dSYM matches the UUID in both reports.
- Device class and OS: iPad mini 5 (`iPad11,1`), iPadOS `26.6.1 (23G83)`.

## TestFlight build-level metric

A read-only TestFlight build-detail observation on 2026-09-04 reports exact
Nimbo Weather `1.1.0 (9)`: 2 installs, 7 sessions, and 3 crashes. This is
build-scoped UI telemetry. The tester-group aggregate of 22 sessions and 8
crashes spans builds and is not attributed to build 9. The two recovered,
UUID-matched iPad `.ips` reports below are separately symbolicated incident
evidence; they do not identify or account for every console-counted crash.

## Recovered incidents

Both reports name `Nimbo` as `procName`, not `NimboWidget`, and both have the
same failure signature on `com.apple.root.default-qos`:

| Capture time (`Asia/Tashkent`) | Exception | First runtime frames |
| --- | --- | --- |
| `2026-09-03 13:45:08 +05:00` | `EXC_BREAKPOINT / SIGTRAP` | `_dispatch_assert_queue_fail` → `_swift_task_checkIsolatedSwift` |
| `2026-09-03 14:49:30 +05:00` | `EXC_BREAKPOINT / SIGTRAP` | `_dispatch_assert_queue_fail` → `_swift_task_checkIsolatedSwift` |

Symbolication with the exact build-9 dSYM resolves the app/Kotlin frames to:

1. `closure #2 in AppDelegate.handleBackgroundRefresh(_:)`;
2. the Swift-to-Kotlin escaping-closure thunk;
3. `startCancellableBackgroundRefresh...invokeSuspend` at
   `BackgroundWeatherUpdater.kt:90`;
4. the Kotlin coroutine continuation and Darwin global queue dispatcher.

## Root cause

`AppDelegate` is `@MainActor`. Build 9 created the Kotlin `onComplete` closure
inline inside `handleBackgroundRefresh`, so Swift 6 recorded MainActor
isolation on the outer closure itself. `BackgroundWeatherUpdater` runs on
`Dispatchers.Default` and invokes that closure after the refresh. Swift traps
on the queue assertion before the closure body can execute its inner
`Task { @MainActor ... }` hop.

The Home Screen widget is therefore a trigger/correlation, not the crashed
binary: WidgetKit causes periodic background refresh activity, and the main
app process fails when Kotlin returns the result from its worker queue.

## Local correction

Product/build-input authority
`fc4b6de9e28fd8956eb64462294b8bcdf405ce7e` creates both BGTask callbacks in
top-level, nonisolated `@Sendable` factories outside `@MainActor AppDelegate`
and advances Apple to `1.1.0 (10)`. Their outer bodies are safe on an arbitrary
queue and explicitly enqueue only the BGTask lifecycle work on `MainActor`.
The existing locked `BackgroundRefreshState` continues to guarantee exactly
one terminal completion and cancels a handle installed after an expiration
race.

`scripts/check_repository.py` now rejects an inline Kotlin completion and
requires both `@Sendable` factories to remain before the `@main` AppDelegate,
with an explicit `MainActor` hop.

## Verification and remaining boundary

- The exact build-9 dSYM symbolication reproduces the same call chain for both
  incidents.
- Source-current Swift 6 Debug and unsigned Release simulator builds compile
  after the correction; the companion watch Release build also succeeds.
- `:shared:iosSimulatorArm64Test` passes, and the native surface suite passes
  `18/18` tests.
- Static repository validation rejects restoration of the actor-inheriting
  inline callback.
- Before the source transition, canonical `scripts/local-ci.sh apple` correctly
  stopped because corrected `AppDelegate.swift` did not match the build-9
  manifest revision. After source authority and the atomically blocked build-10
  manifest were synchronized, the complete Apple entry point passed: shared
  iOS tests, `18/18` native surface tests, and unsigned Release iOS/widget/watch
  builds. No missing signed byte was relabelled as current.
- The corrected build 10 source is not present in the already signed/uploaded
  build 9. Protected run `33852229166` has since signed and
  candidate-byte-verified build 10, and run `33855931653` durably retained the
  exact package in unpublished draft `382592451`. Independent trusted
  verification, upload, and TestFlight exercise remain pending.

Apple build 9 is therefore a failed candidate even though its bytes and prior
source identity remain verifiable. It must remain unreleased. A monotonically
new Apple build, followed by source-bound Release validation and TestFlight
background/widget exercise, is required before either Apple runtime gate can
pass. The user also reports the symptom on an iPhone, but this evidence set
contains only the two exact iPad reports and does not overclaim an unrecovered
iPhone diagnostic.
