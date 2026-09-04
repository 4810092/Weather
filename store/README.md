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
`upload-manifest-1.1.0.json` schema version 2 resolves each store surface to its
exact locale, metadata, creative, and artifact source-sync state. It remains
top-level `draft-blocked`: current phone vc11, Wear `1000011`, and corrected
Apple build 10 from source `fc4b6de9` are atomically `verified-current` with
exact hashes and signing/source-sync evidence, while all three physical-QA
fields remain null. Protected run `33852229166` produced and
candidate-byte-verified the signed set. Materialization run `33855931653`
stored its exact package and receipt as fixed assets in unpublished draft
release `382592451`. Final manual-only trusted run `33859392482` independently
reopened the draft, safely extracted the closed tree, verified pinned
Bundletool 1.18.3, and returned `byte_verified=true` for all three artifacts.
The related Pages run was skipped and no deployment was created. The draft
remains mutable and must be rechecked before every later use. Its full
`source_revision` is
shared with the release/source gate; `check_release_qa_matrix.py` fails if that
revision differs from the current product/build inputs or if either authority
drifts. Historical-source artifacts and runtime observations cannot satisfy the
current physical fields. Exact Apple build 10 was subsequently uploaded,
processed, attached to the internal TestFlight group, and installed on the
connected iPhone and iPad. Bounded build-10 smoke and a visible iPad widget
render are recorded separately, but the manifest field remains null until the
natural OS-scheduled background completion and fresh crash-log window are
proved. That provider state is separate from signed-byte authority and is not
evidence of completed runtime QA, review submission, rollout, or publication.
At 15:47 Asia/Tashkent on September 4, failed build 9 was detached from the
editable App Store version and exact build 10 was selected and saved. Version
1.1.0 remains `Prepare for Submission` with manual release preserved until the
natural background gate allows review resubmission.
The pinned verification policy is executable rather than documentary. Static
contract mode can validate the committed manifest without private files, but
full verification of any `verified-current` claim must reopen the exact external
filenames under `NIMBO_RELEASE_ARTIFACT_ROOT`, recompute their hashes, and pass
platform signature, signer, identity, and embedded-source checks in the same
invocation. Android additionally requires the exact Bundletool 1.18.3 JAR under
`NIMBO_BUNDLETOOL_JAR`. The Apple gate also requires the retained
`Nimbo.xcarchive`, its matching dSYMs, the App Store Connect
`ExportOptions.plist`, and a signed `NimboSourceRevision` value in all three
bundles. Plain Markdown or JSON receipts cannot replace those bytes. Before the
action-time check, stage only the exact release inputs under one owner-only
directory with this layout (the AAB/IPA names come from the manifest):

```text
<artifact-root>/
├── nimbo-phone-1.1.0-vc11.aab
├── nimbo-phone-1.1.0-vc11-mapping.txt
├── nimbo-wear-1.1.0-vc1000011.aab
├── Nimbo.ipa
├── Nimbo.xcarchive/
└── ExportOptions.plist
```

Then run `python3 scripts/verify_release_artifacts.py --artifact-root
<artifact-root> --bundletool-jar <bundletool-all-1.18.3.jar>`. The verifier
copies each store artifact into a read-only temporary staging file, verifies
that copy, and re-hashes both the staged and source bytes before returning.
Public pull-request CI performs the static manifest contract without private
signed inputs. Full byte authority remains a protected GitHub-hosted macOS
verification responsibility, including pinned Bundletool for Android. Final
trusted run `33859392482` authorized the exact upload authority after the
atomic `3/3 verified-current` promotion. The
protected staging and read-only macOS verifier must pass before every later
artifact use; the top-level manifest, current runtime gates, and Apple crash gate remain
blocked. No self-hosted Mac runner is required. The byte verifier proves that the checked-out source is
clean relative to the embedded revision, but external bytes alone cannot prove
the tree was clean when they were built. Protected run `33852229166` supplied
same-clean-checkout build/sign/verify provenance and a retained closed package.
The protected hosted chain must recheck the exact mutable draft assets and
reopen those bytes through the complete pinned verifier before later use. The
current hosted pass and exact promoted hashes are
recorded in
[`growth/quality/release-artifact-full-verification-2026-09-04-build10-hosted.md`](../growth/quality/release-artifact-full-verification-2026-09-04-build10-hosted.md)
and
[`growth/quality/signed-candidate-run-33852229166.md`](../growth/quality/signed-candidate-run-33852229166.md).
The durable draft locator and its mutable-draft boundary are recorded in
[`growth/quality/release-materialization-2026-09-04-run-33855931653.md`](../growth/quality/release-materialization-2026-09-04-run-33855931653.md).
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
480 × 480 Wear OS screenshot captured from the product watch app. The Apple
set adds one 416 × 496 Apple Watch screenshot, plus one
1320 × 2868 App Store iPhone and one 2064 × 2752 App Store iPad screenshot for
each of the 13 app languages. All were captured from real production UI with a
populated local database; no UI was invented. Capture provenance is recorded
per asset and does not imply exact-current binary or physical-device coverage.

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

Apple lists English (U.K.) as the default App Store language for Uzbekistan.
The default App Store payload therefore includes an explicit `en-GB`
localization, and the UZ Custom Product Page maps its `en-GB` payload to Uzbek
copy/assets while `ru-RU` maps to Russian copy/assets. Its keyword lists are
planned candidates, not proof that the terms can already be assigned. Apple
only offers terms from the latest approved base version, so the assignment gate
remains blocked and the required sequence is: submit the base 1.1.0 keywords,
wait for base-version approval, and only then assign Custom Product Page
keywords. The installed app continues to use its complete Uzbek localization.
The upload manifest explicitly aliases default-listing `en-GB` screenshots and
creatives to the existing `en-US` English assets; it does not imply that a new
English UI capture was produced.

The default App Store draft preserves `Nimbo Weather` in both `en-GB` and
`en-US`. Their subtitle is `Best time to go outside`, matching the implemented
product label and the first benefit-led creative while leaving the generic
`weather` / `forecast` terms in the title and keyword fields. The bounded
routing and copy rationale is versioned in
[`growth/reports/apple-uz-subtitle-opportunity-2026-08-30.md`](../growth/reports/apple-uz-subtitle-opportunity-2026-08-30.md).
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
not vendored, so Ubuntu CI validates the exact 31 source hashes and 40 output
hashes instead of attempting a non-equivalent re-render. A local rebuild must
run on a machine with the pinned font bytes and Pillow version; any mismatch
fails before assets are accepted.

The command creates 36 opaque PNG creatives under
`store/creatives/growth-2026-08/`, three localized 1024 × 500 Google Play
feature graphics for EN/RU/UZ, and an EN alias for the global default listing.
Re-running it with identical inputs produces identical bytes; renderer or font
drift stops the build. The manifest also hashes the exact set of 31 phone,
watch, and feature-graphic source images, so stale generated artwork cannot
pass after an input capture changes. Story six uses locale-matched watch
captures; RU/UZ sources are real simulator/emulator evidence. The Apple phone
capture set contains four distinct source-bound states per EN/RU/UZ locale:
overview/Best Time, recent comparison, selected timeline, and 10-day/AQI
details. They are from predecessor product source `9c2dce4`, build 6, and are
bounded to an iPhone 17 Pro Max simulator on iOS 26.5 with the checked-in
Tashkent quick-city seed and the normal live provider path. They remain valid
creative provenance but do not prove the current `2cdd438` binary, distribution signing,
physical iPhone/iPad/watch/widget QA, TestFlight, store review, rollout, or
public availability. An offline-cache state was not checked in for Apple: a
process-scoped unreachable proxy did not deterministically force the live
provider to fail, and product data was not modified to manufacture the state.
Story five therefore keeps the source-bound overview plus the separately
audited privacy claim; it is not evidence of an Apple offline transition.

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
