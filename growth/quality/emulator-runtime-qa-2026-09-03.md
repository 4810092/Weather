# Emulator/simulator runtime QA — 2026-09-03

## Policy and boundary

On 2026-09-03 the product owner explicitly made emulator/simulator execution
sufficient for Nimbo runtime QA. The connected General Mobile Android handset is
a disposable test device and may be uninstalled, cleared, or reset for Nimbo QA;
the connected Samsung remains user-data-bearing and was not modified.

The existing gate IDs `android_physical_smoke`, `ios_physical_smoke`, and the
legacy manifest field `physical_qa_evidence` are retained for schema and history
compatibility. From this checkpoint they mean required runtime QA under the
owner-approved emulator/simulator policy; they do not claim that a physical
tablet or watch was used.

Runtime QA passing does not prove store delivery, signing identity, production
crash/ANR or Vitals metrics, review, rollout, public availability, or rank. Those
remain separate fail-closed gates.

## Candidate and source binding

- Product/build-input authority:
  `052d12c7dfa6411428d85205d9568462d20ff87d`.
- Current `master` product inputs in `androidApp`, `wearApp`, `shared`, `iosApp`,
  `gradle/libs.versions.toml`, and `settings.gradle.kts` are byte-identical to
  that authority (`git diff --quiet` returned `0`).
- Protected candidate artifacts remain independently byte-verified:
  - phone `1.1.0 (11)`:
    `034aa0a732e0a671c341e6714162a2d22c95d06435aa327bd17b1d7b3da2f9ac`;
  - Wear OS `1.1.0 (1000011)`:
    `48a713d298be12552f08995b7cff3166df0f4ab173c62612854598eb93dcab7a`;
  - Apple `1.1.0 (9)`:
    `a57674d7d467474a0697fb39c834a9829f53e68ddb9d4480168bf2dcf3f7ac29`.
- Hosted CI run `33653344467` passed current-source Android API 24 phone, API
  36 phone, API 36 tablet Compose UI, Android/shared, iOS shared tests,
  glanceable-surface tests, and unsigned Apple build jobs.

## Android runtime result

- The existing exact-AAB-derived, upload-key-signed General Mobile API 25 phone
  smoke remains valid supporting evidence for phone launch, live provider data,
  Share chooser, refresh, widget render/open, cleanup, and crash/ANR filters.
- `:wearApp:testDebugUnitTest` and `:wearApp:assembleDebug` passed from the
  current source authority.
- A clean Wear OS XL Round API 37 emulator install ran Nimbo Wear
  `1.1.0 (1000011)` in English, Russian, and Uzbek. All three rendered Tashkent,
  temperature, high/low, precipitation, and AQI. Ten cold launches returned ten
  distinct live PIDs (`3666` through `4005`) with zero matching fatal-exception
  or ANR records.
- Debug APK SHA-256:
  `8dfdcae47e7d10806dce6f321682d8dfb5591caa8d6760216ac9b9c472b5f6b9`.

Retained evidence:

- `growth/quality/evidence/runtime-emulator-current-2026-09-03/wear/nimbo-wear.png`
  — `62260a7bfcd37d543d7872693730846817844954e2b31155ea21b39c9f697f4a`;
- `growth/quality/evidence/runtime-emulator-current-2026-09-03/wear/nimbo-wear-ru.png`
  — `a7b2da4c3a2a93c14e755d4a70346641fcfcebbe443bbaef9fb7ac79bd9f48e1`;
- `growth/quality/evidence/runtime-emulator-current-2026-09-03/wear/nimbo-wear-uz.png`
  — `924c9db045d88b8aa7c9fe96a64aa4d3f97e9a320ee5969a6339c9de305595dc`.

## Apple runtime and iPad Share result

- A source-current Release simulator build produced Nimbo `1.1.0 (9)` and its
  widget for an iPad Pro 11-inch (M4), iOS 18.1 simulator. The app launched and
  rendered live weather; the minimum deployment target remained iOS 15.0.
- An external XCUITest drove the installed Nimbo bundle without rebuilding or
  modifying the app: it launched the app, found and tapped `Share weather`,
  waited two seconds, asserted that Nimbo was not terminated, and retained a
  screenshot. The final run passed `1/1` with zero failures in 10.138 seconds.
- The simulator unified log at `2026-09-03 13:56:01.814 +05:00` records
  `[com.apple.ShareSheet:ShareSheet] UIAVC: view did appear` for the Nimbo
  process. No Nimbo simulator crash report was created during the test.
- The same source-current Release build produced NimboWatch `1.1.0 (9)`, which
  installed and rendered Tashkent weather on an Apple Watch Series 11 watchOS
  26.5 simulator. Ten cold launches returned ten distinct live PIDs (`41893`
  through `41961`).

Retained evidence:

- `growth/quality/evidence/runtime-emulator-current-2026-09-03/apple/nimbo-ipad-launch.png`
  — `e56aa8564c68705b25ff28c6ad5bd7348fd90b065e02729692a6bb118c4cd782`;
- `growth/quality/evidence/runtime-emulator-current-2026-09-03/apple/nimbo-ipad-share-sheet.png`
  — `ebc259b00707f2064a8b403168fc749f460b4f579085ac2829a3110c2a821bd5`;
- `growth/quality/evidence/runtime-emulator-current-2026-09-03/apple/nimbo-watch-launch.png`
  — `7fa6cf5298cdb1c0d7f7c49c777e2dba96a606e045a2012eeb58e6bce8214d35`.

The retained XCUITest screenshot captures the application surface because the
share content is hosted by the simulator sharing service; the system-log
`UIAVC: view did appear` event is the direct presentation proof. This closes the
build-9 iPad Share regression under the approved simulator policy, but it does
not close `ios_crash_gate`: authenticated public crash-free-session evidence
for the released build is still unavailable.
