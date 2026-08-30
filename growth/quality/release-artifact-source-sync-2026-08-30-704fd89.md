# Release artifact source sync — 2026-08-30 deterministic locale gate

Status: **BLOCKED for Android phone, Wear OS, and Apple; exact-source hosted
rerun pending; 0/3 current artifacts byte-verified**.

The authoritative product/build-input commit is
`704fd893e59d94d8e9a4971313a773b3fa545ab6`. It resolves to Android phone
`1.1.0 (8)`, Wear OS `1.1.0 (1000008)`, and Apple app/widget/watch
`1.1.0 (6)`.

## Change boundary

Compared with predecessor `fb591e3d16f507a5a4f794ae537ccd087523889b`,
the current authority changes only the Android Compose UI-test locale harness:

- the test manifest launches `NimboLocaleTestActivity` instead of the generic
  `ComponentActivity`;
- the dedicated activity applies the requested `LocaleList`, resource locale,
  and layout direction to its base Android configuration in
  `attachBaseContext()`, before Compose creates the tested content;
- the harness verifies that Compose resources observe the injected language
  and derives `LocalLayoutDirection` from that same locale;
- all five tests and their exact Uzbek, Arabic, Russian, RTL, 200% text,
  accessibility, onboarding, successful-forecast, cached-offline, and recovery
  assertions remain present.

Targeted local checks passed for this exact source:

- `:shared:ktlintAndroidDeviceTestSourceSetCheck`;
- `:shared:compileAndroidDeviceTest`;
- `:shared:processAndroidDeviceTestManifest`, with the merged manifest resolving
  the custom activity.

No emulator matrix, broad Gradle/Xcode suite, signed build, or physical-device
test was run locally for this authority. Production weather behavior, store
versions, signing identities, provider endpoint, CI runners, and upload policy
are unchanged.

Strict dependency verification still contains `1,758` artifact entries. The
complete `gradle/verification-metadata.xml` SHA-256 remains
`91b016e7fc72ca605d473634135b87e1d5b4e16f04608272a0bd809d263782a4`.

## Historical predecessor run

Public GitHub Actions
[run 33296238901](https://github.com/4810092/Weather/actions/runs/33296238901)
executed at evidence commit
`23617f361671a35245b2a892631fab73025b09b0`, whose release-source authority was
`fb591e3d16f507a5a4f794ae537ccd087523889b`:

- `android-and-shared` passed;
- the fail-closed KVM/hardware-acceleration gate passed on API 24 phone, API 36
  phone, and API 36 tablet;
- every Android UI job launched exactly five tests and every job failed the
  same two localized title checks: the Uzbek onboarding title and Russian title
  at 200% font scale were absent from the semantics tree;
- the zero-node failures show that scrolling was not the issue. The predecessor
  harness changed the default locale before launching a generic activity, whose
  device configuration reset meant Compose resources still observed the system
  locale;
- `ios` passed in 20m38s: shared iOS Simulator tests took 7m24s, Apple
  glanceable-surface tests took 3m9s, and the unsigned application build took
  9m18s.

The three Android UI failures made the predecessor run fail overall. Its
unsigned artifacts and failed-test reports are bounded historical regression
evidence only; they are not upload candidates and do not transfer to `704fd89`.
No hosted run has executed the current custom-activity locale harness yet.

## Current artifact authority

| Surface | Exact identity | Current signed bytes | Decision |
| --- | --- | --- | --- |
| Android phone/tablet | `1.1.0 (8)` | none bound to this revision | **BLOCKED** |
| Wear OS | `1.1.0 (1000008)` | none bound to this revision | **BLOCKED** |
| Apple app/widget/watch | `1.1.0 (6)` | no distribution-signed archive or IPA bound to this revision | **BLOCKED** |

The schema-v2 upload manifest keeps every current SHA-256, signing-evidence
path, and physical-QA path null. Historical candidates, unsigned artifacts,
and device results from predecessor revisions remain non-transferable.

## Remaining unblock

1. Push the source/evidence commits and obtain a green ordinary hosted rerun for
   this exact authority, including both ordinary jobs and all three Android UI
   jobs.
2. Provision the eight required protected `release-signing` environment inputs
   without exposing credentials in chat, then run the manual candidate workflow.
3. Promote the manifest only from the verified receipt and a separately
   committed signing record.
4. Run the exact signed physical phone/tablet/widget/watch matrix and bind its
   evidence to the retained artifact hashes.

No release artifact was signed, uploaded, submitted, or published by this
source-sync update.
