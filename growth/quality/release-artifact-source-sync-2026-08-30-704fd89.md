# Historical release artifact source sync — 2026-08-30 deterministic locale gate

Status: **HISTORICAL PREDECESSOR AUTHORITY; EXACT-SOURCE HOSTED REGRESSION WAS
GREEN; SUPERSEDED BY `2cdd438`; 0/3 ARTIFACTS WERE BYTE-VERIFIED AT THIS
CHECKPOINT**.

The authoritative product/build-input commit at this checkpoint was
`704fd893e59d94d8e9a4971313a773b3fa545ab6`. It resolves to Android phone
`1.1.0 (8)`, Wear OS `1.1.0 (1000008)`, and Apple app/widget/watch
`1.1.0 (6)`.

## Change boundary

Compared with predecessor `fb591e3d16f507a5a4f794ae537ccd087523889b`,
the checkpoint authority changes only the Android Compose UI-test locale harness:

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

## Exact-source hosted regression

Public GitHub Actions
[run 33297505825](https://github.com/4810092/Weather/actions/runs/33297505825)
executed at evidence commit
`163ff034c2b93ec302c4c5bee3c49168e0b33ada`, whose resolved release-source
authority at this checkpoint was exactly
`704fd893e59d94d8e9a4971313a773b3fa545ab6`.

- the overall run passed in 17m30s;
- `android-and-shared` passed in 2m31s;
- API 24 phone, API 36 phone, and API 36 tablet UI jobs passed in 2m24s,
  3m15s, and 3m30s respectively, with all five deterministic tests green on
  every profile;
- `ios` passed in 17m25s: shared simulator tests took 5m20s, Apple
  glanceable-surface tests took 2m29s, and the unsigned application build took
  8m37s.

The run retained six GitHub artifact archives:

| Artifact archive | Displayed size | GitHub archive SHA-256 |
| --- | ---: | --- |
| `android-release-unsigned` | 5.1 MB | `36db17cc8a0faac163aad463e9ddbc8ef500c67aea54b9ceb274adeb47c711e4` |
| `wear-release-unsigned` | 2.42 MB | `30d87426a7d0a43508cbee16da377965562802e2839719e7beba943dcae48d1e` |
| `android-ui-results-phone-api24` | 50.2 KB | `46fbc3843c84ff52c53aae0589491912bf00f0f483baca3cdfca27be5f4f4e41` |
| `android-ui-results-phone-api36` | 140 KB | `9d9896ab752ca87cd650607c839be37cfd8e382afa895c3422972116016c9b6c` |
| `android-ui-results-tablet-api36` | 329 KB | `49cdbcad149479b2e79d68238d4ab4b8e584f09dfb91d0dbbe7ff960f254c6da` |
| `ios-simulator-test-results` | 77.9 KB | `1eea44358a95c8e2b58af184fd1fabd46369aec22a12975e128aa54d122994ba` |

These are GitHub archive digests, not verified hashes of signed AAB/IPA upload
candidates. The run closes exact-source hosted regression execution only. It
does not establish distribution signing, transfer any archive digest into the
upload manifest, provide physical-device QA, or diagnose the suppressed iOS
crash.

At `2026-08-30 12:29 +05:00`, the protected `release-signing` environment
contained 4/8 required secrets: the Android keystore payload and the app,
widget, and watch provisioning profiles. The two Android passwords, Apple
distribution P12, and its transport password remain absent behind local
Keychain authorization. No candidate workflow has run, so this partial
provisioning changes neither artifact authority nor the `0/3` result.

## Artifact authority at this checkpoint

| Surface | Exact identity | Signed bytes at checkpoint | Decision |
| --- | --- | --- | --- |
| Android phone/tablet | `1.1.0 (8)` | none bound to this revision | **BLOCKED** |
| Wear OS | `1.1.0 (1000008)` | none bound to this revision | **BLOCKED** |
| Apple app/widget/watch | `1.1.0 (6)` | no distribution-signed archive or IPA bound to this revision | **BLOCKED** |

The schema-v2 upload manifest at this checkpoint kept every SHA-256,
signing-evidence path, and physical-QA path null. Historical candidates,
unsigned artifacts, and device results from predecessor revisions remained
non-transferable.

## Unresolved boundary carried forward

1. Unlock the local login Keychain and provision the four remaining protected
   `release-signing` inputs without exposing credentials in chat, then run the
   manual candidate workflow.
2. Promote the manifest only from the verified receipt and a separately
   committed signing record.
3. Run the exact signed physical phone/tablet/widget/watch matrix and bind its
   evidence to the retained artifact hashes.
4. Obtain and symbolicate the suppressed iOS crash diagnostic, reproduce or
   disposition it against the current signed build, and close the crash gate.

## Successor boundary

Current authority `2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652` adds provider
decoding hardening. The hosted runs and unsigned artifacts documented here
predate that change and do not transfer. Current signing, artifact, crash, and
physical gates remain blocked at `0/3`; see the
[current source-sync record](release-artifact-source-sync-2026-08-30-2cdd438.md).

No release artifact was signed, uploaded, submitted, or published by this
historical source-sync update.
