# Internal store delivery — 2026-08-31

Status: **PARTIAL**. The exact Apple, Android phone, and Wear OS candidates
reached their intended internal store channels, and Apple processing completed
successfully. The phone invite has not been accepted, and the Wear internal
track has no tester group. No store-delivered installation or production
change is claimed.

Follow-up: the phone invite was accepted, Google Play delivered phone
`1.1.0 (8)` for a bounded API 25 smoke, and the Wear tester track became active
on `2026-09-01`. Those later states are recorded separately in
[play-delivered-android-smoke-2026-09-01.md](play-delivered-android-smoke-2026-09-01.md);
the remainder of this file preserves the August 31 checkpoint.

All times below are `Asia/Tashkent` (`UTC+05:00`). The observations come from
the authenticated Transporter and Google Play Console interfaces. Artifact
identity is bound to the retained, independently byte-verified release set for
product source revision
`2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652`.

## Apple / Transporter

- App: `Nimbo Weather`, Apple ID `6799886897`.
- Candidate: `1.1.0 (6)`, exact `Nimbo.ipa` SHA-256
  `7466afb1a06f3000ad5d095734082d57cf58e992bdd7a8bed326e90d26ba39d0`.
- Transporter reported `Delivered` on `2026-08-31 21:40`.
- At `2026-08-31 21:51`, the follow-up Transporter state still reported
  `THE APP IS PROCESSING`.
- A subsequent authenticated, read-only App Store Connect relationship GET
  returned build ID `37307a66-1c14-4c7a-8140-83d6868d6a25`, build number `6`,
  `processingState=VALID`, `buildAudienceType=APP_STORE_ELIGIBLE`, uploaded at
  `2026-08-31 21:47:14` Asia/Tashkent, `minOsVersion=15.0`, `expired=false`, and
  `usesNonExemptEncryption=false`.
- This proves completed Transporter delivery and App Store Connect processing
  of the exact IPA. TestFlight beta-group availability, tester assignment,
  installation, review, production submission, and public availability are not
  yet verified; the available API key returns `403` for the separate
  prerelease/TestFlight-detail endpoints.

## Google Play / phone Internal

- Package: `uz.ganikhodjaev.weather`.
- Candidate: `1.1.0 (8)`, exact phone AAB SHA-256
  `d4a90676f32745ea314b50ced2c9955e86923589534a1a7654ac6f1207e88a62`.
- Internal track ID: `4700083514281298386`.
- At `2026-08-31 21:47`, Play Console reported
  `Доступен внутренним тестировщикам` for the release.
- The existing `License testers` group with four testers is attached.
- The General Mobile device opens the invitation, but the invitation has not
  been accepted and no Play-delivered installation has occurred.

## Google Play / Wear OS Internal

- Package: `uz.ganikhodjaev.weather`.
- Candidate: `1.1.0 (1000008)`, exact Wear AAB SHA-256
  `e76d685b20e86f8878be7c9a1a59ac6edb5781ec8e61d5ecd36feb52ddc1cccf`.
- Wear OS Internal track ID: `4699242452771231163`.
- At `2026-08-31 21:49`, Play Console reported the release as available to
  internal testers.
- The track itself remains `Неактивно` because zero tester groups are
  attached. No Wear installation or paired-device run has occurred.

## Google Play / Uzbekistan store listing

- An authenticated read-only recheck at `2026-08-31 23:17–23:23` confirmed
  that review request `14` is `На рассмотрении`.
- The reviewed change contains only the Uzbekistan Custom Store Listing store
  data for `en-US` (`Nimbo: Ob-havo va prognoz`) and `ru-RU`
  (`Nimbo: Погода и прогноз`).
- Managed publishing is off and the latest verified publication remains
  `2026-08-27`.
- This is review submission evidence, not approval, publication, propagation,
  or rank impact. See
  [google-play-console-2026-08-31.md](google-play-console-2026-08-31.md).

## Boundary

The phone Internal release is tester-addressable, while the Wear release is
uploaded and assigned but its track is inactive without a tester group. Apple
delivery and processing are complete, but beta-group distribution and runtime
installation are not verified. These states do not prove a TestFlight or
Play-delivered install, physical phone/tablet/widget/watch QA, crash resolution,
production review or rollout, public availability, vitals, or store rank.
Production was not changed on either store.
