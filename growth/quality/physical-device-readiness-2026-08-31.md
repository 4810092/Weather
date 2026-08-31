# Physical device readiness — 2026-08-31

Status: **PARTIAL**. The exact Android phone candidate now has bounded local
physical evidence. Store-delivered Apple and full Android/Wear matrices remain
blocked.

## Android

| Target | State | Safe use |
| --- | --- | --- |
| General Mobile 4G Dual, Android 7.1.1 / API 25 | Dedicated phone; returned to package-absent state after the vc8 smoke | Clean Play Internal phone install when credentials become available |
| Samsung SM-S908E, Android 16 / API 36 | Contains user data and a debuggable Nimbo 1.1.0 (8) with a different installed APK identity | Do not overwrite; a Play-signed update may require uninstall and data loss |
| Android tablet | No physical ADB target present | Blocked |
| Wear OS | No physical ADB target present | Blocked |

## Apple

| Target | State | Safe use |
| --- | --- | --- |
| iPhone 14 Pro, iOS 26.6.1 | Paired, booted, Developer Mode enabled; public Nimbo 1.0.1 (4) installed | TestFlight update after exact IPA processing |
| iPad mini 5, iPadOS 26.6 | Paired, booted, Developer Mode enabled; Nimbo absent | Fresh TestFlight install after exact IPA processing |
| Apple Watch Series 5, watchOS 10.6.2 | Compatible with minimum watchOS 10 and paired, but Developer Mode is disabled and the developer tunnel is disconnected | Blocked until watch readiness is restored |

The exact Apple `Nimbo.ipa` is App Store-profile signed and therefore cannot be
installed directly with `devicectl`. It must be uploaded unchanged and installed
through TestFlight. The phone and Wear AABs likewise require Play delivery for
app-signing-key runtime proof. Direct local installation is not a substitute for
those store-delivery checks.
