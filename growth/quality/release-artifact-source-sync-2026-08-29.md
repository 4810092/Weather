# Release artifact source sync — 2026-08-29

Status: **BLOCKED for Android phone, Wear OS, and Apple**.
No artifact was signed, uploaded, submitted, or published by this refresh.

## Decision

The exact product commit is
`24ea3734c105e259374ad3b41a6f7e6476ea70db`. Its source identities are Android
phone `1.1.0 (8)`, Apple app/widget/watch `1.1.0 (6)`, and Wear OS
`1.1.0 (1000008)`.

| Surface | Source sync | Exact current evidence | Signing and device boundary |
| --- | --- | --- | --- |
| Android phone/tablet | **BLOCKED** | AAB `f91d0dce82aad7596118a6563d64b94f9f90daa2550cfb4b345fc3ef966bfdab`; mapping `d749110783872a36406c56a99b11d9c67764a7973d767656c3bd6f0ed59addfd` | Bundletool passes and embedded VCS metadata names the exact commit, but the AAB has zero signature entries. The exact debug APK passed the bounded first-screen smoke on a physical API 25 phone; there is no upload-signed/full physical matrix. |
| Wear OS | **BLOCKED** | unsigned AAB `6bcf5f9b947cb52887ba2e5c7a48c59cd5a1428c4680c67d63edd6a708bcd439`; historical signed AAB `ac19a0eab1a60554db309166f135e754c97205b79c4f5182164a8b21594e7dc6` | The unsigned bundle embeds exact revision `24ea373`; the signed bundle embeds historical revision `4d9492a`. There is no exact-current signed bundle or physical-watch pass. |
| Apple app/widget/watch | **BLOCKED** | app `421b867257004a15e6042cb98817190570b91cb8c54ac61b3c4e8df049f94ad7`; widget `e639f0661cd6e96924803d8aa5982706ee0d78c981b7d2d4375b920d2eac1b27`; watch `9f29f22984185f2c5cf072357434b442b5e95f90b6c292b9aabfc97993bd689d` | Release simulator executables carry only linker-generated ad-hoc signatures. UUID-matched dSYMs verify, but there is no distribution-signed archive, IPA, or physical Apple pass. |

## Current verification

- The phone bundle reports package `uz.ganikhodjaev.weather`, versionCode `8`,
  versionName `1.1.0`, minSdk `24`, and targetSdk `36`. Bundletool 1.18.3
  validation passed, and embedded VCS metadata resolves to the full commit
  above. Archive inspection found zero signature entries.
- The exact phone debug APK SHA-256 is
  `968ac46930c6175562855b1e5229a74f9d49c47e3b4da107334d337291530ad4`.
  Its installed bytes matched on a physical Android 7.1.1 / API 25 phone after
  a fresh install. Russian onboarding, Tashkent without location permission,
  the first-screen Best Time card, 150% text, and the exercised process path
  passed. This is debug evidence, not a source-synced signed release pass.
- Empty/Fresh/Stale phone-widget and round-Wear emulator coverage is retained in
  `growth/quality/surface-freshness-2026-08-29.md` as prior regression evidence
  for commit `ee7c36f`; it is not relabelled as exact-current physical proof.
- The Apple executables above are thin arm64 simulator products for iOS 15.0
  app/widget and watchOS 10.0. Their UUIDs are app
  `6F1E3580-866F-3F7B-B4E2-73A22488CDBF`, widget
  `3DF79B39-B3BF-3898-9A5D-DBE9F872C74E`, and watch
  `77A04CF4-4666-38C7-AC65-5A658831BA02`; each matches its dSYM. They have no
  Team Identifier, bound Info.plist, or sealed resources. This is not archive
  or physical evidence.
- The exact product source passed 127 growth tests, repository, localization,
  store metadata/assets/previews, dashboard, and site checks. Targeted Gradle
  tests plus the Android debug build passed 146 actionable tasks; exact phone
  and Wear release bundles passed 133 tasks; the iOS simulator test passed 26
  tasks; and the separate Swift surface suite passed 18 XCTest cases. Both AABs
  passed Bundletool 1.18.3 validation.
- The retained signed Wear bundle embeds full revision
  `4d9492a343283344ac80f3248a73c6fc752906e1`; the fresh unsigned bundle embeds
  `24ea3734c105e259374ad3b41a6f7e6476ea70db`. Exact-source provenance therefore
  remains blocked.
- Android protected-value lookup remains unauthorized with `security` status
  `51`. Apple private-key use reports `errSecAuthFailed (-25293)`, and a GUI
  Xcode archive fails at `NimboWidget` CodeSign without producing an archive.
  Existing credentials and identities were not printed, replaced, or reset.

## Prior-product dated CI evidence

GitHub Actions run [`33250702915`](https://github.com/4810092/Weather/actions/runs/33250702915)
succeeded on the prior product commit
`ee7c36fbd83970e0bc44aa45681c78fc69bba155` in `20m36s`.
`android-and-shared` completed in `3m59s`; `ios` completed in `20m32s`. The run
retained these workflow artifacts:

| Workflow artifact | Archive digest (SHA-256) | Boundary |
| --- | --- | --- |
| `android-release-unsigned` | `550b0bae8132b3b9e263587b033c97c7a577a88a0fbdbc61cccbf60d0a6f5fa8` | Artifact archive digest, not the inner phone AAB identity; unsigned build only. |
| `wear-release-unsigned` | `247314d495ea7eb7a57a0d36676f03ee29f1ef5973d8e33532ecbefe2bd82636` | Artifact archive digest, not the inner Wear AAB identity; unsigned build only. |
| `ios-simulator-test-results` | `07864344b354c8507ba86230c1e601e95625aac5411b317f309748fadd010f25` | Simulator test-output archive, not a distribution archive. |

This prior-product CI run proves that revision's automated workflow only. It is not
signing, store upload, review, publication, physical-device, or
end-user-availability evidence and does not prove the current product commit.

See `growth/quality/surface-freshness-2026-08-29.md` and
`growth/quality/signing-readiness-2026-08-29.md` for the bounded evidence.

## Preserved historical candidates

| Surface | Historical identity | SHA-256 | Evidence boundary |
| --- | --- | --- | --- |
| Android phone/tablet | `1.1.0 (7)` | `e476a124c33854873add9061140f68f1720ff098202b52e7758038bb50f5a77c` | Signed artifact and API 25 physical results remain scoped to vc7 only. |
| Wear OS | `1.1.0 (1000008)`, revision `4d9492a` | `ac19a0eab1a60554db309166f135e754c97205b79c4f5182164a8b21594e7dc6` | Signed bytes remain historical because embedded VCS metadata does not identify the exact current commit; no physical-watch pass exists. |
| Apple app/widget/watch | `1.1.0 (5)` | `b36f8fddb225cd616e3833de6037b6434486ec3cbb9ed06f5cc8deb0627ed4dc` | Distribution archive and bounded iPad evidence remain scoped to build 5 only. |

Those historical artifacts predate the current product commit and
cannot be promoted as current-source evidence.

## Unblock requirements

1. Restore authorized use of the existing protected signing material without
   replacing identities or exposing secrets.
2. Upload-sign the Android phone and Wear OS AABs and distribution-sign the
   Apple archive from the exact current source; verify certificates, embedded
   revisions, versions, hashes, provisioning, dSYMs, and exported artifacts.
3. Run the source-synced signed physical phone/tablet/widget/watch matrix.
4. Populate upload-manifest artifact fields only after the corresponding files
   exist and the validator accepts the exact source identity.

This is a local release-integrity record, not proof of store processing or
public availability.
