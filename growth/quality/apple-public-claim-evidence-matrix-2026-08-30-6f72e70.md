# Apple and public-claim evidence matrix — 2026-08-30

Status: **PUBLIC AND CANDIDATE CLAIMS SEPARATED; PRIVACY SOURCE CORRECTED;
DEPLOYMENT AND STORE MUTATIONS PENDING**.

This audit is bound to release-source authority
`6f72e70fff6eb7566e06dd862e1fad09055343a4`. Public Apple remains
`1.0.1 (4)` and public Google Play remains phone `1.0.2 (6)` plus Wear
`1.0.2 (1000007)`. The current `1.1.0` candidate has no source-current signed
bytes, upload, review, or public availability.

## Claim matrix

| Surface / claim | Classification | Decision |
| --- | --- | --- |
| Best Time Outside, yesterday comparison, ±24-hour timeline, 10-day/AQI, saved forecast, and city search without location | `public-proven` at product level through retained public-product evidence | Safe as general Nimbo feature copy; do not infer every-device accessibility or watch-pairing proof |
| Android, iPhone, iPad, Wear OS, Apple Watch, and widget availability | `public-proven` for product availability | Safe availability statement; physical paired behavior remains unclaimed |
| No account, ads, subscription, analytics SDK, or cross-app tracking | `public-proven` within reviewed dependency/privacy scope | Safe while provider, permissions, dependencies, and business model remain unchanged |
| Revised Apple subtitle, Russian localization, UZ Custom Product Page, and localized creative set | `source-backed-draft` | Truthful product wording, but not saved/submitted/public store state |
| Quick-city first use, first-forecast tip, revised review policy, share CTA, and background retry | `candidate-only` | Keep event and release claims unpublished until exact `1.1.0` bytes pass release gates and become public |
| Ranking, featuring, accuracy, safety, ratings, installs, retention, or crash-free claims | `prohibited/unproven` | Keep absent |

## Privacy-copy correction

The previous public privacy route described the candidate-only review-prompt
timing as if it applied to public `1.0.x` products. Commit
`e552c0f87b5774582a0215abec60be92e4245b53`, inherited by current authority
`6f72e70fff6eb7566e06dd862e1fad09055343a4`, removes those timing details in
Uzbek, Russian, and English and keeps only the version-neutral statement that
Nimbo does not collect or store rating or review text inside the app.

The corrected `site/content.json` SHA-256 is
`59915e7bb0ac70e4c27b625c9229998879bb8604b67531b3ae4782d065d46f76`.
This is repository-source evidence only until the Pages workflow succeeds and
the three live privacy routes are verified after propagation. Until then, the
old public wording remains a deployment mismatch and must not be cited as
current-product behavior.

## Store boundary

The Apple default page, UZ Custom Product Page, Google UZ custom listing,
featuring drafts, localized creatives, and `1.1.0` release notes remain
unpublished inputs. This record authorizes no upload, review submission,
featuring nomination, promotional event, article publication, or outreach.
