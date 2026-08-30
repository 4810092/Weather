# Historical release artifact source sync — 2026-08-30 hosted UI rerun checkpoint

Status: **HISTORICAL PREDECESSOR AUTHORITY; RUN 33296238901 FAILED ALL THREE
ANDROID UI PROFILES; SUPERSEDED BY `704fd89`; 0/3 ARTIFACTS WERE BYTE-VERIFIED
AT THIS CHECKPOINT**.

The authoritative product/build-input commit at this checkpoint was
`fb591e3d16f507a5a4f794ae537ccd087523889b`. It resolves to Android phone
`1.1.0 (8)`, Wear OS `1.1.0 (1000008)`, and Apple app/widget/watch
`1.1.0 (6)`.

## Change boundary

Compared with predecessor `6f72e70fff6eb7566e06dd862e1fad09055343a4`,
this checkpoint authority changed only the hosted Android UI proof path:

- Uzbek, Arabic, and Russian localized onboarding-title checks now use
  `performScrollTo()` before visibility assertions. Uzbek and Arabic popular-
  city section headings are also scrolled into view while the existing real
  LTR/RTL quick-city ordering checks remain intact. The English first-viewport
  assertion remains strict, and the Russian case still runs at 200% font scale.
- The KVM gate records runner identity and device metadata, installs/reloads the
  udev rule, triggers the device, then applies `chmod 0666` to the current
  `/dev/kvm` inode before the fail-closed runner-user read/write check.
- The emulator is still prohibited from falling back to software execution:
  `disable-linux-hw-accel` remains `false` and the emulator command now requires
  explicit `-accel on`.

The production weather behavior, store versions, signing identities, provider
endpoint, verification metadata, and upload policy are unchanged. Per the
hosted-only CI decision, no broad Gradle/Xcode suite or emulator matrix was run
locally for this checkpoint authority.

Strict dependency verification still contains `1,758` artifact entries. The
complete `gradle/verification-metadata.xml` SHA-256 remains
`91b016e7fc72ca605d473634135b87e1d5b4e16f04608272a0bd809d263782a4`.

## Historical predecessor run

Public GitHub Actions
[run 33295070238](https://github.com/4810092/Weather/actions/runs/33295070238)
executed at evidence commit
`2390a10a676d958b70a478f47932685413d15fbc`, whose release-source authority
was `6f72e70fff6eb7566e06dd862e1fad09055343a4`. It failed overall after 12m24s:

- `android-and-shared` passed in 6m32s;
- `ios` passed in 12m21s, including shared simulator tests, Apple surface tests,
  and unsigned app/watch simulator products;
- API 24 and API 36 phone jobs each executed exactly five tests and each failed
  exactly two title-visibility assertions: Uzbek onboarding and Russian 200%;
- the API 36 tablet job stopped before emulator start because `/dev/kvm`
  existed but was not read/write-accessible to the runner user.

That failed run is bounded historical regression evidence only. Its unsigned
artifacts and failed-test reports are not upload candidates and did not transfer
to `fb591e3`.

Public GitHub Actions
[run 33296238901](https://github.com/4810092/Weather/actions/runs/33296238901)
later executed at evidence commit
`23617f361671a35245b2a892631fab73025b09b0`, whose release-source authority was
this exact `fb591e3` checkpoint:

- `android-and-shared` passed in 1m55s;
- `ios` passed in 20m38s;
- the fail-closed KVM gate passed on API 24 phone, API 36 phone, and API 36
  tablet;
- every UI job launched exactly five tests and every job failed the same two
  zero-node Uzbek/Russian locale selectors.

The run failed overall. It proved that scrolling did not resolve localization:
the generic activity reset device configuration before Compose resources were
created. These results are historical and do not transfer to successor
authority `704fd89`.

## Artifact authority at this checkpoint

| Surface | Exact identity | Signed bytes at checkpoint | Decision |
| --- | --- | --- | --- |
| Android phone/tablet | `1.1.0 (8)` | none bound to this revision | **BLOCKED** |
| Wear OS | `1.1.0 (1000008)` | none bound to this revision | **BLOCKED** |
| Apple app/widget/watch | `1.1.0 (6)` | no distribution-signed archive or IPA bound to this revision | **BLOCKED** |

The schema-v2 upload manifest at this checkpoint kept every SHA-256, signing-
evidence path, and physical-QA path null. Historical candidates, unsigned
artifacts, and device results from predecessor revisions remained non-transferable.

## Successor boundary

Successor authority `704fd893e59d94d8e9a4971313a773b3fa545ab6` replaces the
generic test activity with a dedicated activity that applies locale before
composition. Targeted device-test ktlint, compilation, and manifest processing
pass, but no hosted rerun exists for that successor. The current signing,
artifact, and physical matrix remains blocked at `0/3`; see the
[current source-sync record](release-artifact-source-sync-2026-08-30-704fd89.md).

No release artifact was signed, uploaded, submitted, or published by this
historical source-sync update.
