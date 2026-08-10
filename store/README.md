# Store release material

This directory contains version-controlled metadata, declarations, artwork, and
production-UI screenshots used for the Nimbo 1.0 release. Store consoles remain
the final source for submission state; this directory is the reviewable input.

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

The committed set contains five 1080 × 1920 Android phone screenshots, four
2560 × 1440 Android large-screen screenshots, one 1320 × 2868 App Store iPhone
screenshot, and one 2064 × 2752 App Store iPad screenshot. All were captured
from release production code with a populated local database; no UI was invented.

`scripts/check_store_metadata.py` validates locale coverage and text limits.
`scripts/check_store_assets.py` validates the expected files, dimensions, formats,
and alpha restrictions. Device frames must not obscure the app.
