# Release artifact source sync — 2026-08-29

Status: **BLOCKED for Android phone, Wear OS, and Apple**.
No upload or release candidate was signed, uploaded, submitted, or published by
this refresh. This bounded refresh built and inspected unsigned Android release
bundles plus Apple Release simulator products. A subsequent exact-product debug
APK passed the bounded physical API 25 phone smoke described below; protected
release signing was not retried and no signed-device matrix was claimed.

## Decision

The exact product commit is
`9c2dce4200dbba5487c8c458ade4616005fde6e6`. Its source identities are Android
phone `1.1.0 (8)`, Apple app/widget/watch `1.1.0 (6)`, and Wear OS
`1.1.0 (1000008)`.

| Surface | Source sync | Exact current evidence | Signing and device boundary |
| --- | --- | --- | --- |
| Android phone/tablet | **BLOCKED** | full-Git standalone AAB `b7c7acb6e90189e8d73e5b8a5f780bf1d3ab36f43edaf3d5076a1dba4e22d4e5`; mapping `4fdfeefa05c8f71eb3cc2ac538732672ae2c5ba5793ddd35f03bfa7f6b714d18`; physical API 25 debug APK `52146b883a04e4c2d272ea4e3ecc9b1277a8c78c117b547a121de3a7d90c3730` | Bundletool passes and embedded AAB VCS metadata names the exact commit. The debug APK passed clean-install/onboarding/live/offline/recovery/tip-suppression smoke on a physical API 25 phone, but the AAB has zero signature entries. It is not an upload candidate, and no exact-current signed physical matrix, tablet, or widget result exists. Mutable main-worktree `build/outputs` are excluded. |
| Wear OS | **BLOCKED** | full-Git standalone unsigned AAB `2d73fdf1e4fd661a96a699a9fd2ef7b2e989b0f4ab019692ce7c97465673d3fa`; historical signed AAB `ac19a0eab1a60554db309166f135e754c97205b79c4f5182164a8b21594e7dc6` | The unsigned bundle embeds exact revision `9c2dce4` and has zero signature entries; the signed bundle embeds historical revision `4d9492a`. There is no exact-current signed bundle or physical-watch pass. Mutable main-worktree `build/outputs` are excluded. |
| Apple app/widget/watch | **BLOCKED** | app `b7c3ba937658007b07ee9ad8e85ddc892e90f423e7839e0dc112a1070ea04849`; widget `7191acd40334d4d9fec6062bc5023450fefbb55006fbd92f57109f41eb27a7ff`; watch `c310c785750ffa779e5dfdc30384088fca889deddb11417f2b4e8e0e30109728` | Exact-source Release simulator executables carry only linker-generated ad-hoc signatures. UUID-matched dSYMs verify, but there is no exact-current distribution-signed archive, IPA, or physical Apple pass. |

## Current verification

- A standalone local clone with a full `.git` directory checked out detached at
  the full commit above and had no tracked changes. `./gradlew --no-daemon
  :app:bundleRelease :wearApp:bundleRelease` completed successfully with 133
  actionable tasks; 79 executed and 54 came from cache.
- The phone AAB is 5,449,723 bytes and has SHA-256
  `b7c7acb6e90189e8d73e5b8a5f780bf1d3ab36f43edaf3d5076a1dba4e22d4e5`.
  Its R8 mapping is 42,366,574 bytes and has SHA-256
  `4fdfeefa05c8f71eb3cc2ac538732672ae2c5ba5793ddd35f03bfa7f6b714d18`.
  The manifest reports package `uz.ganikhodjaev.weather`, versionCode `8`,
  versionName `1.1.0`, minSdk `24`, and targetSdk `36`.
- The Wear AAB is 2,580,891 bytes and has SHA-256
  `2d73fdf1e4fd661a96a699a9fd2ef7b2e989b0f4ab019692ce7c97465673d3fa`.
  Its manifest reports the same package, versionCode `1000008`, versionName
  `1.1.0`, minSdk `30`, and targetSdk `36`. No Wear mapping file is expected or
  produced because the Wear release build does not enable minification.
- Bundletool 1.18.3 validation exited `0` for both AABs. The checked standalone
  Bundletool JAR SHA-256 is
  `a099cfa1543f55593bc2ed16a70a7c67fe54b1747bb7301f37fdfd6d91028e29`.
  ZIP integrity checks also reported no errors.
- Each AAB contains `base/root/META-INF/version-control-info.textproto` with
  revision `9c2dce4200dbba5487c8c458ade4616005fde6e6`. Each archive has zero
  `META-INF` signature entries. The Gradle task name `signReleaseBundle` does
  not change that archive-level result: neither file is upload-signed.
- This refresh did not read Keychain items, request protected values, or start a
  signing command. The inspected temporary outputs were not promoted as upload
  candidates. The manifest therefore remains fail-closed with null current
  artifact hashes and signing evidence; only its source revision advances.
- Exact-source arm64 Release simulator builds also pass for Apple app
  `1.1.0 (6)`, embedded WidgetKit extension, and watchOS app. Their binary and
  matching dSYM UUIDs are respectively
  `44F5F65F-080A-3F89-B5E5-D052EDF9A219`,
  `4DB04672-B8CF-3BD7-909B-D0869C744ABB`, and
  `58CE68C5-A8B1-32B9-BE4D-BEE8A8C531C0`; `dwarfdump --verify` passes for all
  three. The shared iOS simulator and 18-case Swift surface suites pass. These
  binaries have ad-hoc signatures and no Team Identifier, so they are not an
  archive, IPA, signing, or physical-device result.
- An exact-product debug APK built from the clean current worktree and installed
  on a dedicated physical API 25 phone has SHA-256
  `52146b883a04e4c2d272ea4e3ecc9b1277a8c78c117b547a121de3a7d90c3730`.
  The streamed installed bytes matched. Russian onboarding, Tashkent without
  location permission, live forecast, late-day Best Time boundary, first-tip
  acknowledgement/cold-start suppression, cached offline fallback, and fresh
  network recovery passed. The post-recovery product-scoped log filter had zero
  matching fatal, ANR, TLS, CertPath, or trust-anchor entries. See
  `growth/quality/android-current-product-physical-smoke-2026-08-29.md`. This is
  current-product physical regression evidence under the debug certificate,
  not upload-signing, Play delivery, tablet/widget, or Wear proof.
- Earlier Android debug-device, widget/Wear emulator, Apple simulator, and Apple
  archive-attempt results remain useful regression evidence for their recorded
  commits, but none is relabelled as exact-current signed-release proof. The
  retained signed Wear bundle still embeds revision
  `4d9492a343283344ac80f3248a73c6fc752906e1` and remains historical.

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
