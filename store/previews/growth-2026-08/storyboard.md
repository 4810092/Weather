# Nimbo short preview storyboard

Status: **capture blocked by release QA**. This document is the approved edit
plan, not an uploadable preview. Apple requires an app preview to use captured
footage of the app itself, so the checked-in static screenshots must never be
turned into a slideshow and presented as a finished preview.

The machine-readable timing, candidate identities, localized SRT captions,
expected output names, hash fields, and blocking gates are in
[`manifest.json`](manifest.json). `scripts/check_store_previews.py` keeps the
package fail-closed until genuine same-platform recordings and strict JSON
evidence replace the null master fields.

The manifest uses canonical IDs from `growth/quality/gates.json`; its blocker
set must exactly equal the required non-pass preview gates. Candidate version,
Apple build, and Google version code must also match
`store/upload-manifest-1.1.0.json`. A ready package additionally requires
verified-current artifact hashes plus signing and physical-QA evidence.

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
- A `ready` manifest must have no blocking gates. Apple outputs must keep the
  exact `.mov` suffix and Google outputs the exact `.mp4` suffix. Renaming an
  SRT, screenshot, or another asset is never sufficient: every output must be a
  genuine ISO-BMFF container with non-empty `ftyp`, `moov`, and `mdat` boxes.
  Validation also uses `ffprobe` and a complete `ffmpeg` decode to require one
  real video stream and measure its codec, duration, dimensions, frame rate,
  and bitrate. Container-box names or evidence text alone cannot make a master
  ready.

## Required evidence beside each final file

Each master points to a `.json` evidence file with exactly the fields below; no
free-form or omitted fields are accepted. `candidate_identity` must exactly
match the Apple or Google identity in the manifest. The two hashes must match
the master entry, the output hash must also match the video bytes, and duration,
resolution, codec, frame rate, and bitrate must match the measured media stream;
the applicable values must also satisfy `export_contract`.
Record `fps` from the probed average frame rate and `bitrate_kbps` as the nearest
integer to the stream bitrate divided by 1000 (falling back to the container
bitrate only when the stream value is absent).

```json
{
  "schema_version": 1,
  "platform": "apple",
  "locale": "uz-UZ",
  "candidate_identity": {"version": "1.1.0", "build": "6"},
  "device": "iPhone 15",
  "os": "iOS 18.6",
  "capture_date": "2026-08-29",
  "source_recording_sha256": "64 lowercase hexadecimal characters",
  "output_sha256": "64 lowercase hexadecimal characters",
  "duration_seconds": 20,
  "resolution": {"width": 886, "height": 1920},
  "codec": "h264",
  "fps": 30,
  "bitrate_kbps": 11000,
  "reviewer": "QA reviewer name"
}
```

For Google evidence, use `platform: "google"`, the matching locale, Google
candidate identity, Android device/OS, and a portrait resolution. Final videos
and evidence are intentionally absent until genuine capture and approval are
complete; while they are absent the manifest remains `capture-blocked` with
null hashes and evidence paths.
