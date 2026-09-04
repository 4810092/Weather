# TestFlight iOS build 10 delivery — 2026-09-04

## Result

The corrected Nimbo `1.1.0 (10)` binary is uploaded, processed by App Store
Connect, and attached to the existing internal TestFlight group. This closes
the upload/processing step only. It does not close the iOS physical-smoke or
crash gate and does not authorize or prove an App Store release.

## Exact artifact chain

- Product source: `fc4b6de9e28fd8956eb64462294b8bcdf405ce7e`.
- Bundle identifier: `uz.ganikhodjaev.weather`.
- Version/build: `1.1.0 (10)`.
- IPA SHA-256:
  `20e8e4ac61c55d856aedcdf88a27a2f11ac4cb036aa2dfa002e729ace1986061`.
- Protected signing run: `33852229166`.
- Durable materialization run: `33855931653`, unpublished draft
  `382592451`, package asset `544061853`, receipt asset `544061890`.
- Final pre-upload trusted verification: run `33859392482`, attempt 1, on
  exact master `d7dbdc3e42d93d2fe1a15219cfb51aba1ba7dd6e`; receipt artifact
  `9931523244` and candidate-stage artifact `9931493836`.
- The final trusted receipt is retained at
  `growth/quality/receipts/trusted-release-verification-33859392482.json`.

The linked Pages run `33859495781` skipped both jobs, and the GitHub
Deployments API returned no deployment for the exact verification head.

## Provider observation

Transporter, already authenticated under the correct provider, accepted the
exact IPA and reported delivery on September 4, 2026 at 14:44 Asia/Tashkent.
Its local history still displayed the asynchronous processing message at the
last observation, so that client text is not used as the processing authority.

App Store Connect independently showed the exact TestFlight build at 14:46:

- build detail: `1.1.0 (10)`;
- binary state: `Confirmed` (`Подтвержден` in the active Russian UI);
- bundle ID: `uz.ganikhodjaev.weather`;
- minimum iOS: `15.0`;
- device family: iPhone, iPad, and Apple Watch;
- symbols included: yes;
- export-compliance non-exempt encryption: no;
- TestFlight build status: `Ready to Submit` (`Готово к отправке`);
- attached group: the existing internal group with two testers.

No tester, group, external-beta, review, rollout, or public-release setting was
changed during the read-only App Store Connect confirmation.

## Initial device observation

At 14:48–14:51 Asia/Tashkent, CoreDevice reported that the connected iPhone 14
Pro on iOS `26.6.1 (23G83)` had automatically updated Nimbo to `1.1.0 (10)`.
The app and its build-10 widget extension launched, the app was then moved to
the background by opening TestFlight, both Nimbo processes remained alive, and
the device crash-log inventory gained no new `Nimbo-*.ips` report. This is a
bounded launch/background observation, not proof that iOS scheduled and
completed `uz.ganikhodjaev.weather.refresh`.

An ephemeral, manually provisioned XCUITest harness then selected Nimbo in the
already authenticated iPad TestFlight app; no Apple Account or MFA prompt was
shown. By 15:03, CoreDevice reported exact `1.1.0 (10)` installed on the
connected iPad mini 5 running iPadOS `26.6.1 (23G83)`. Its build-10 widget
extension was alive, the app-group preference file had been written at 15:01,
and the retained crash-log inventory still contained only the four historical
build-8/build-9 reports from September 2–3. This proves installation and a
bounded app/widget launch only; it does not prove a later OS-scheduled refresh.

The same external harness then held Nimbo foreground for 20 seconds, returned
to the Home Screen, selected the Nimbo small-widget control, and completed with
no UI-test failure. A retained privacy-cropped physical screenshot at 15:04
shows the Nimbo widget rendered for Tashkent with `30°C`, high `30°`, low `19°`,
`0%` precipitation, and `AQI 42`:

- `growth/quality/evidence/testflight-ios-build10/ipad-home-widget.png`
- SHA-256:
  `b7873f9fbfda9780d696827df1c10ce33a4dcbdeca4806c4a055a812bbe15a62`

The QA runner was uninstalled after the check and its exact temporary harness
was moved recoverably to Trash; TestFlight and Nimbo build 10 were retained.

Foreground baselines for the natural background-refresh audit are:

| Device | Last foreground `updated_at` | Baseline plist SHA-256 | Existing Nimbo crash files |
| --- | --- | --- | ---: |
| iPhone 14 Pro | `1788515295` / 14:48:15 +05 | `cc7a95b12a9c246745ccadc77fca97a93a42c7bcec40b9ef8563cb5bea79dd24` | 3; latest 12:54, before build-10 install |
| iPad mini 5 | `1788516112` / 15:01:52 +05 | `a29cc6e879cc250707a4f12f57a33ac14ad6472bd671af53321cd0bd025d2f6e` | 4; latest September 3, before build-10 install |

Both apps were left backgrounded after `sceneDidEnterBackground`, which submits
the one-hour-earliest refresh request. A separate read-only hourly audit will
compare later app-group timestamps and system crash inventories without
launching either app.

A read-only poll at 15:43 Asia/Tashkent confirmed that both devices still had
exact `1.1.0 (10)` and no additional `Nimbo-*.ips` file. The iPhone and iPad
`updated_at` values and plist hashes were still identical to the baselines
above, so this poll does not establish a natural background completion.

## App Store replacement state

The build-9 App Store release was cancelled after its runtime failure. At 15:47
Asia/Tashkent, the owner-authorized App Store Connect replacement detached build
9, selected only exact build 10 (`df093ea0-e1c9-4880-ba12-883acee5a7d1`) for
version `1.1.0`, and saved the change. The version now reports `Prepare for
Submission`; manual release and the seven-day phased update remain selected.
Build 9 is detached and unreleased; the former submission ended as `Developer
Rejected`. It must not be reattached or released, and no public release occurred.
A fresh authenticated reload at 15:55 showed exactly one build row, build 10,
with version status `Prepare for Submission`, manual release, and the seven-day
phased update still selected.

## Fail-closed boundary

Exact device reports prove build 9's main process crashes during OS-scheduled
background refresh. Build 10 has been exercised on both affected form factors
and its iPad widget has been visually observed. It still requires a natural
OS-scheduled background-refresh completion and fresh post-completion crash-log
inspection before the runtime gates can change. No App Store review resubmission
or public release was performed. The owner authorized review submission, but the
repository's fail-closed policy still prohibits that final click until the
natural background gate passes.
