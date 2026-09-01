# Play-delivered Android vc10 smoke — 2026-09-01

Status: **PASS for the bounded current phone and widget scope**. The complete
Android/Wear physical gate remains blocked because no current physical tablet
or paired Wear OS vc1000010 result exists.

All times are `Asia/Tashkent` (`UTC+05:00`). This record binds the physical
result to product source
`8fc43b48b65d17b3339663549cd86208f62f6bb7` and exact phone AAB
`nimbo-phone-1.1.0-vc10.aab`, SHA-256
`c11bc62221c11a16b1d6614aae2060af60ca7b98ad989e68dc5f87c224bbcd89`.

## Store delivery and installed identity

- Target: dedicated General Mobile 4G Dual, Android 7.1.1 / API 25,
  `gm4g_sprout`. The Samsung API-36 device containing user data was not
  modified.
- Google Play Internal exposed an enabled `Обновить` action for
  `Nimbo (бета-версия для разработчиков)` and completed the preserved-data
  update from vc9 to `1.1.0 (10)` at `2026-09-01 19:01:05`.
- Package Manager reports `minSdk=24`, `targetSdk=36`, and
  `installerPackageName=com.android.vending`.
- The installed split set has these SHA-256 values:
  - `base.apk`: `8661ffea6d47d01b6ed071ce023b9903aacf7303dad1499041d17cdd16a009a1`;
  - `split_config.armeabi_v7a.apk`: `47f1084cf16c8720b106441af6cc4c9ed949f7851cdb5ec54fba263042cb34fb`;
  - `split_config.xhdpi.apk`: `9830818dd1302215205d13534fa9ab9204f71ef832efdbda9419ada20460ea4b`;
  - locale splits `ar`, `ru`, and `tr`:
    `dce53c16b18a8ec34995e4f9004fdedb4891b549231ee0423446e9f1238effe7`,
    `a9c6001282c45c1806f39181a45e245c21477958537f1db3fb70e00267be8b81`,
    and `003f78af78a93e9179536f609664240200544c743937c198c67424b0f2055cbd`.
- APK Signature Scheme verification reports Google Play App Signing
  certificate SHA-256
  `99b8761f7efb2f0290e4a198e9465436c73bcad0dd619114126ff567ff80bf63`,
  matching the previously verified delivery identity.

## Bounded physical result

- A force-stop followed by launcher cold start retained the saved Tashkent
  state and rendered live weather, yesterday comparison, future context, and
  `Лучшее время для прогулки`. The Nimbo activity remained resumed.
- The localized Share action opened Android's native resolver. No destination
  was selected.
- Manual refresh returned to the populated Tashkent forecast without an error.
- The preserved home-screen widget rendered `Ташкент`, `28°C`, high/low,
  `Осадки 0%`, and AQI. Tapping it focused
  `uz.ganikhodjaev.weather/.MainActivity` and reopened the populated forecast.
- Bounded log filters found no product fatal exception, Nimbo ANR, process
  death, SSL handshake, certificate-path, or trust-anchor failure.

## Boundary

This proves one preserved-data Play Internal update and bounded runtime path on
one physical API-25 phone. It does not prove clean install, physical tablet,
TalkBack regression, paired Wear OS vc1000010, post-delivery Android Vitals,
production rollout, public availability, or rank.
