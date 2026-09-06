# TestFlight build 11 delivery — 2026-09-06

Status: **UPLOADED, PROCESSED, AND AVAILABLE TO THE EXISTING INTERNAL GROUP**.

The owner authorized TestFlight delivery of the autonomous-widget-refresh fix.
The exact IPA is `1.1.0 (11)`, bundle `uz.ganikhodjaev.weather`, source
`fcffe13be1cc15e83a0609751f696e48c9301444`, SHA-256
`4811f81bc0bc0baa70843061cbb03d0ff0d27e7181b7a2019ea23942d9fe6eb1`.

The protected artifact chain is signing `34047427535`, durable materialization
`34048604324`, and independent trusted verification `34048714127` on exact head
`277f829f6003154541324941beffffba4c9df565`. The final trusted receipt is retained
at `growth/quality/receipts/trusted-release-verification-34048714127.json` and
came from artifact `9993898685`. It verifies the app, widget and Watch as
version 1.1.0/build 11 with the exact source above, matching distribution
signatures, profiles, topology and Mach-O/dSYM identities.

Before delivery, the local IPA hash was checked again, and fixed draft
`383662265` plus assets `547465393` and `547465445` were rechecked through the
GitHub API. They retained the same sizes/hashes and unpublished draft state.
The linked Pages run `34048770250` was skipped; GitHub reported zero deployments
for the trusted verification head.

The existing authenticated Transporter provider displayed Nimbo Weather,
app ID `6799886897`, `1.1.0 (11)`. After Deliver, Transporter reported
**DELIVERED ON 6 SEP 2026 AT 22:32** (Asia/Tashkent) and **THE APP IS PROCESSING**.
The App Store Connect processing confirmation is recorded separately below.

Natural widget refresh on the iPhone remains unverified. After installing this
build, open Nimbo once to transfer the selected location and units to the
versioned App Group, then observe a later widget-produced snapshot without
opening Nimbo. This delivery does not transfer build-10 runtime evidence to
build 11. App Store 1.1.0 (10) remains in Pending Developer Release under manual
release; its approved item was not replaced or released. No Android delivery,
external-beta review submission or public release was performed.

App Store Connect independently listed the new upload as `1.1.0 (11)`, created
September 6 at 10:32 PM, with status `Processing` (`Обработка`). The row had no
build-detail link yet at this observation.

Final App Store Connect confirmation: the TestFlight list shows build 11 as
`Ready to Submit` (`Готово к отправке`) with 90 days remaining. Its detail page
is exactly `1.1.0 (11)`, build UUID `a0d9b47a-70e0-470b-a010-77531c5597aa`.
The detail page contains `Group (1)` and the existing `internal testers group`,
type `Internal`, with two testers. The group attached automatically; no tester,
group, external-beta or review setting was changed.

[Exact TestFlight build](https://appstoreconnect.apple.com/teams/6fedfeb4-4c9f-41c0-8e0a-536fcde83246/apps/6799886897/testflight/ios/a0d9b47a-70e0-470b-a010-77531c5597aa)
is available to the existing internal group. No installation or natural
widget-refresh result is inferred from that availability.
