# Surface freshness emulator evidence — 2026-08-29

Status: **PASS within the exact product-commit emulator scope**. Signing,
source-synced physical-device, paired-watch, and store-delivery gates remain
blocked.

## Product identity and contract

The tested product commit is
`ee7c36fbd83970e0bc44aa45681c78fc69bba155`.

Android widget and Wear OS share the same strict local payload contract:

- every required weather field must be present, finite, and within its defined
  range;
- a missing, partial, malformed, deleted, or more-than-five-minutes future-dated
  payload renders `Empty` and exposes no synthetic weather facts;
- a valid payload at or below six hours old renders `Fresh`;
- a valid payload older than six hours renders `Stale`, preserves the cached
  facts, and adds an explicit localized update-needed label;
- freshness is recomputed from local time when the surface renders or resumes;
  neither widget nor Wear performs a provider request.

The Apple widget and watch surfaces use the same Empty/Fresh/Stale behavior and
boundaries. Their deterministic contract coverage is recorded below; this
report does not substitute an Apple runtime screenshot or physical-device pass.

## Exact Android artifacts

| Surface | Debug APK SHA-256 | Boundary |
| --- | --- | --- |
| Android phone/widget | `e508f060b05f7560bcebbd508a75cda6876235393c259e3cfd0f1a1dc6135a3c` | Debug-signed emulator artifact only; not upload-signed or store-delivered. |
| Wear OS | `b1f20aa60117c36f5e041777c775dbebabc820f726141bd739a581ef55f35f58` | Debug-signed emulator artifact only; not Play-signed, paired, or physically installed. |

## Emulator environments

- Android widget: Android Emulator `36.6.11`, API 24 Google APIs ARM64,
  Pixel profile, `1080×1920`, `420 dpi`, using a real system-approved temporary
  `AppWidgetHost`.
- Wear OS: Android Emulator `36.6.11`, Wear OS 7 / API 37 ARM64, small round
  profile, `384×384`, `320 dpi`.
- Wi-Fi and mobile data were disabled for the scenario matrix. The retained
  payload is therefore deterministic local evidence rather than a live
  Open-Meteo request.

## Scenario results

| Surface | Empty | Fresh | Stale | Result |
| --- | --- | --- | --- | --- |
| Android widget | Localized open-app CTA only; no temperature, range, rain, or AQI | Tashkent, `24°C`, daily range, `Rain 10%`, and `AQI 42`; no stale label | The same cached facts plus the complete localized update-needed label | **PASS** |
| Wear OS round | Localized open-phone CTA only; no weather facts | Tashkent, `24°C`, daily range, `Rain 10%`, and `AQI 42`; no stale label | The same cached facts plus the complete localized update-needed label | **PASS** |

The Wear layout was additionally rendered in English, Uzbek, and Russian. The
long strings `Telefonda Nimbo’ni oching`,
`Saqlangan ob-havo · yangilash kerak`, and
`Сохранённая погода · нужно обновить` fit the round viewport without clipping.
No `FATAL EXCEPTION` appeared in the inspected logs.

## Retained visual evidence

| Scenario | File | SHA-256 |
| --- | --- | --- |
| Android widget Empty | [`android-widget-empty-api24.png`](evidence/surface-freshness-2026-08-29/android-widget-empty-api24.png) | `bb52ef22bd2b6885f00cd0865257a371bd8ae9fc39bb6be230f3090d93b61574` |
| Android widget Fresh | [`android-widget-fresh-api24.png`](evidence/surface-freshness-2026-08-29/android-widget-fresh-api24.png) | `562ae9955d05248fcdcfe5685df067f808093fefcae3bea7934744fd65b0f8ed` |
| Android widget Stale | [`android-widget-stale-api24.png`](evidence/surface-freshness-2026-08-29/android-widget-stale-api24.png) | `99b460f59144cf1f4a472a6540ae1a4ec1d4f41f655115b0cb5404a49edc651b` |
| Wear Empty | [`wear-empty-api37.png`](evidence/surface-freshness-2026-08-29/wear-empty-api37.png) | `8d5e4b678088be09e8989cf9c471b323c34b9eef4bce1fff97c467c5e8b3791f` |
| Wear Fresh | [`wear-fresh-api37.png`](evidence/surface-freshness-2026-08-29/wear-fresh-api37.png) | `1149702120f59179ec9cc94df069bd9706ba258ec14cc33c877b70f12067e61f` |
| Wear Stale | [`wear-stale-api37.png`](evidence/surface-freshness-2026-08-29/wear-stale-api37.png) | `83da1ca9677077ed1184c41d9733a0855d7c931294550ed89c472b613c294507` |

## Automated and Apple simulator evidence

- A clean Gradle gate completed `276` actionable tasks and parsed `232` test
  executions with zero failures: shared iOS Simulator `102`, shared Android
  host `107`, Android app `13`, and Wear `10`.
- The dedicated Swift surface suite passed `18/18` tests.
- Release arm64 simulator builds passed for the iOS app with widget and for the
  watch app. The exact executables and their matching dSYM identities remain
  documented in
  [`release-artifact-source-sync-2026-08-29.md`](release-artifact-source-sync-2026-08-29.md).
- The existing Apple linker warning remains: an ICU object targets iOS
  Simulator 18.5 while the product deployment floor is iOS 15.0. A successful
  simulator link does not erase that compatibility boundary.

## Non-transferable boundary

This evidence does not prove upload/distribution signing, install-over-public,
physical launcher behavior, Bluetooth or phone-watch handoff, real background
cadence or battery behavior, provider-network behavior, TalkBack or VoiceOver,
store processing, review, rollout, or end-user availability. The two original
physical Android devices were not modified. Temporary emulator hosts, AVDs,
userdata, and processes were removed after capture.
