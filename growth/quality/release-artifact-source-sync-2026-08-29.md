# Release artifact source sync — 2026-08-29

Status: **BLOCKED for Android phone, Wear OS, and Apple**.
No artifact was signed, uploaded, submitted, or published by this refresh.

## Decision

The exact product commit is
`ee7c36fbd83970e0bc44aa45681c78fc69bba155`. Its source identities are Android
phone `1.1.0 (8)`, Apple app/widget/watch `1.1.0 (6)`, and Wear OS
`1.1.0 (1000008)`.

| Surface | Source sync | Exact current evidence | Signing and device boundary |
| --- | --- | --- | --- |
| Android phone/tablet | **BLOCKED** | AAB `e16da522aca84776419a999db82a9ddb5a42b15660516bfe6f1fd65cf5a3edcb`; mapping `7e678576d95e36dd8e27cab78a565a47a1539a3caf6f769a283f9aca415a324f` | Bundletool passes and embedded VCS metadata names the exact commit, but the AAB has zero signature entries. The new widget contract has emulator-only coverage; there is no upload-signed/full physical matrix. |
| Wear OS | **BLOCKED** | unsigned AAB `d1088ec635b69258baf5aaa42e42423b930a97a3077f059a2ae59c6d06061e71`; historical signed AAB `ac19a0eab1a60554db309166f135e754c97205b79c4f5182164a8b21594e7dc6` | The unsigned bundle embeds exact revision `ee7c36f`; the signed bundle embeds historical revision `4d9492a`. There is no exact-current signed bundle or physical-watch pass. |
| Apple app/widget/watch | **BLOCKED** | app `279185d6778c7819d889a1f769d8ce2eb10b861790ed4ef2cc833044946aad90`; widget `bd651c05eb19551853fd5dde604fafdc7233f1615f21a9462b20f45199dc3209`; watch `14c419fb71f35097c0fe4396183acb1d701ef229ea55f3608a2982d5bab5c493` | Release simulator executables carry only linker-generated ad-hoc signatures. UUID-matched dSYMs verify, but there is no distribution-signed archive, IPA, or physical Apple pass. |

## Current verification

- The phone bundle reports package `uz.ganikhodjaev.weather`, versionCode `8`,
  versionName `1.1.0`, minSdk `24`, and targetSdk `36`. Bundletool 1.18.3
  validation passed, and embedded VCS metadata resolves to the full commit
  above. Archive inspection found zero signature entries.
- Exact debug APK SHA-256 values are phone
  `e508f060b05f7560bcebbd508a75cda6876235393c259e3cfd0f1a1dc6135a3c`
  and Wear
  `b1f20aa60117c36f5e041777c775dbebabc820f726141bd739a581ef55f35f58`.
  Their Empty/Fresh/Stale emulator matrix is recorded in
  `growth/quality/surface-freshness-2026-08-29.md`. Emulator evidence is not a
  source-synced signed physical pass.
- The Apple executables above are thin arm64 simulator products for iOS 15.0
  app/widget and watchOS 10.0. Their UUIDs are app
  `D7078863-9D24-3DA4-8A12-5646A16555CB`, widget
  `D7B8A1AF-4D6F-324E-A6E9-9E234DED5F23`, and watch
  `A2D5B7BB-72DD-3660-B630-23842D868140`; each matches its dSYM. They have no
  Team Identifier, bound Info.plist, or sealed resources. This is not archive
  or physical evidence.
- A clean full Gradle gate passed 276 actionable tasks, including formatting,
  Android-host and iOS Simulator tests, app unit tests, SQLDelight migration,
  lint-vital/R8, and phone/Wear release bundles. The parsed task reports contain
  232 test executions with zero failures; the separate Swift surface suite adds
  18 passing XCTest cases.
- The retained signed Wear bundle embeds full revision
  `4d9492a343283344ac80f3248a73c6fc752906e1`; the fresh unsigned bundle embeds
  `ee7c36fbd83970e0bc44aa45681c78fc69bba155`. Exact-source provenance therefore
  remains blocked.
- Android protected-value lookup remains unauthorized with `security` status
  `51`. Apple private-key use reports `errSecAuthFailed (-25293)`, and a GUI
  Xcode archive fails at `NimboWidget` CodeSign without producing an archive.
  Existing credentials and identities were not printed, replaced, or reset.

## Dated CI evidence

GitHub Actions run [`33250702915`](https://github.com/4810092/Weather/actions/runs/33250702915)
succeeded on the exact product commit
`ee7c36fbd83970e0bc44aa45681c78fc69bba155` in `20m36s`.
`android-and-shared` completed in `3m59s`; `ios` completed in `20m32s`. The run
retained these workflow artifacts:

| Workflow artifact | Archive digest (SHA-256) | Boundary |
| --- | --- | --- |
| `android-release-unsigned` | `550b0bae8132b3b9e263587b033c97c7a577a88a0fbdbc61cccbf60d0a6f5fa8` | Artifact archive digest, not the inner phone AAB identity; unsigned build only. |
| `wear-release-unsigned` | `247314d495ea7eb7a57a0d36676f03ee29f1ef5973d8e33532ecbefe2bd82636` | Artifact archive digest, not the inner Wear AAB identity; unsigned build only. |
| `ios-simulator-test-results` | `07864344b354c8507ba86230c1e601e95625aac5411b317f309748fadd010f25` | Simulator test-output archive, not a distribution archive. |

This exact-product-source CI run proves the automated workflow only. It is not
signing, store upload, review, publication, physical-device, or
end-user-availability evidence and does not close this gate.

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
