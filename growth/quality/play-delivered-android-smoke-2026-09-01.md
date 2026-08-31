# Play-delivered Android smoke — 2026-09-01

Status: **PASS for the bounded Play-delivered phone scope** and **PASS for
Wear Internal tester activation**. The combined Android physical gate remains
**BLOCKED** because physical tablet/widget, proven-offline Play-delivered phone,
paired Wear OS, accessibility, and post-delivery vitals evidence are incomplete.

All times are `Asia/Tashkent` (`UTC+05:00`). Production was not changed.

## Artifact and store authority

- Product source revision:
  `2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652`.
- Exact retained phone AAB: `nimbo-phone-1.1.0-vc8.aab`, SHA-256
  `d4a90676f32745ea314b50ced2c9955e86923589534a1a7654ac6f1207e88a62`.
- Phone Internal track: `4700083514281298386`.
- Exact retained Wear AAB: `nimbo-wear-1.1.0-vc1000008.aab`, SHA-256
  `e76d685b20e86f8878be7c9a1a59ac6edb5781ec8e61d5ecd36feb52ddc1cccf`.
- Wear Internal track: `4699242452771231163`.

The General Mobile device accepted the phone Internal invitation. The Google
opt-in page then reported `You’re a tester for Nimbo
(uz.ganikhodjaev.weather)`. After normal propagation, Google Play changed from
an initial unsupported result to the internal-test listing
`Nimbo (бета-версия для разработчиков)` with an enabled install action.

At `2026-09-01 02:59:12`, Google Play installed package
`uz.ganikhodjaev.weather` as version `1.1.0 (8)`, `minSdk=24`,
`targetSdk=36`. Package-manager evidence identifies
`com.android.vending` as the installer. The selected split set was:

- `base.apk` — SHA-256
  `029eeb0fb091b3025a21ecec8c2e19dec61952915d5185a689f584887342e3f0`;
- `split_config.armeabi_v7a.apk` — SHA-256
  `a02dd462e3b7bd69db5eb2c38fb0adbae5e414383107c147e90675a1d2897902`;
- `split_config.xhdpi.apk` — SHA-256
  `17e7ca1014d7f70906c1d361b6fd8dc4d5ac342c5b7cb25058140d8026cf4515`;
- locale splits `ar`, `ru`, and `tr`, with SHA-256 values
  `fe0149aa12f1208bdfc0c6df33536c4580df674bac3838510060def9d8fa0e3d`,
  `8d00cc705e29ed1873f74d6fd355dc34812d3834bd686a88aa754a0820017404`,
  and `1323bf34c8bd0de30272b2f7ff75a0007e571c1dc12fa4ef0ed499ea5706c5b7`.

The installed base verifies with APK Signature Scheme v2 and v3. Its signer
certificate SHA-256 is
`99b8761f7efb2f0290e4a198e9465436c73bcad0dd619114126ff567ff80bf63`,
matching the previously verified Google-managed Play App Signing identity.
This distinguishes the installed package from the upload-key-signed local
pre-delivery smoke.

## Physical phone result

- Target: dedicated General Mobile 4G Dual (`gm4g_sprout`, serial
  `e76fd426`), Android `7.1.1` / API 25, 32-bit ARM, 720 x 1280, Russian locale.
- A forced cold start completed successfully in 1,543 ms and rendered the
  localized first-run screen without requesting location.
- Selecting the quick city `Ташкент` rendered a live forecast, current
  conditions, yesterday comparison, and `Лучшее время для прогулки`.
- The share action opened the native Android chooser. No destination was
  selected and no message was sent.
- Filtered process evidence contained no Nimbo fatal exception or ANR for the
  tested paths.

Two attempts to create a physical offline condition were deliberately not
counted. Android 7.1 denied the airplane-mode broadcast, and the subsequent
radio command did not produce a disconnected connectivity state. The cached
screen remained visible, but without a proven network outage it is not valid
offline evidence. The earlier exact-AAB-derived offline pass remains regression
evidence only and does not replace a Play-delivered offline pass.

## Wear Internal result

The existing four-account `License testers` list was selected for Wear
Internal and saved. Play Console returned `Changes updated`; a fresh recheck
then reported the Wear OS test as `Активно` with exact release
`Nimbo Wear 1.1.0 (1000008) — UZ growth QA`. The opt-in page reports the
current Google account as a Nimbo tester.

This is tester-access and active-track evidence. No Play-delivered physical
watch install, cold start, phone handoff, forecast transfer, or paired-device
result is claimed.

## Remaining boundary

The bounded phone pass proves Google Play delivery, split selection, the
Google-managed signing identity, a clean first run, a live Tashkent forecast,
the primary Best Time value, native share dispatch, and process health on API
25. Still missing are the Play-delivered phone offline/recovery path, large
text/TalkBack/background retry, physical tablet/widget coverage, paired
physical Wear OS coverage, and post-delivery crash/ANR rates. The connected
Samsung API 36 device contains user data and was not modified. No production
review, rollout, public availability, ranking improvement, or crash-gate
closure follows from this internal-test result.
