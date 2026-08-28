# Nimbo public site

This directory is the versioned source for Nimbo's Uzbek-first public landing,
press kit, support, privacy pages, seasonal-guide pipeline, and a source-backed growth dashboard. The
landing surface intentionally has no analytics, cookie banner, third-party
JavaScript, or build-time package dependency.

Build a local preview from the repository root:

```sh
python3 scripts/build_site.py --base-url http://127.0.0.1:8765
python3 -m http.server 8765 --directory build/pages
```

The two September guides in `growth/content/articles.json` remain
`draft-blocked`. The normal production build excludes them. Use
`--include-drafts` only for local/CI QA; changing an article to `published`
requires a real publication date and explicit `pass` state for every gate named
in `growth/content/calendar.csv`. The builder reads
`growth/quality/gates.json` and fails rather than publishing through an open
provider, crash, release, device, policy, or domain gate.

The deployment workflow runs automatically when site, dashboard, or site-build
sources change on `master`, and it also supports a manual dispatch. It builds
with `https://nimbo.uz` as the canonical URL and uploads only `build/pages`.
GitHub Pages is the origin; Cloudflare provides DNS-only records during domain
verification and TLS issuance.

All phone images shown on the site are copied from the versioned, real-device or
simulator store capture set. Marketing copy must not imply features that are not
present in the application. The public press download uses the dedicated
`site/assets/press-asset-usage.md`; internal Store preflight notes are never
copied into the deployed press kit.
