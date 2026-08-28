# Store release material

This directory contains version-controlled metadata, declarations, artwork,
production-UI screenshots, and draft growth creatives for Nimbo. Store consoles
remain the final source for submission state; this directory is the reviewable
input and nothing here is published automatically.

`metadata.json` uses schema version 2 (documented by
`metadata.schema.json`). It separates reusable locale copy from platform and
storefront listings, Custom Store Listing / Custom Product Page drafts,
creative-set references, experiment gates, and marketing/support/privacy URLs.
Experiments stay `not-started` until the recorded weekly-visitor gate is met.
The canonical public URLs are `https://nimbo.uz/`,
`https://nimbo.uz/support/`, and `https://nimbo.uz/privacy/`.

## Required image formats

- Google Play icon: 512 × 512, 32-bit PNG, at most 1 MB.
- Google Play feature graphic: 1024 × 500, JPEG or 24-bit PNG without alpha.
- Google Play screenshots: 2–8 per device type; large-screen images are 1080–7680
  px and 16:9 or 9:16.
- App Store: 1–10 screenshots. The primary iPhone 6.9-inch set accepts
  1320 × 2868, and the required iPad 13-inch set accepts 2064 × 2752.

Requirements were verified against the official
[Google Play asset specification](https://support.google.com/googleplay/android-developer/answer/9866151?hl=en)
and [Apple screenshot specification](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications/)
on August 10, 2026.

The committed set contains 35 Android phone screenshots: five images each for
English, Russian, and Uzbek, plus two localized images for each of the other ten
app languages. It also
contains four English 2560 × 1440 Android large-screen screenshots and one
480 × 480 Wear OS screenshot captured from the current watch app. The Apple
set adds one 416 × 496 Apple Watch screenshot, plus one
1320 × 2868 App Store iPhone and one 2064 × 2752 App Store iPad screenshot for
each of the 13 app languages. All were captured from current production UI with
a populated local database; no UI was invented.

Google Play and App Store Connect do not offer Uzbek as a product-page locale.
The UZ Google custom-listing draft therefore records Uzbek audience copy with an
`en-US` store-locale fallback, alongside a separate Russian localization. The
UZ App Store Custom Product Page draft uses the same explicit fallback. This
mapping is data for a manual console update; the installed app continues to use
its complete Uzbek localization.

## Growth creative set

`creative-sets/growth-2026-08.json` is the source manifest for six captioned
phone creatives in English, Russian, and Uzbek for both stores. Every composition
uses the checked-in production phone/watch captures. The renderer only crops,
scales, frames, and captions those captures; it does not generate, translate, or
retouch UI.

The current English, Russian, and Uzbek Android captures visibly prove the
10-day, air-quality, Best Time, and offline surfaces used by Google Play
creatives. App Store captions remain generic where equivalent Apple captures
are absent. The home-screen-widget story is deliberately excluded until a
matching production capture exists. This keeps the asset pipeline fail-closed
against unsupported marketing claims and prevents a fixed English source from
being reused inside localized Google creatives.

The short captioned video is specified in
[`previews/growth-2026-08/storyboard.md`](previews/growth-2026-08/storyboard.md).
No video is committed yet: Apple requires genuine in-app footage, and the
offline scene plus the release candidate must pass device QA before capture.
Publishing the Google YouTube preview or uploading an Apple preview remains an
explicit external action.

Rebuild with the pinned Pillow/font renderer:

```sh
python3 scripts/build_store_creatives.py
```

The command creates 36 opaque PNG creatives under
`store/creatives/growth-2026-08/` and refreshes the 1024 × 500 Uzbek Google Play
feature graphic. Re-running it with identical inputs produces identical files;
renderer or font drift stops the build.

`scripts/check_store_metadata.py` validates schema version, locale coverage,
platform/storefront relationships, approved UZ/RU copy, text limits, experiment
gates, creative references, and HTTPS support URLs. `scripts/check_store_assets.py`
validates source provenance, six-story locale coverage, expected files,
dimensions, formats, opacity, and the fail-closed claim exclusions. Device frames
must not obscure the app.
