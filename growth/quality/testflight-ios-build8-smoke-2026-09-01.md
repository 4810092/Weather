# TestFlight iOS build 8 physical smoke — 2026-09-01

Status: **PASS for the bounded current iPhone and share-fix scope**. The full
iOS physical/crash gate remains blocked by the missing current iPad, visible
widget, physical watch, iOS 15, diagnostic, and post-delivery crash-free
evidence.

All times are `Asia/Tashkent` (`UTC+05:00`). No tester email address, invite
token, invitation code, device serial, or private raw store export is retained.

## Store and installed identity

- App Store Connect build ID:
  `9696b8c2-d076-4596-af20-b8a5214aaf01`.
- Candidate: `Nimbo Weather 1.1.0 (8)` from source
  `8fc43b48b65d17b3339663549cd86208f62f6bb7`; exact IPA SHA-256
  `6aff05fc50a0e1546a196cc8f7f9139bfb87f8e89c0dcda7c91dc1ddb1defac4`.
- App Store Connect reports upload status `Завершено`, TestFlight status
  `Готово к отправке`, and one internal group containing two
  owner-controlled testers.
- TestFlight exposed exact `1.1.0 (8)` as an update. After installation,
  `devicectl` inventory reported bundle `uz.ganikhodjaev.weather`, version
  `1.1.0`, bundle version `8`, and the installed `Nimbo.app` path on the
  connected iPhone 14 Pro.

## Bounded physical result

- First launch after the TestFlight update completed without a visible error
  and rendered a live Tashkent forecast at `28°`, including current condition,
  yesterday comparison, future context, the 24-hour timeline, and Best Time
  Outside.
- Manual refresh returned to the populated forecast.
- The native share sheet opened. Its preview contained
  `Ташкент: 28°, вероятность дождя 0%...`; copying the generated payload
  produced exactly:

  ```text
  Ташкент: 28°, вероятность дождя 0% — Nimbo
  Скачайте Nimbo для следующей прогулки:
  https://apps.apple.com/app/id6799886897
  ```

  This proves one literal percent sign, the localized CTA, and the canonical
  platform URL with no coordinates, identifiers, fragment, or analytics
  parameters.
- Post-action process inventory contained both `Nimbo.app/Nimbo` and the
  bundled `NimboWidget.appex/NimboWidget` processes. No visible crash occurred.

## Fail-closed boundary

The connected iPad remains on historical build 7. The paired Apple Watch has
Developer Mode disabled, so current watch bundle identity and runtime could not
be inspected through `devicectl`; no physical watch launch is claimed. A
running widget extension does not prove visible widget render/open. No iOS 15
device result, crash diagnostic/symbolication, post-delivery crash-free metric
window, production submission, review, public availability, or rank effect is
claimed.
