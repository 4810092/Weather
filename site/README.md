# Nimbo public site

This directory is the versioned source for Nimbo's Uzbek-first public landing,
press kit, support, privacy pages, and a source-backed growth dashboard. The
landing surface intentionally has no analytics, cookie banner, third-party
JavaScript, or build-time package dependency.

Build a local preview from the repository root:

```sh
python3 scripts/build_site.py --base-url http://127.0.0.1:8765
python3 -m http.server 8765 --directory build/pages
```

The deployment workflow builds with `https://nimbo.uz` as the canonical URL and
uploads only `build/pages`. GitHub Pages is the origin; Cloudflare provides
DNS-only records during domain verification and TLS issuance.

All phone images shown on the site are copied from the versioned, real-device or
simulator store capture set. Marketing copy must not imply features that are not
present in the application.
