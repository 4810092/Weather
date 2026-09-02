# TestFlight iOS build 9 delivery — 2026-09-02

Status: **PASS for exact upload and App Store Connect processing only**. The
iPad share regression and the wider Apple physical/crash gates remain blocked.

All times are `Asia/Tashkent` (`UTC+05:00`). No tester address, invite token,
credential value, device serial, or private raw store export is retained.

## Exact candidate identity

- Product/build-input authority:
  `052d12c7dfa6411428d85205d9568462d20ff87d`.
- App: `Nimbo Weather 1.1.0 (9)`, bundle `uz.ganikhodjaev.weather`.
- Exact IPA SHA-256:
  `a57674d7d467474a0697fb39c834a9829f53e68ddb9d4480168bf2dcf3f7ac29`.
- Protected signed-candidate run: `33616952267`; durable materialization run:
  `33626711140`; unpublished draft release: `381212810`.
- Final exact-source CI run `33633738734` passed all five jobs on commit
  `93e699f3d4ac1a28cbbe8beb0ffd15bac80b3b01`.
- Final trusted release verification run `33635751765` passed staging and full
  signed-byte verification on that same commit before upload.

## Delivery result

- The exact IPA above was selected from
  `build/testflight-build9/bytes/Nimbo.ipa` in Apple Transporter under the
  configured Nimbo provider.
- Transporter accepted the package, completed package analysis, uploaded it to
  App Store Connect, and reported `Delivered` at `2026-09-02 18:31 +05:00`.
- Transporter subsequently reported that the app had finished processing.
- No review submission, App Store version attachment, phased release, public
  release, or production availability action was performed.

## Fail-closed physical boundary

At `18:34 +05:00`, CoreDevice reported the paired iPad mini 5 reachable. Its
installed Nimbo identity was `1.1.0 (9)`, but the app remained classified as a
developer app from the earlier development-signed install. That install is not
relabelled as TestFlight evidence. TestFlight `4.3.0 (659.1)` was present and
was launched on the device so the owner can install the processed build.

The distribution-signed TestFlight build has not yet been proven installed on
the iPad, and the system share sheet has not yet been visually observed on that
build. Therefore `ios_crash_gate` and `ios_physical_smoke` remain blocked. A
passing bounded result requires the TestFlight-installed build 9 to open its
native share sheet on iPad without Nimbo terminating, followed by a fresh
process/crash-log check.
