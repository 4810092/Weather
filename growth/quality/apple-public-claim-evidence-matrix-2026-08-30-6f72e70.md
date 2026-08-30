# Apple and public-claim evidence matrix — 2026-08-30

Status: **PUBLIC AND CANDIDATE CLAIMS SEPARATED; PRIVACY CORRECTION DEPLOYED
AND VERIFIED; STORE MUTATIONS PENDING**.

This historical audit is bound to checkpoint release-source authority
`6f72e70fff6eb7566e06dd862e1fad09055343a4`. Current authority
`2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652` inherits its public-claim
separation. Public Apple remains
`1.0.1 (4)` and public Google Play remains phone `1.0.2 (6)` plus Wear
`1.0.2 (1000007)`. The current `1.1.0` candidate has no source-current signed
bytes, upload, review, or public availability.
Its 14 Android-host and 12 iOS Simulator provider tests are bounded current-
source regression evidence only. Hosted runs `33297505825` and `33299592101`
remain predecessor `704fd89` history. Current evidence head
`fb877d30b2179a489f5ce18dd06d892461436540` passed exact-source GitHub-hosted
CI run `33300967788` / #117 for `2cdd438` in 24m01s overall: all five jobs
succeeded, including 5/5 tests on each Android UI profile and 18/18 Apple
surface tests. Its six retained GitHub archives are unsigned build and
test-result proof only. The protected environment remains 4/8 secrets, the
signed workflow has not run, 0/3 current signed artifacts are byte-verified,
and physical/crash gates remain blocked. None of this evidence changes a
public claim or store state.

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
`e552c0f87b5774582a0215abec60be92e4245b53`, inherited by checkpoint authority
`6f72e70fff6eb7566e06dd862e1fad09055343a4`, predecessor authority `704fd89`,
and current authority `2cdd438`,
removes those timing details in
Uzbek, Russian, and English and keeps only the version-neutral statement that
Nimbo does not collect or store rating or review text inside the app.

The corrected `site/content.json` SHA-256 is
`59915e7bb0ac70e4c27b625c9229998879bb8604b67531b3ae4782d065d46f76`.
GitHub Pages run `33295070242` is green: build job `99213210597` completed the
localized site and validators, and deploy job `99213248352` published it. After
propagation, direct HTTPS reads of `https://nimbo.uz/privacy/`,
`https://nimbo.uz/ru/privacy/`, and `https://nimbo.uz/en/privacy/` each returned
the locale-matched version-neutral review-text statement. The previous public
wording mismatch is closed; this proves only the deployed site copy, not a
store listing, binary, review prompt, or release-state change.

## Store boundary

The Apple default page, UZ Custom Product Page, Google UZ custom listing,
featuring drafts, localized creatives, and `1.1.0` release notes remain
unpublished inputs. This record authorizes no upload, review submission,
featuring nomination, promotional event, article publication, or outreach.
