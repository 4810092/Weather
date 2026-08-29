# Release artifact source sync — 2026-08-29

Status: **BLOCKED for Android phone, Wear OS, and Apple**.
No artifact was signed, uploaded, submitted, or published by this refresh.

## Decision

The exact product commit is
`df5f82401348a2cca7405feec36c03621af43ea7`. Its source identities are Android
phone `1.1.0 (8)`, Apple app/widget/watch `1.1.0 (6)`, and Wear OS
`1.1.0 (1000008)`.

| Surface | Source sync | Exact current evidence | Signing and device boundary |
| --- | --- | --- | --- |
| Android phone/tablet | **BLOCKED** | AAB `8e590cca0d7e9945874c58a412520142e9d965584236f73cb2836f98a9b9bb19`; mapping `1e87fc59cbfae641bd70e980d33d9696284494f08aff0240d35995d912dc7846` | Bundletool passes and embedded VCS metadata names the exact commit, but the AAB has zero signature entries. Matching debug bytes passed bounded physical API 25 trust/feedback QA; there is no upload-signed/full matrix. |
| Wear OS | **BLOCKED** | historical signed AAB `ac19a0eab1a60554db309166f135e754c97205b79c4f5182164a8b21594e7dc6`; fresh unsigned output `d4df3f2a4f7c315b8afd309ea9cd5d04825c8c9662faa2a7155faf982a155637` | The signed bundle embeds historical revision `4d9492a`; the unsigned bundle embeds exact revision `df5f824`. There is no exact-current signed bundle or physical-watch pass. |
| Apple app/widget/watch | **BLOCKED** | app `d293763bc3dcf0eee73ebac9db1d5f0e4eda7aca7849c6000e3caf714041f5d9`; widget `74b6c6af76d5dc01efb61c2cd66c4fa4b28975704b690bc1371ea21579fd533b`; watch `0ebc1c8f49f390e57bee86420b5be977ead8f086cb4b9a7ed0ab6849c26068c7` | Release simulator executables carry only linker-generated ad-hoc signatures. UUID-matched dSYMs verify, but there is no distribution-signed archive, IPA, or physical Apple pass. |

## Current verification

- The phone bundle reports package `uz.ganikhodjaev.weather`, versionCode `8`,
  versionName `1.1.0`, minSdk `24`, and targetSdk `36`. Bundletool 1.18.3
  validation passed, and embedded VCS metadata resolves to the full commit
  above. Archive inspection found zero signature entries.
- Exact debug APK SHA-256
  `fb039c02964a0cbd49d9702998a2cba967c63bbc9ff368bcda9ea44936f0c753`
  was installed fresh on the dedicated physical API 25 phone and applied as a
  same-certificate preserved-data update on the physical API 36 Samsung; pulled
  installed bytes matched on both. The exercised paths covered no-location
  Tashkent onboarding, retained-state cold start, live weather, localized
  support and Play destinations, and bounded logs with zero matching
  FATAL/ANR lines. This is debug-signed bounded QA, not signed-release proof.
- The Apple executables above are thin arm64 simulator products for iOS 15.0,
  iOS 17.0 widget, and watchOS 10.0. They have no Team Identifier, bound
  Info.plist, or sealed resources. The iOS app passed 40 cold-launch/terminate
  cycles without a captured matching failure, diagnostic, scene-lifecycle
  fault, executor fault, or crash/fatal line. This is not archive or physical
  evidence.
- A clean full Gradle gate passed 214 actionable tasks, including formatting,
  Android-host and iOS Simulator tests, app unit tests, SQLDelight migration,
  lint-vital/R8, and phone/Wear release bundles. The parsed test reports contain
  212 tests with zero failures.
- The retained signed Wear bundle embeds full revision
  `4d9492a343283344ac80f3248a73c6fc752906e1`; the fresh unsigned bundle embeds
  `df5f82401348a2cca7405feec36c03621af43ea7`. Exact-source provenance therefore
  remains blocked.
- Android protected-value lookup remains unauthorized with `security` status
  `51`. Apple private-key use reports `errSecAuthFailed (-25293)`, and a GUI
  Xcode archive fails at `NimboWidget` CodeSign without producing an archive.
  Existing credentials and identities were not printed, replaced, or reset.

## Dated CI evidence

GitHub Actions run `33243395554` succeeded on commit
`79290c6e7cfd3c1ef5e31a557ac7b09840cc72aa` in `13m38s`.
`android-and-shared` completed in `1m49s`; `ios` completed in `13m33s`. The run
retained these workflow artifacts:

| Workflow artifact | Archive digest (SHA-256) | Boundary |
| --- | --- | --- |
| `android-release-unsigned` | `4573dcd34ffac59466220aa0680c5cf5b05cf4b1225815b4eb35ba1246e18bfa` | Artifact archive digest, not the inner phone AAB identity; unsigned build only. |
| `wear-release-unsigned` | `db56216882cfc61e4ff532d7e4929fdb66284478f3cb83a3e9387aaa588d5c6e` | Artifact archive digest, not the inner Wear AAB identity; unsigned build only. |
| `ios-simulator-test-results` | `7754a95741e88087724a4ff1c004425809f754135eb7ccae9c90970468f18917` | Simulator test-output archive, not a distribution archive. |

Commit `79290c6` changes growth documentation, metadata, and creatives while the
exact product source remains `df5f824`. This CI run proves the automated
workflow only; it is not signing, store upload, review, publication, or
end-user-availability evidence and does not close this gate.

See `growth/quality/current-source-crash-hardening-2026-08-29.md` and
`growth/quality/signing-readiness-2026-08-29.md` for the bounded evidence.

## Preserved historical candidates

| Surface | Historical identity | SHA-256 | Evidence boundary |
| --- | --- | --- | --- |
| Android phone/tablet | `1.1.0 (7)` | `e476a124c33854873add9061140f68f1720ff098202b52e7758038bb50f5a77c` | Signed artifact and API 25 physical results remain scoped to vc7 only. |
| Wear OS | `1.1.0 (1000008)`, revision `4d9492a` | `ac19a0eab1a60554db309166f135e754c97205b79c4f5182164a8b21594e7dc6` | Signed bytes remain historical because embedded VCS metadata does not identify the exact current commit; no physical-watch pass exists. |
| Apple app/widget/watch | `1.1.0 (5)` | `b36f8fddb225cd616e3833de6037b6434486ec3cbb9ed06f5cc8deb0627ed4dc` | Distribution archive and bounded iPad evidence remain scoped to build 5 only. |

Those historical artifacts predate the current crash-hardening changes and
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
