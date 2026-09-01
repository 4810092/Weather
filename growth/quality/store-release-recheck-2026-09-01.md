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
