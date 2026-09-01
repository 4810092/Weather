# TestFlight iOS build 7 physical smoke — 2026-09-01

Status: **FAIL / bounded evidence only**. Exact TestFlight delivery and an
iPhone cold/live/runtime path are proved, but the share payload contains a
visible duplicate-percent defect. This result blocks production use of build
7 and does not close the iOS crash or physical-matrix gates.

All times below are `Asia/Tashkent` (`UTC+05:00`). No tester email address,
invite token, invitation code, device serial, or private raw store export is
retained in this public record.

## Store and channel identity

- App Store Connect exact build ID:
  `baf82ec3-33bc-4df5-898f-b95a5b85ad37`.
- Candidate: `Nimbo Weather 1.1.0 (7)` from source
  `ba824beae5e72653e42af2b8b78286f61415e3ab`; exact hosted IPA SHA-256
  `b918a8d7fa66d1755ca05486ee02ffac6a73b96ddd72f681bd3f6bfb3108709d`.
- App Store Connect showed the build in internal group
  `c91ad70b-57ea-430f-9489-514b49b3fd4c` as `Тестируется`, expiring in
  90 days. One owner-controlled tester invitation was accepted; the second
  remained invited.
- The TestFlight 4.3.0 client on the connected iPhone 14 Pro refreshed from
  historical `1.0 (3)` to exact `1.1.0 (7)` only after the Apple invitation
  was accepted. Installation was initiated from that exact TestFlight row and
  replaced the public `1.0.1 (4)` install.
- Post-install `devicectl` inventory reported bundle
  `uz.ganikhodjaev.weather`, version `1.1.0`, bundle version `7`, and the
  installed `Nimbo.app` path. This is channel evidence paired with the visible
  TestFlight install flow; it is not a production-availability claim.

## Bounded physical result

- Cold launch completed without a visible error.
- A live Tashkent forecast rendered at `29°`, including the current condition,
  yesterday comparison, 24-hour timeline, and Best Time Outside card.
- The first-success contextual tip rendered and could be dismissed.
- Manual refresh returned to the forecast and the Nimbo process remained
  alive.
- The share action opened the native iOS share sheet. Copying its generated
  payload proved the correct localized call to action and canonical App Store
  URL with no coordinates, identifiers, fragment, or analytics parameters.
- The same payload failed content QA because its first line contained
  `вероятность дождя 0%%` instead of `0%`.

## Fail-closed boundary

The duplicate-percent defect is fixed only in successor source
`8fc43b48b65d17b3339663549cd86208f62f6bb7`; build 7 does not contain that
fix. No Nimbo widget render/open, iPad install, paired-watch install or handoff,
iOS 15 runtime, diagnostic/symbolication result, post-delivery crash-free
window, production submission, review, public availability, or rank effect is
claimed. Build 7 is historical and production-ineligible.
