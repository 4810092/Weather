# Release artifact source sync — 2026-08-29

Status: **BLOCKED for Android phone and Apple; VERIFIED-CURRENT for Wear OS**.
No artifact was signed, uploaded, submitted, or published by this correction.

## Decision

The signed Android phone `1.1.0 (7)` AAB and Apple `1.1.0 (5)` IPA were built
before the current review-prompt and background-refresh hardening. Their hashes,
signature evidence, and bounded device results remain valid only for those
historical bytes. They cannot be reused as evidence for the current source.

The current product commit is
`f97238beb8d99cea5ed19883b1528dca4923baee`; its source identities are Android phone `1.1.0 (8)` and
Apple app/widget/watch `1.1.0 (6)`. The Wear OS source is unchanged and remains
`1.1.0 (1000008)`. `iosApp/project.yml` is the Apple version source; the
committed Xcode project was regenerated from it with XcodeGen 2.45.3.

| Surface | Current source identity | Source sync | Current local evidence SHA-256 | Current signing evidence | Current physical QA |
| --- | --- | --- | --- | --- | --- |
| Android phone/tablet | `1.1.0 (8)` | **BLOCKED** | unsigned AAB `a631c67df19761964d25dd6fbbdc89b7d9c0ee6d8544ebc23113bcee52043ed9` | 0 signature entries; not upload-signed | bounded current-source debug QA on physical API 25 and API 36 emulator; no signed/full matrix |
| Wear OS | `1.1.0 (1000008)` | **VERIFIED-CURRENT** | `ac19a0eab1a60554db309166f135e754c97205b79c4f5182164a8b21594e7dc6` | retained signed AAB evidence | no physical-watch pass |
| Apple app/widget/watch | `1.1.0 (6)` | **BLOCKED** | app `67a99d6cfc04302c54aeb71fed0a78a6e3c6c9d9aaaca7bb4d0f1e13ed62bb58`; widget `3c65e9c8716a0f0426e19f2682b0d0ab1f1c0c0975106e773694d22600f72a4e`; watch `75a329ed9ad25ae8fe25dcdb54afcd0b5828a9975d2056a9ec28bc079761713a` | simulator-only; no development or distribution signature | no physical Apple pass |

The current phone and Apple rows stay blocked until uploadable release artifacts
are built from the current source, signed with the accepted identities, hashed,
and tested on the required physical devices. The exact-current Apple hashes are
from arm64 Release simulator builds made with `CODE_SIGNING_ALLOWED=NO`; they are
not archives or upload candidates. Signing metadata and protected local material
are present, but current non-interactive private operations fail: the Android
`security` secret lookup exits with status `51`, while Apple archive signing
returns `errSecInternalComponent`. See
`growth/quality/signing-readiness-2026-08-29.md`. The Android hash above is
explicitly local unsigned evidence, not a promoted upload artifact. No
placeholder hash or inherited QA claim is recorded.

## Local source-identity checks

- An isolated exact-commit phone rebuild at
  `f97238beb8d99cea5ed19883b1528dca4923baee` produced
  `build/release/nimbo-phone-1.1.0-vc8-unsigned-f97238b.aab` with SHA-256
  `a631c67df19761964d25dd6fbbdc89b7d9c0ee6d8544ebc23113bcee52043ed9`.
  Bundletool 1.18.3 validation passed; its manifest reports package
  `uz.ganikhodjaev.weather`, versionCode `8`, versionName `1.1.0`, minSdk `24`,
  and targetSdk `36`. Archive inspection reports zero signature entries. The
  companion mapping file
  `build/release/nimbo-phone-1.1.0-vc8-mapping-f97238b.txt` has SHA-256
  `b25870ff3173eb6bccd0ee6bceffba098685d11aa828d27dc9f7a1965ec2c6c7`.
  Both ignored local files are evidence only and are not referenced by the
  upload manifest.
- The Wear release bundle remains versionCode `1000008`; its retained signed
  evidence is unchanged. It is not a substitute for the blocked phone row.
- Exact commit `f97238beb8d99cea5ed19883b1528dca4923baee` passed clean arm64
  Release simulator builds with `CODE_SIGNING_ALLOWED=NO`. The executable
  evidence is:

  | Product | Exact executable path | Bundle identity | Minimum OS | SHA-256 |
  | --- | --- | --- | --- | --- |
  | iOS app | `build/DerivedData-f972-current/Build/Products/Release-iphonesimulator/NimboSimulator.app/NimboSimulator` | `uz.ganikhodjaev.weather`, `1.1.0 (6)` | iOS 15.0 | `67a99d6cfc04302c54aeb71fed0a78a6e3c6c9d9aaaca7bb4d0f1e13ed62bb58` |
  | embedded widget | `build/DerivedData-f972-current/Build/Products/Release-iphonesimulator/NimboSimulator.app/PlugIns/NimboWidget.appex/NimboWidget` | `uz.ganikhodjaev.weather.widget`, `1.1.0 (6)` | iOS 17.0 | `3c65e9c8716a0f0426e19f2682b0d0ab1f1c0c0975106e773694d22600f72a4e` |
  | watch app | `build/DerivedData-f972-current/Build/Products/Release-watchsimulator/NimboWatch.app/NimboWatch` | `uz.ganikhodjaev.weather.watchkitapp`, `1.1.0 (6)` | watchOS 10.0 | `75a329ed9ad25ae8fe25dcdb54afcd0b5828a9975d2056a9ec28bc079761713a` |

  All three are thin arm64 simulator Mach-O executables. The bundles have no
  `_CodeSignature` directory; the executables contain only Xcode's embedded
  ad-hoc linker signature (`TeamIdentifier=not set`, no bound `Info.plist`, no
  sealed resources), not a development or distribution signature. Therefore
  they are simulator-only, not uploadable, and do not provide an xcarchive,
  exported IPA, dSYM validation, or physical Apple smoke evidence.
- A later current-source signing readiness pass confirmed compatible Apple
  profiles and visible identities, but both the full archive and an isolated
  watch archive failed at `codesign`; neither produced an xcarchive.
- A single commit-80 archive retry again failed at widget CodeSign
  with `errSecInternalComponent`, without a provisioning or compile failure;
  no xcarchive was produced.
- The provider-capacity change passed shared Android-host and iOS Simulator
  tests, Kotlin formatting, SQLDelight migration verification, Android phone
  and Wear release bundle builds, and `CODE_SIGNING_ALLOWED=NO` iOS/watchOS
  Release simulator builds with only linker-generated ad-hoc signatures. These
  checks do not create distribution-signed artifacts or physical-device proof.
- The earlier API 25 debug/source smoke is now historical because it predates
  the provider-throttling and cross-path single-flight changes.
- Commit `2004e4f237ce4f176a106d465ecc21b2dc36d741` then passed a bounded
  physical API 25 debug/source smoke for live weather, the fresh-cache
  automatic skip with provider access blocked, explicit manual bypass,
  recovery, and cleanup. Its APK hash is
  `1d3ade497395c349d0fda77e72f76e494da230933d9aa011ac71bb475f48a31e`.
  Debug signing does not satisfy the upload-signed vc8 or release-certificate
  physical gates. That result is historical for the current source, which now
  also changes durable automatic-refresh state and retry handling, saved-location
  cleanup, repository observation windows, and the iOS review-request path.
- Commit `80cdd608b93056edd05e29873da43834a916cd3a` has a bounded historical
  device pass. The exact debug APK SHA-256 is
  `e10aa48ffb5ea7ee2e6a9b43031e623731788a936e23dc94a3480386074d32bc`;
  the installed bytes matched on the physical API 25 phone and API 36 emulator.
  Live and cached weather, true offline fallback and recovery, share chooser,
  legacy navigation contrast, IME resize, light/dark rendering, and landscape
  cutout/three-button paths passed without a captured crash or ANR. The later
  `f97238b` shared review-policy change makes this result historical for the
  current product. It still supports the inherited edge-to-edge implementation
  but does not close current physical QA, the missing upload signature,
  tablet/widget paths, or the paired physical Wear OS matrix.
- Current commit `f97238beb8d99cea5ed19883b1528dca4923baee` was rebuilt as
  debug APK SHA-256
  `7b2f2c12d56fdda293f19317ef6eb6da153213f84b1daeef11fd35f8e9e30edb`.
  That matching-source APK passed bounded QA on the dedicated physical API 25
  phone and API 36 emulator, including onboarding, live city selection/search,
  share chooser, legacy navigation contrast, true-offline cache/error/recovery,
  IME resize, dark landscape, and process stability. It remains debug-signed,
  did not force a Store review prompt, and does not close the upload-signed,
  tablet/widget, or physical Wear OS requirements. See
  `growth/quality/android-current-head-device-smoke-2026-08-29.md`.

## Preserved historical candidates

| Surface | Historical identity | SHA-256 | Evidence boundary |
| --- | --- | --- | --- |
| Android phone/tablet | `1.1.0 (7)` | `e476a124c33854873add9061140f68f1720ff098202b52e7758038bb50f5a77c` | Signed artifact and API 25 physical results remain scoped to vc7 only. |
| Apple app/widget/watch | `1.1.0 (5)` | `b36f8fddb225cd616e3833de6037b6434486ec3cbb9ed06f5cc8deb0627ed4dc` | Distribution signature/archive evidence and the bounded iPad install remain scoped to build 5 only. |

The original evidence is retained without alteration:

- `growth/quality/android-release-artifacts-2026-08-28.md`
- `growth/quality/android-physical-smoke-2026-08-28.md`
- `growth/quality/apple-release-artifacts-2026-08-28.md`
- `growth/quality/apple-runtime-smoke-2026-08-28.md`

## Unblock requirements

1. Build and upload-sign `nimbo-phone-1.1.0-vc8.aab` from the current source;
   verify package, version, certificate, Bundletool output, and SHA-256.
2. Archive and distribution-sign Apple `1.1.0 (6)` from the current source;
   verify the app, widget, watch, dSYM, provisioning, and exported IPA identity.
3. Run the source-synced phone and Apple physical matrices. Historical vc7/build5
   device results may inform coverage but cannot satisfy the new artifact gates.
4. Replace `null` values in `store/upload-manifest-1.1.0.json` only after the
   corresponding evidence files exist and the validator accepts the exact
   source identity.

This is a local release-integrity record, not proof of store processing or
public availability.
