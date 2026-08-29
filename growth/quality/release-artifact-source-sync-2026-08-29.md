# Release artifact source sync — 2026-08-29

Status: **BLOCKED for Android phone, Wear OS, and Apple**.
No artifact was signed, uploaded, submitted, or published by this refresh.

## Decision

The exact product commit is
`97c26cbec570468b4971daa7779e3839aa4c48ce`. Its source identities are Android
phone `1.1.0 (8)`, Apple app/widget/watch `1.1.0 (6)`, and unchanged Wear OS
`1.1.0 (1000008)`.

| Surface | Source sync | Exact current evidence | Signing and device boundary |
| --- | --- | --- | --- |
| Android phone/tablet | **BLOCKED** | AAB `c89b311f2227ecad6ff0f80d8f18529348f52118655b8c70112c2aef48d1c23c`; mapping `0e1624387e2829c90b690a9c288d4140545df68ecbf523d98e36d704b8150988` | Bundletool passes and embedded VCS metadata names the exact commit, but the AAB has zero signature entries. Matching debug bytes passed bounded physical API 25 and emulator API 36 QA; there is no upload-signed/full matrix. |
| Wear OS | **BLOCKED** | historical signed AAB `ac19a0eab1a60554db309166f135e754c97205b79c4f5182164a8b21594e7dc6`; fresh unsigned output `0a0369d132d856c27625efed1b1cb3489b97e41b7c218f33957fe281ec77485c` | Non-signature payloads match except version-control metadata, but the signed bundle embeds revision `4d9492a`, while the unsigned bundle embeds exact revision `97c26cb`. There is no exact-current signed bundle or physical-watch pass. |
| Apple app/widget/watch | **BLOCKED** | app `e6a43119ff23a1ffd3fb0da600bfad9334b94f3ce7a15d244afa9744d853c539`; widget `0df017e7e3f01e04acdba3b7cbb304e442318b2fad4e2ca68b1fba0a391afa94`; watch `71452e1d08c9293aaf0c3b851b7335c8053b3568f06231cba0633c4758b6b462` | Release simulator executables carry only linker-generated ad-hoc signatures. There is no distribution-signed archive, IPA, or physical Apple pass. |

## Current verification

- The phone bundle reports package `uz.ganikhodjaev.weather`, versionCode `8`,
  versionName `1.1.0`, minSdk `24`, and targetSdk `36`. Bundletool 1.18.3
  validation passed, and embedded VCS metadata resolves to the full commit
  above. Archive inspection found zero signature entries.
- Exact debug APK SHA-256
  `5680f2bd8b7f2904cd61831c774614fb1bd147239ae37a78e858209346a180f0`
  was installed on a dedicated physical API 25 phone and an isolated API 36
  emulator; pulled installed bytes matched. Both passed onboarding, live
  Tashkent weather, and ten force-stop/cold starts. API 25 additionally passed
  Bukhara search and localized sharing. API 36 passed true-offline cache,
  failed-refresh fallback, online recovery, and deliberate first-SQL-read
  failure to retry UI. This remains debug-signed bounded QA.
- The Apple executables above are thin arm64 simulator products for iOS 15.0,
  iOS 17.0 widget, and watchOS 10.0. They have no Team Identifier, bound
  Info.plist, or sealed resources. The iOS app passed 40 cold-launch/terminate
  cycles without a captured matching failure, diagnostic, scene-lifecycle
  fault, executor fault, or crash/fatal line. This is not archive or physical
  evidence.
- A clean full Gradle gate passed 214 actionable tasks, including formatting,
  Android-host and iOS Simulator tests, app unit tests, SQLDelight migration,
  lint-vital/R8, and phone/Wear release bundles. A preceding non-clean aggregate
  run failed on a missing derived Gradle in-progress result file; standalone iOS
  tests and the clean full gate passed, so that derived-output event is not
  treated as a product failure or hidden as a clean first attempt.
- Wear application source is unchanged, and entry-by-entry comparison found
  that the retained signed bundle and fresh output match for every
  non-signature entry except `base/root/META-INF/version-control-info.textproto`.
  The retained signed bundle embeds full revision
  `4d9492a343283344ac80f3248a73c6fc752906e1`; the fresh unsigned bundle embeds
  `97c26cbec570468b4971daa7779e3839aa4c48ce`. Exact-source provenance therefore
  remains blocked even though the executable payload is otherwise equivalent.
- Android protected-value lookup remains unauthorized with `security` status
  `51`. Apple private-key use reports `errSecAuthFailed (-25293)`, and a GUI
  Xcode archive fails at `NimboWidget` CodeSign without producing an archive.
  Existing credentials and identities were not printed, replaced, or reset.

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
