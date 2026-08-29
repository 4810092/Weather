# Store release material

This directory contains version-controlled metadata, declarations, artwork,
production-UI screenshots, and draft growth creatives for Nimbo. Store consoles
remain the final source for submission state; this directory is the reviewable
input and nothing here is published automatically.

`metadata.json` uses schema version 2 (documented by
`metadata.schema.json`). It separates reusable locale copy from platform and
storefront listings, Custom Store Listing / Custom Product Page drafts,
creative-set references, experiment gates, and marketing/support/privacy URLs.
Its `product.release` identifies the coordinated candidate described by the
repository, not the currently public store versions; the validator requires it
to match the Android, Wear OS, and Apple source versions.
`upload-manifest-1.1.0.json` resolves each store surface to its exact locale,
metadata, creative, and artifact source-sync state. It intentionally remains
`draft-blocked`: current phone vc8, Wear `1000008`, and Apple build 6 have null
upload-candidate hashes, signing, and physical-QA evidence until exact-source
signed artifacts and their matching QA exist. Its full `source_revision` is
shared with the release/source gate; `check_release_qa_matrix.py` fails if that
revision differs from the current product/build inputs or if either authority
drifts. The older signed phone vc7, signed Wear `1000008`, and Apple build 5
bytes remain historical candidates because their source predates the current
revision. This is a preflight inventory, not evidence of a console upload.
Experiments stay `not-started` until the recorded weekly-visitor gate is met.
The canonical public URLs are `https://nimbo.uz/`,
`https://nimbo.uz/support/`, and `https://nimbo.uz/privacy/`.

## Required image formats

- Google Play icon: 512 × 512, 32-bit PNG with alpha, at most 1 MB.
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
The publishable Google package therefore contains one Custom Store Listing,
`google-play-uz-country-listing`, targeting country `UZ` only. It declares
`en-US` as the default store locale and maps it to Uzbek audience copy/assets
(`audience_locale: uz-UZ`), with a separate `ru-RU` locale. Its full descriptions
are exact copies of `metadata.localizations.uz-UZ.description` and
`metadata.localizations.ru-RU.description`; the upload manifest records these
sources explicitly. `uz-UZ` is never declared as a Google Play product-page
locale. The five generic queries from `growth/config.json` remain monitoring and
Apple candidate terms; no global Google keyword-targeted listing is packaged.

The UZ App Store Custom Product Page draft uses the same explicit fallback: its
`en-US` payload maps to Uzbek copy/assets, while its `ru-RU` payload maps to
Russian copy/assets. Its keyword lists are planned candidates, not proof that
the terms can already be assigned. Apple only offers terms from the latest
approved base version, so the assignment gate remains blocked and the required
sequence is: submit the base 1.1.0 keywords, wait for base-version approval, and
only then assign Custom Product Page keywords. The installed app continues to
use its complete Uzbek localization.

The default App Store draft preserves the global English name `Nimbo Weather`.
Its Russian override uses `Nimbo: Погода и прогноз` and `Лучшее время для
прогулки`, keeping the generic query terms in a visible indexed field and the
implemented Best Time Outside benefit in the subtitle. This is versioned input
only; it is not evidence that either value is saved in App Store Connect or
public in the UZ storefront.

Apple's keyword limit is 100 UTF-8 bytes, not 100 Unicode characters. The JSON
Schema retains a portable 100-character ceiling, and
`scripts/check_store_metadata.py` applies the stricter byte count to base and
override keyword fields.

Current contracts: [Apple platform-version metadata](https://developer.apple.com/help/app-store-connect/reference/app-information/platform-version-information/),
[Apple Custom Product Page keyword assignment](https://developer.apple.com/help/app-store-connect/create-custom-product-pages/configure-multiple-product-page-versions/),
and [Google custom-listing targeting](https://support.google.com/googleplay/android-developer/answer/9867158?hl=en-GB).

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

The current renderer is intentionally pinned to the exact macOS Arial and Arial
Bold byte hashes recorded in the manifest. Those proprietary system fonts are
not vendored, so Ubuntu CI validates the exact 22 source hashes and 40 output
hashes instead of attempting a non-equivalent re-render. A local rebuild must
run on a machine with the pinned font bytes and Pillow version; any mismatch
fails before assets are accepted.

The command creates 36 opaque PNG creatives under
`store/creatives/growth-2026-08/`, three localized 1024 × 500 Google Play
feature graphics for EN/RU/UZ, and an EN alias for the global default listing.
Re-running it with identical inputs produces identical bytes; renderer or font
drift stops the build. The manifest also hashes the exact set of 22 phone,
watch, and feature-graphic source images, so stale generated artwork cannot
pass after an input capture changes. Story six uses locale-matched watch captures; RU/UZ
sources are real simulator/emulator evidence. The Apple captures remain scoped
to historical build 5 and do not establish current build-6 or physical-watch
QA.

`scripts/check_store_metadata.py` validates schema version, locale coverage,
platform/storefront relationships, exact UZ/RU candidate copy, text limits, experiment
gates, creative references, HTTPS support URLs, exact source identities, and
fail-closed artifact state. A blocked current artifact cannot carry a SHA,
signing evidence, or physical-QA evidence. `scripts/check_store_assets.py`
validates source provenance, six-story locale coverage, expected files,
dimensions, formats, per-surface alpha rules, and the fail-closed claim
exclusions. The Google Play icon must retain its required alpha channel;
feature graphics, screenshots, and captioned creatives must remain opaque.
Device frames must not obscure the app.
