# TestFlight iOS build 8 iPad share crash — 2026-09-02

Status: **FAIL — SUPERSEDED CANDIDATE**.

The connected iPad mini installed exact TestFlight `Nimbo 1.1.0 (8)`. Live
Toshkent refresh and bounded cache inspection passed, but two attempts to use
Share terminated the app at 13:58 and 13:59 Asia/Tashkent.

Both device system crash reports identified `EXC_CRASH` / `SIGABRT` and the
last Objective-C exception in
`-[UIPopoverPresentationController presentationTransitionWillBegin]`. The
build-8 `UIActivityViewController` did not provide the source view and source
rectangle required for iPad popover presentation.

Source commit `37c2a80f55a0883cca5f2501b93486a70c950b0f` anchors the activity
controller to the active presenter's view and adds an iOS regression test.
Successor authority `052d12c7dfa6411428d85205d9568462d20ff87d` advances Apple to build
9 and the Android identities to vc11/vc1000011. A development-signed build 9
compiled, installed, launched, and remained alive with no new Nimbo crash log,
but the system share sheet was not visually observed. This is not a TestFlight
or distribution-signed pass.

The temporary local crash-log copies were zeroed and moved to Trash after the
bounded exception evidence was recorded. Build 8 must not be promoted.
