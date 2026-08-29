# Apple localized source-bound product capture — 2026-08-30

Status: **PASS for predecessor `9c2dce4` App Store phone screenshot provenance;
not current-binary evidence for `44c1892`**.

This record proves only the provenance and store-format readiness of twelve
localized iPhone phone sources: four distinct states in each of English,
Russian, and Uzbek. It does not satisfy Apple distribution signing,
physical-device, iPad, widget, paired-watch, iOS 15, crash, TestFlight, review,
rollout, or public-availability gates.
The captures were exact-current for `9c2dce4` when recorded; later source
authority `44c1892` supersedes that binary identity, so the images remain
creative provenance but cannot verify the current app artifact.

## Exact captured build and simulator boundary

- Product source:
  `9c2dce4200dbba5487c8c458ade4616005fde6e6`.
- Release simulator app: `NimboSimulator` `1.1.0 (6)`, bundle
  `uz.ganikhodjaev.weather`, minimum iOS `15.0`.
- Captured executable SHA-256:
  `b7c3ba937658007b07ee9ad8e85ddc892e90f423e7839e0dc112a1070ea04849`.
- Executable and UUID-matched dSYM UUID:
  `44F5F65F-080A-3F89-B5E5-D052EDF9A219` (`arm64`).
- Signature boundary: ad-hoc simulator signature, no `TeamIdentifier`; this is
  not an App Store upload artifact.
- Runtime: iPhone 17 Pro Max simulator, iOS 26.5, 1320 x 2868 framebuffer.
- Capture window: 2026-08-30 00:01 UZT, after the local-day rollover. All three
  localized launches rendered the real `00:00–02:00` Best Time recommendation
  instead of the legitimate late-evening insufficient-hours fallback.

## Seed and live-provider boundary

The simulator container was seeded only with the product's checked-in Tashkent
quick-city identity and exact coordinates (`quick:uz:tashkent`, 41.2995,
69.2401, `Asia/Tashkent`). Nimbo then fetched the forecast through its normal
live provider path. At capture the database contained 408 weather-hour, 17
daily-forecast, 120 air-quality-hour, and 48 forecast-snapshot rows for that
exact location.

Between terminated launches, only the quick-city display label was changed to
the product's English (`Tashkent`, `Uzbekistan`), Russian (`Ташкент`,
`Узбекистан`), or Uzbek (`Toshkent`, `Oʻzbekiston`) name. Each launch used the
matching Apple language and locale. No weather value, condition,
recommendation, UI pixel, or product logic was invented or retouched.

## Capture interactions and versioned phone sources

An ephemeral XCUITest harness outside the repository launched the exact app by
bundle identifier and used only real accessibility interactions: dismiss the
context tip, select the visible `02:00` timeline button, and scroll to the
10-day/AQI section. The harness changed no product source or stored weather
values. Each checked-in image is the direct kept `XCUIScreen` attachment for
that state.

| Locale | State | Source | SHA-256 |
| --- | --- | --- | --- |
| English | Overview / Best Time | [`iphone-6.9-en/01-current.png`](../../store/screenshots/app-store/iphone-6.9-en/01-current.png) | `aa53927097576b5c79e42dbf9d5448865ff0eb6dfe1742a4aff0376d35680445` |
| English | Recent comparison | [`iphone-6.9-en/02-recent-comparison.png`](../../store/screenshots/app-store/iphone-6.9-en/02-recent-comparison.png) | `529fd6b68c7848915b5f4794681179ee21054ece78e88a8929f171c71d8418a4` |
| English | Selected `02:00` timeline | [`iphone-6.9-en/03-timeline-selected.png`](../../store/screenshots/app-store/iphone-6.9-en/03-timeline-selected.png) | `c7e2baf75ddaf9cd8a992fdcc35b00124e4c59874916522123315abe8458e15b` |
| English | 10-day / AQI details | [`iphone-6.9-en/04-details.png`](../../store/screenshots/app-store/iphone-6.9-en/04-details.png) | `9f0e2a3ed3c490b56966c75d07fdba2633ab5317b9be1165a121f1a6bc8c6bba` |
| Russian | Overview / Best Time | [`iphone-6.9-ru-RU/01-current.png`](../../store/screenshots/app-store/iphone-6.9-ru-RU/01-current.png) | `7392de3670de2d04914d7713cc2d2abea50c0ccac3a742c143503191d859c2af` |
| Russian | Recent comparison | [`iphone-6.9-ru-RU/02-recent-comparison.png`](../../store/screenshots/app-store/iphone-6.9-ru-RU/02-recent-comparison.png) | `b8e8234306784fbb5e73f3f8f5f06707da4f37b06bbed2db2a65bf5dd9a5a10d` |
| Russian | Selected `02:00` timeline | [`iphone-6.9-ru-RU/03-timeline-selected.png`](../../store/screenshots/app-store/iphone-6.9-ru-RU/03-timeline-selected.png) | `dfa1876f613c3bb1fca35164c59aa697ee0107fad4a01a98fa0186e483279ef2` |
| Russian | 10-day / AQI details | [`iphone-6.9-ru-RU/04-details.png`](../../store/screenshots/app-store/iphone-6.9-ru-RU/04-details.png) | `60c80b8e368c0efb60e67dafcb6b64655efee37d0c47f4093b31a4e1e818cb62` |
| Uzbek | Overview / Best Time | [`iphone-6.9-uz-UZ/01-current.png`](../../store/screenshots/app-store/iphone-6.9-uz-UZ/01-current.png) | `a7a039dfa2f556ccf154316b655271336d8075dc2701e1108a78da1760c85fae` |
| Uzbek | Recent comparison | [`iphone-6.9-uz-UZ/02-recent-comparison.png`](../../store/screenshots/app-store/iphone-6.9-uz-UZ/02-recent-comparison.png) | `d1c121c148c2e6506e6dc25a22cd7aeb807f6a82812f2fdeac2311e9830d40b2` |
| Uzbek | Selected `02:00` timeline | [`iphone-6.9-uz-UZ/03-timeline-selected.png`](../../store/screenshots/app-store/iphone-6.9-uz-UZ/03-timeline-selected.png) | `5316254056d64128b8ce803adf620815921840017f9edaba7888c9b489e0d087` |
| Uzbek | 10-day / AQI details | [`iphone-6.9-uz-UZ/04-details.png`](../../store/screenshots/app-store/iphone-6.9-uz-UZ/04-details.png) | `8db685119840564386ebd8b39d7203d640e8b3a52a8d58deee19ae495037e7df` |

The initial overview screenshots were converted losslessly from opaque RGBA to
RGB PNG; the nine interaction-state screenshots were exported directly as
opaque RGB PNG attachments. All twelve preserve the 1320 x 2868 framebuffer
and are accepted by the App Store asset validator.

## Explicit offline-state limitation

A process-scoped unreachable HTTP/HTTPS proxy was tested against a terminated
launch and an explicit refresh. The normal Apple networking stack still
completed a live refresh, so the expected saved-weather error did not appear.
That attempted screenshot was rejected. We did not alter timestamps, provider
responses, database values, or application code to manufacture an offline
state. Therefore no Apple `05-offline-cache` source is checked in and this
record makes no claim that an Apple offline transition was captured.

## Creative-set and cleanup boundary

Creative manifest revision 7 hashes the twelve source-bound predecessor files. The
deterministic renderer only crops, scales, frames, and captions those real
application pixels; the complete generated output set remains byte-locked in
the manifest. Stories two through four now use the matching recent-comparison,
selected-timeline, and 10-day/AQI sources. Story five retains the source-bound
overview and the separately audited privacy caption; it is not presented as
Apple offline-state evidence.

The final story-two/three/four output hashes are:

| Locale | Story 2 | Story 3 | Story 4 |
| --- | --- | --- | --- |
| English | `249cc78fcc2198ccec803f98b1ad95d7ba83b5f6f5531136038ddb96c9710ff5` | `95f92fb39cb5a3b3e5a82a348aaff5f7f0c72f61a047f64cc7f5a02a17a84e54` | `a90a1f430bc3452c342508ea69a9d2d73f5a7576be62b0d793537e543ca8538d` |
| Russian | `6bc62c1f077872c6066d9568ebe83b5892c8138a12faae0ad13144898a986cc4` | `a9c11507c32c61b3324995d8fa60b99175a8d22d902ed9f2f013ff79017b6d79` | `2cefece39b18b9a28c8ea6b78cbaf7e71996627e25525d01f229f82e7fee5300` |
| Uzbek | `c00aa4c40d3315c852536f4a58566aeb66b4a0c233b1356b2be6a1b73156a8b7` | `534a9b884dcf21fc35586428b849fc28a3fff828048c9069c37ea590ec5a8fba` | `9218e53b92620defc5338043a7b17744d3de5d35fd086b48fa63c74761e9ea64` |

A second complete renderer run produced these same hashes and passed the
fail-closed 40-output contract. Visual inspection of all nine generated
story-two/three/four images confirmed the corresponding localized source state,
with no clipping or visible PII.

After verification the temporary app and XCUITest runner were terminated and
uninstalled, the status-bar override was cleared, and the dedicated simulator
was shut down. Both bundle-container lookups returned not found before the
final shutdown.
No store upload, submission, outreach, rollout, or other external action was
performed.
