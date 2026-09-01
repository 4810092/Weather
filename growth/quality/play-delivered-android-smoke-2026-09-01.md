# Play-delivered Android smoke — 2026-09-01

Status: **PASS for the bounded Play-delivered phone scope** and **PASS for
Wear Internal tester activation**. The combined Android physical gate remains
**BLOCKED** because physical tablet/widget, paired Wear OS, background-retry,
and post-delivery vitals evidence are incomplete.

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
- At Android `font_scale=1.3`, a fresh Russian onboarding render remained
  vertically scrollable with readable city actions. Quick-city Tashkent then
  rendered the current conditions, yesterday comparison, and Best Time card
  without clipping the primary value or action controls.
- At `04:41–04:43`, the system Wi-Fi control was switched off and independently
  confirmed by `wifi_on=0` plus a direct `1.1.1.1` ping failing with
  `Network is unreachable`. A forced cold start of the Play-installed package
  retained the saved Tashkent forecast and Best Time card. Manual refresh kept
  those values and rendered the localized message `Не удалось обновить.
  Показана сохранённая погода.`
- Wi-Fi was then restored through the system UI. `wifi_on=1` and a direct
  `1.1.1.1` ping both passed before refresh. The next manual refresh removed the
  saved-weather failure message while retaining the live forecast surface.
  Airplane mode remained off throughout the counted path.
- Filtered process evidence contained no Nimbo fatal exception or ANR for the
  tested paths.

Two earlier attempts to create a physical offline condition were deliberately
not counted. Android 7.1 denied the airplane-mode broadcast, and the subsequent
radio command did not produce a disconnected connectivity state. The final
system-UI Wi-Fi transition above is the counted Play-delivered offline/recovery
result because both the radio state and direct-IP reachability were checked on
each side of the app behavior. The three local captures have SHA-256 values
`7f16c8ed42b753e82fece5a58a86c7a869193f5f60d682ca5907150cddf9d40a`,
`45d37780829f7147a9f14502e062caac31ed9260ac606471e18719c7bfae8e30`,
and `9611b761238cb1ce41570f083ffd31685a5bf502e7ae11779d494cd9eea6a976`.
The raw device captures stay outside Git under the repository's aggregate-only
evidence policy.

## Accessibility boundary

The installed Nimbo build exposes text nodes for the live forecast and explicit
content descriptions for share, refresh, and change-location actions. The
device's installed TalkBack `12.2.0.442723463` update could not establish a
valid service on Android 7.1 because it references API-26-only classes. That
first attempt remains excluded.

The device also contains its signed system TalkBack `5.0.4`, which targets API
24. Before temporarily removing only the incompatible update, both update APKs
were pulled and hashed. With system TalkBack active, `dumpsys accessibility`
reported a live `TalkBack` service with spoken, haptic, and audible feedback,
`touchExplorationEnabled=true`, and the Nimbo application window focused.

A cold Nimbo launch followed by hardware-key focus traversal produced visible
green screen-reader focus on the forecast surface and then on all three primary
controls. The focused bounds and nested semantics matched:

- `[352,80][448,176]` → `Поделиться погодой`;
- `[464,80][560,176]` → `Обновить`;
- `[576,80][672,176]` → `Сменить место`.

TalkBack/Google TTS emitted AudioTrack activity during each captured transition;
no audio transcript is claimed. Nimbo remained in `MainActivity`, and the
filtered log contained no Nimbo fatal exception or ANR. The four local capture
SHA-256 values are
`5fed99234380b0998dac5ff0feccb3ea9e146a1b681f6adc008e3376e450798b`,
`3beab412813904a664668c04f6c44e0ce70b871697a570bc2f064d81a2beb9e1`,
`a20cb27693b489b47f437a2a1488caea128acb60f8535fdeb3edd3a125b87e7c`,
and `c72cb9e79c505dc7e045883fa8eee5a7f740b591032cc92fb94955711d3f6b7a`.
Raw captures stay outside Git under the aggregate-only evidence policy.

After the counted pass, accessibility and the temporary TTS default were
disabled/deleted, `touchExplorationEnabled=false`, and `font_scale=1.0`. The
original TalkBack 12.2 split set was reinstalled byte-for-byte: base
`e9f1591c7cba627d85edfc90467a063ca330d15db708b1ff39ab2d931da9b88d`
and ARM split
`28dfdf41ba10a07c01e29390832b198ddab777b96fb359c5d8cbcb1b38d721fc`.
Nimbo remained Play-installed `1.1.0 (8)` with installer
`com.android.vending`, Wi-Fi on, and airplane mode off. This closes the bounded
API-25 TalkBack path for the Play-delivered phone package; it does not prove
newer-OS screen-reader, tablet, widget, background, or Wear behavior.

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
25. The separate `font_scale=1.3` onboarding/live-forecast pass and the
system-UI-proven offline/cache/recovery path also succeed. Still missing are
background retry, physical tablet/widget coverage, paired physical Wear OS
coverage, and post-delivery crash/ANR rates. The connected Samsung API 36
device contains user data and was not modified. No production review, rollout,
public availability, ranking improvement, or crash-gate closure follows from
this internal-test result.
