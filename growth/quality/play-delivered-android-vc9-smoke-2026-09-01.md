# Play-delivered Android vc9 smoke — 2026-09-01

Status: **PASS for the bounded replacement phone and widget scope**. The
complete Android/Wear physical gate remains blocked because no physical tablet
or paired Wear OS vc1000009 result exists.

All times are `Asia/Tashkent` (`UTC+05:00`). This record binds the physical
result to replacement source
`ba824beae5e72653e42af2b8b78286f61415e3ab` and exact retained phone AAB
`nimbo-phone-1.1.0-vc9.aab`, SHA-256
`0fd5ae542a71f8cccb1cbbd043ffef09df9f29a2c1c6642010cfcce579f00681`.
The protected pre-delivery byte check is recorded in
[release-artifact-full-verification-2026-09-01-hosted.md](release-artifact-full-verification-2026-09-01-hosted.md).

## Store delivery and installed identity

- Target: dedicated General Mobile 4G Dual, Android 7.1.1 / API 25,
  `gm4g_sprout`, serial `e76fd426`.
- The device began with Play-delivered `1.1.0 (8)`. The already accepted
  Internal Testing listing exposed an enabled `Обновить` action for
  `Nimbo (бета-версия для разработчиков)`.
- Google Play completed the preserved-data update at
  `2026-09-01 13:14:38` to `1.1.0 (9)`, `minSdk=24`, `targetSdk=36`.
  Package Manager identifies `com.android.vending` as the installer.
- The installed split set has these SHA-256 values:
  - `base.apk`: `30913427bf558b307125a15b403bd64c6e3937127aa1399fe46d578ab1b46a0d`;
  - `split_config.armeabi_v7a.apk`: `447b045c2b00a1a70d78d01e80a5f94ddc46ad0593ef41a3731166ce184cbf51`;
  - `split_config.xhdpi.apk`: `6b026e3fb825476a24765c9ce84a16ddf9d122f29490853aef026d2de56e316f`;
  - locale splits `ar`, `ru`, and `tr`:
    `f848d506d07cf935e11e89c218b1fea333fa3bb560a4b32a93c40dee70fcbacf`,
    `e1419ef00e8e810f222396983f2a2e8ecb32cafc5d1cae9c82c545eab1a47139`,
    and `6802a3f12a629f88e6af3a68267a12b5d67888078edb7e72c628a2a8c25f76ce`.
- APK Signature Scheme v3 verifies. The signer certificate SHA-256 is
  `99b8761f7efb2f0290e4a198e9465436c73bcad0dd619114126ff567ff80bf63`,
  matching the previously verified Google-managed Play App Signing identity.

## Bounded physical result

- The API-25 launcher renders the square Nimbo mark instead of the Android
  Studio template. The retained home-screen capture has SHA-256
  `02e391bc81cc029d5df22919932629e54e08dc7f99b38ce552f15ef7c43288d0`.
- A force-stop followed by launcher cold start retained the saved Tashkent
  state and rendered live weather, yesterday comparison, future context, and
  `Лучшее время для прогулки`. The process remained alive; the retained app
  capture has SHA-256
  `f91979489716dd806d7438083cfb962ab6e338cc970b831e205d0b9c523cd1f5`.
- The localized Share action opened Android's native resolver with Gmail,
  Quick Share, Drive, Copy, Messages, and Bluetooth destinations. No destination
  was selected.
- Manual refresh returned to the populated Tashkent forecast without an error.
- The preserved home-screen widget rendered Tashkent weather after the update;
  tapping it focused `uz.ganikhodjaev.weather/.MainActivity` and reopened the
  populated forecast.
- Bounded post-action log filters found no product fatal exception, Nimbo ANR,
  process death, SSL handshake, certificate-path, or trust-anchor failure.

## Boundary

This is exact replacement phone vc9 evidence for a preserved-data Play Internal
update on one physical API-25 phone. It does not prove a clean-install path,
physical tablet layout, TalkBack regression on vc9, paired Wear OS vc1000009,
post-delivery Android Vitals, production review/rollout, public availability,
or rank. Samsung API-36 user data was not modified. Google Play production
remains unchanged.
