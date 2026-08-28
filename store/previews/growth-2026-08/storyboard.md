# Nimbo short preview storyboard

Status: **capture blocked by release QA**. This document is the approved edit
plan, not an uploadable preview. Apple requires an app preview to use captured
footage of the app itself, so the checked-in static screenshots must never be
turned into a slideshow and presented as a finished preview.

## 20-second cut

| Time | Genuine in-app action | English caption | Russian caption | Uzbek caption |
| --- | --- | --- | --- | --- |
| 0–5 s | Fresh onboarding; select Toshkent without requesting location | Find the best time to go outside | Найдите лучшее время выйти на улицу | Tashqariga chiqish uchun eng yaxshi vaqtni toping |
| 5–10 s | Forecast appears; show the yesterday comparison | Compare now with yesterday | Сравните сейчас со вчерашней погодой | Hozirgi ob-havoni kechagi bilan solishtiring |
| 10–15 s | Scroll the real 24-hours-ago / now / 24-hours-ahead timeline | 24 hours ago · now · 24 hours ahead | 24 часа назад · сейчас · 24 часа вперёд | 24 soat oldin · hozir · 24 soat keyin |
| 15–20 s | Cold-launch the verified cached forecast while offline | Keep the last forecast offline | Последний прогноз доступен офлайн | So‘nggi prognoz oflayn ham mavjud |

The offline scene is included only after the candidate passes the documented
device offline/cache smoke. If it does not pass, replace that scene with genuine
city search footage and the caption “Search any city / Найдите любой город /
Istalgan shaharni toping”.

## Capture and export contract

- Capture a clean production-candidate build on iPhone and Android. Do not show
  notifications, accounts, exact coordinates, advertising IDs, or analytics
  parameters.
- Keep every frame inside the app. Do not use fabricated UI, static screenshot
  animation, store badges, device frames, or footage from another platform in
  the Apple preview.
- Record separate English, Russian, and Uzbek app sessions so captions and the
  visible UI use the same language.
- Apple master: portrait 886 × 1920, 15–30 seconds, H.264 progressive at a
  10–12 Mbps target, no more than 30 fps. If audio is present, use enabled AAC
  stereo at 44.1 or 48 kHz. See the official
  [App preview specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/app-preview-specifications/).
- Google master: real Android footage with the same story. Uploading it to an
  unlisted/public YouTube URL and adding that URL in Play Console are external
  publication actions and require action-time approval.
- Before export, recheck every visible value and claim against the candidate,
  then run the device smoke and store-asset checklist. Preview upload remains
  blocked while the iOS crash gate or Open-Meteo promotion gate is open.

## Required evidence beside each final file

Record the candidate version/build, platform/device/OS, capture date, locale,
source recording SHA-256, output SHA-256, duration, resolution, codec, frame
rate, bitrate, audio layout, and the QA reviewer. Final videos are intentionally
absent from the repository until genuine capture and approval are complete.
