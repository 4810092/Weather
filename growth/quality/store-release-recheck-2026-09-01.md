# Store release recheck — 2026-09-01

Status: **PLAY REVIEW STILL PENDING; APPLE BUILD VALID BUT TESTFLIGHT
UNVERIFIED**.

Observed at `05:05–05:11` Asia/Tashkent. No Console, store, tester, release,
device, or account state was changed.

## Google Play

The authenticated Nimbo publishing overview still reports `Изменения на
проверке` and says the changes are under review. Managed publishing remains
off, and the latest displayed publication is still `2026-08-27`. The reviewed
set contains only the Uzbekistan Custom Store Listing:

- `en-US`: `Nimbo: Ob-havo va prognoz`;
- `ru-RU`: `Nimbo: Погода и прогноз`.

A fresh logged-out public request to the Uzbekistan product page with
`gl=UZ&hl=uz` still renders the heading `Nimbo`, `10+`, and the old English
description. This proves that the new UZ listing is not publicly propagated at
this cutoff. It does not predict the review outcome or rank effect.

## Apple

The App Store Connect web route redirected to login with
`authResult=FAILED`, so no web-only beta-group claim is made. The existing
maintainer API key authenticated successfully and resolved app `6799886897`.
Its app-build relationship again returned build
`37307a66-1c14-4c7a-8140-83d6868d6a25` as exact version `6` with:

- `processingState=VALID`;
- `buildAudienceType=APP_STORE_ELIGIBLE`;
- `expired=false`;
- `minOsVersion=15.0`;
- `usesNonExemptEncryption=false`;
- upload time `2026-08-31T09:47:14-07:00`.

Direct build, beta-detail, prerelease-version, and beta-group inventory routes
remain unavailable to this key with security/relationship HTTP 403 responses.
This read path therefore proves continued processing validity, not TestFlight
group distribution or tester access.

The iPhone 14 Pro was unavailable to CoreDevice. The paired iPad mini 5 was
visible on the local network with Developer Mode enabled, but the app-inventory
request stopped at `kAMDMobileImageMounterDeviceLocked`; no app list or install
was read. No password or device code was requested. TestFlight installation
and the physical Apple matrix remain blocked.

## Decision

Public acquisition remains held. Google review/public propagation must be
rechecked after the store changes state. Apple needs an authenticated
TestFlight group/session plus an unlocked eligible device before build-6
runtime QA can begin. Neither surface contributes a Top-10 day at this cutoff.

## 05:55–06:19 follow-up

The fixed read-only public-rank checker completed again without writing a
daily or intraday snapshot. It preserved the canonical daily record and the
verified streak at `0/7`. The live check found Apple Weather category rank
`70`, Apple `weather` search rank `87`, Google Weather category rank `>30` in
all three fixed UZ profiles, and zero of five generic queries meeting the
required profile quorum. One auxiliary Apple query remained too sparse for a
diagnostic rank; every required goal surface was complete and failed.

An authenticated Play Console recheck then confirmed request `14` is still
`На рассмотрении`. The Uzbekistan Custom Store Listing targets Uzbekistan at
100% with no end date. Its read-only review form exposes two localized object
sets:

- en-US title `Nimbo: Ob-havo va prognoz`, localized Uzbek short and full
  descriptions, one icon, one feature graphic, six phone screenshots, and one
  Wear OS screenshot;
- ru-RU title `Nimbo: Погода и прогноз`, localized Russian short and full
  descriptions, one icon, one feature graphic, six phone screenshots, and one
  Wear OS screenshot.

The en-US and ru-RU feature-graphic, phone-screenshot, and Wear-object URL sets
are distinct, so these are separate localized creative sets rather than a
single inherited image set. Neither locale has 7-inch or 10-inch tablet
screenshots. The form was only navigated read-only; no field was changed and
its save action remained disabled. Managed publishing remains off and the
latest displayed publication remains August 27. The fixed logged-out UZ
product pages still returned the pre-review Uzbek/English and Russian
descriptions; their new aggregate sizes and hashes are recorded in
[google-play-public-propagation-2026-09-01.md](google-play-public-propagation-2026-09-01.md).

The Play global last-28-days overview now displayed 1.12 thousand device
impressions, 26 installations, 18 device first launches, 13 monthly active
devices, and 34.29% store-listing conversion. D7 retention remained
unavailable. These are global rolling-window observations, not an Uzbekistan
cohort, and they do not satisfy the UZ conversion or retention KPI.

The App Store Connect web route again returned `authResult=FAILED`; no
TestFlight group or tester claim is made. CoreDevice still showed the iPhone
14 Pro as unavailable. The paired iPad mini 5 appeared available, but an
app-inventory attempt acquired a tunnel and then immediately disconnected with
CoreDevice error 4000. No password, passcode, application list, install, or
runtime result was obtained. A separate public UZ lookup still exposed version
`1.0.1`, released `2026-08-24T05:16:14Z`, with one 5.0 rating and one iPhone
plus one iPad screenshot. Build 6 is therefore processed and eligible inside
App Store Connect, not publicly released.
