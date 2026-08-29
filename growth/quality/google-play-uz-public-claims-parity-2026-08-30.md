# Google Play UZ public-claims parity — 2026-08-30

Status: **CLAIM PARITY PASS; CONSOLE SUBMISSION HOLD**.

Revision 2, audited after the repository-only Uzbek-fallback title change from
`Nimbo: Ob-havo va prognoz` to `Nimbo Weather: Ob-havo`. The new title adds a
generic discovery term and retains the local `Ob-havo` phrase; it adds no
functional or quality claim. The evidence and bounded rationale are recorded
in `growth/reports/google-play-uz-title-opportunity-2026-08-30.md`.

The persisted Uzbekistan Custom Store Listing draft is truthful for the
currently public Android phone release `1.0.2 (6)` and the public Wear OS
release `1.0.2 (1000007)`. The copy and six Google Play stories do not depend
on the unreleased `1.1.0` onboarding, review, share, background-retry, or
first-screen layout changes.

This pass is deliberately narrower than a publication authorization. The
listing remains a Console draft, and the independent crash, upload-signed
artifact, and physical-device release gates remain blocked. No Console field,
release, rollout, review, or publication state was changed by this audit.

## Audited identities

| Surface | Audited artifact | Identity | SHA-256 / boundary |
| --- | --- | --- | --- |
| Android phone/tablet | preserved upload AAB outside Git | `1.0.2 (6)` | `798cfe33b636cbe6a291ef0125abc193dbd1549e31c7daf50b261a0105c322ca` |
| Android runtime | Bundletool 1.18.3 universal APK generated from that AAB and signed only for local installation | `1.0.2 (6)`, min SDK 26, target SDK 36 | `64b732a7119eef449005edf06bf219f5debd5235ef4693547a9c4eba5d895f6d`; this local signature is not Play delivery proof |
| Wear OS | preserved accepted upload AAB outside Git | `1.0.2 (1000007)` | `aeecf509e977036f9af3f0d48c55e80413619a3fa5ea6061fa9f070f73ba2b91` |
| Wear runtime | Bundletool 1.18.3 universal APK generated from that AAB and signed only for local installation | `1.0.2 (1000007)`, min SDK 30, target SDK 36 | `fcddf5002823df5738e61645a836a1f89555f222e895e410d79aa3a8af7b23cd`; this local signature is not Play delivery proof |
| Bundletool | official `bundletool-all-1.18.3.jar` | 1.18.3 | `a099cfa1543f55593bc2ed16a70a7c67fe54b1747bb7301f37fdfd6d91028e29` |

Google Play Console independently reports the phone release `1.0.2 (6)` and
Wear release `1.0.2 (1000007)` as public. The preserved AAB hashes are the
recorded release inputs; this audit does not claim a newly downloaded
Play-signed APK or cryptographic proof of the bytes delivered to every device.

The phone APK was clean-installed on a fresh, no-snapshot Android API 36
emulator at `1080 x 1920`. Location permission remained ungranted, the app
locale was set to `uz-UZ`, and Toshkent was selected through ordinary city
search. The Wear APK was clean-installed on a fresh API 37, `480 x 480` round
Wear emulator and rendered its built-in product demo/data surface in Uzbek.

## Claim matrix

`public-proven` means the function was observed in the AAB-derived public
version runtime or is structurally present in that exact AAB. `candidate-only`
means it belongs to `1.1.0` and must not appear in this listing. `unknown`
marks a stronger behavior that this audit did not prove.

| Draft claim / story | Classification | Exact evidence | Asset or copy source | Decision |
| --- | --- | --- | --- | --- |
| `Nimbo Weather: Ob-havo` / `Nimbo: Погода и прогноз` | public-proven | Product identity is version-neutral; both public APKs label the app `Nimbo` and ship RU/UZ resources. `Weather` and `Ob-havo` describe the existing weather product rather than a new function | `store/metadata.json` | safe |
| Best Time Outside / лучшее время / eng yaxshi vaqt | public-proven | Exact phone vc6 runtime rendered `Tashqariga chiqish uchun eng yaxshi vaqt`, `00:00–02:00`, and the comfort/rain/wind reason | title, short copy, full copy, feature graphics, `01-best-time.png` | safe; no 1.1-only dependency |
| Compare with yesterday / recent weather | public-proven | Exact phone vc6 runtime rendered `Kecha shu vaqtdagi bilan deyarli bir xil` and recent-day cards | full copy and `02-recent-comparison.png` | safe |
| `−24 / NOW / +24` timeline | public-proven | Exact phone vc6 runtime rendered `24 soat oldin · hozir · 24 soat keyin`; current UZ `01-current` and `02-timeline-selected` source pixels are pixel-identical to the captures committed with the 1.0.2 release source | full copy and `03-timeline.png` | safe |
| 10-day forecast and AQI | public-proven | Exact phone vc6 runtime rendered `Havo sifati`, AQI/PM values, provider attribution, and `10 kunlik prognoz` | full copy and `04-details.png` | safe feature; the dedicated RU/UZ source capture was produced after release, but it depicts the same vc6 surface |
| Last saved forecast offline | public-proven | After a successful forecast, exact phone vc6 was cold-launched with connectivity disabled and rendered `Yangilab bo‘lmadi. Saqlangan ob-havo ko‘rsatilmoqda` while retaining the forecast | full copy and `05-offline-privacy.png` | safe feature; the dedicated RU/UZ source capture was produced after release, but it depicts the same vc6 surface |
| City search without location permission | public-proven | Exact phone vc6 Uzbek onboarding stated that city search works without permission; Toshkent search and live forecast succeeded while location permission remained ungranted | short/full copy | safe |
| Automatic, metric, and imperial units | public-proven | Exact phone vc6 runtime rendered `Avtomatik`, `Metrik`, and `Imperial` selectors | full copy | safe |
| Android home-screen widget | public-proven (structural) | Exact vc6 APK manifest contains `WeatherWidgetProvider`, `APPWIDGET_UPDATE`, provider metadata, widget layout, and widget-info resources; the API 36 launcher discovered the provider | full copy only; widget story stays excluded from the creative manifest | safe availability claim; no exact public physical-widget rendering claimed |
| Wear OS phone-and-wrist story | public-proven for availability/rendering | Exact public Wear AAB-derived `1000007` APK rendered the localized 480 x 480 watch surface with temperature, range, rain, and AQI; Console records the same version public | `06-watch.png` and localized Wear source captures | safe for `phone and wrist`; the RU/UZ source pixels are emulator captures, not paired physical-watch proof |
| Apple Watch availability | public-proven outside the Android artifact | The dated public-store audit records one Watch creative on the public App Store page and public iOS `1.0.1`; Android vc6 is not used as its evidence | full copy only | safe as a cross-platform availability statement; do not infer Android-to-Apple-Watch pairing |
| No account, ads, or analytics | public-proven | vc6 has no account flow; the versioned privacy/dependency audit records no ads or analytics SDK | full copy | safe |
| Quick Uzbekistan city chips | candidate-only | Introduced after vc6 | absent from draft copy and all six story captions | must remain absent until 1.1.0 is public |
| First-forecast tip, revised review policy, localized store CTA in share, background retry | candidate-only | Introduced after vc6 | absent from draft copy and all six story captions | must remain absent until 1.1.0 is public |
| Physical paired phone-to-Wear transfer and exact Play-signed physical widget behavior | unknown | No exact public paired physical matrix was produced by this audit | not claimed by the draft | no blocker for current wording; any stronger sync/physical claim is blocked |

## Creative provenance boundary

The claim and the concrete capture provenance are tracked separately:

- UZ/RU source images `01-current.png` and `02-timeline-selected.png` are
  pixel-equivalent to their 1.0.2 release-source counterparts.
- Dedicated UZ/RU `03-details.png`, `05-offline-cache.png`, and localized Wear
  captures were created after the phone release. They therefore remain
  candidate-sourced pixels even though the exact public-version runtime above
  independently reproduced every marketed surface.
- The generated frames crop, scale, and caption genuine app pixels. They do
  not advertise quick-city chips, the first-forecast tip, the moved
  first-screen Best Time placement, the revised review flow, or another
  1.1-only state.
- The home-screen-widget screenshot remains excluded. Adding one requires a
  new exact-public or then-current-public capture and a new audit revision.

This distinction prevents a candidate screenshot from being misreported as a
Play-delivered screenshot while still allowing a truthful feature-parity
decision.

## Decision and fail-closed rule

- **Public 1.0.2 claim parity: PASS.** No current UZ/RU copy or Google story
  requires an unreleased 1.1.0 function.
- **Custom-listing Console submission: HOLD.** This audit does not override the
  independent crash, source-signed artifact, physical-device, or publication
  gates.
- Any change to the UZ listing payload, either localized feature graphic, any
  of the twelve RU/UZ Google phone creatives, either localized Wear source, or
  the icon invalidates this dated parity decision until it is re-audited.
- Any new claim about quick-city shortcuts, first-run guidance, review flow,
  paired-watch synchronization, physical-device validation, ranking, or
  production quality is blocked unless separately evidenced.

The drift guard is executable:

```sh
python3 scripts/check_google_play_public_claims.py
python3 -m unittest scripts.growth.tests.test_public_listing_claims
```

The validator pins only the audited Google UZ payload and Google assets. It
does not modify or validate Apple creatives, ranks, dashboards, release
versions, or Console state.
