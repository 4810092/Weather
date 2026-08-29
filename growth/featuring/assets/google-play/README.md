# Google Play promotional-content artwork

These are local, unsubmitted candidates for the proposed Nimbo `1.1.0` major
update. They do not prove Promotional Content eligibility, Console acceptance,
featuring, release publication, or rank impact.

Both images are original raster artwork generated with the built-in OpenAI
image-generation tool on 2026-08-29, then mechanically resized and encoded as
opaque RGB JPEGs. The checked files and SHA-256 values in
`growth/featuring/manifest.json` are the canonical candidates; image generation
is nondeterministic and is not the reproducible source of truth.

## Creative direction

Use case: `ads-marketing`.

Primary prompt:

> Create original text-free Google Play Promotional Content artwork for
> Nimbo's new quick city selection at first launch in Uzbekistan. Show one
> centered luminous coral location marker integrated with a sun-and-cloud
> weather motif above a bright, contemporary Tashkent-inspired skyline. Use six
> much smaller city lights with subtle atmospheric trails to suggest a choice
> among seven cities. Use a polished, friendly 3D editorial style with sky
> blue, turquoise, warm amber, coral, and off-white clouds. Keep one strong
> focal point inside the documented crop-safe area. Include no text, letters,
> numbers, logos, app name, brand mark, store badge, rank, award, testimonial,
> button, toggle, tap target, phone frame, screenshot, watermark, border,
> rounded outer corners, or third-party IP.

The landscape generation specified a `16:9` canvas and Google primary-image
safe zone: 10% on each side, 15% at the top, and 20% at the bottom. The square
generation specified a `1:1` canvas with all critical content inside the
central 70%. The two outputs intentionally contain no locale-specific text, so
the same pair can be used for Uzbek, Russian, and English.

## Pre-submit checks

- Reconfirm the live Play Console upload controls and current image rules.
- Preview every crop, especially Spotlight overlays and compact list surfaces.
- Keep the primary file at or below 1 MB.
- Do not add text, logos, store UI, ratings, ranking, awards, or testimonials.
- If any upload control rejects the square candidate's dimensions, resize from
  the checked square master without changing its composition, then update the
  manifest hash and rerun repository validation.
- Submission remains blocked until the operational gates and exact release
  artifact requirements in `growth/quality/gates.json` pass.

