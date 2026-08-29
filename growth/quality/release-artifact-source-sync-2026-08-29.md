# Release artifact source sync — 2026-08-29

Status: **BLOCKED for Android phone, Wear OS, and Apple**.
No upload or release candidate was signed, uploaded, submitted, or published by
this refresh. The bounded physical smoke used the explicitly identified debug-
signed APK below.

## Decision

The exact product commit is
`9342824db7c0dcadfc4bdfe11f580377c108d968`. Its source identities are Android
phone `1.1.0 (8)`, Apple app/widget/watch `1.1.0 (6)`, and Wear OS
`1.1.0 (1000008)`.

| Surface | Source sync | Exact current evidence | Signing and device boundary |
| --- | --- | --- | --- |
| Android phone/tablet | **BLOCKED** | detached exact-source standalone AAB `e1c65555ed6848e30b335af2312acd37200f741bc42f55e2754a79134b84c5f8`; mapping `df9153ef1bc8973c39df369a2d5fb14825bcd0a04c9ea3ee5a2634e7494d9a6a` | Bundletool passes and embedded VCS metadata names the exact commit, but the AAB has zero signature entries. Exact debug paths passed the bounded physical API 25 first-forecast-tip smoke and the no-snapshot API 24 live/cache/recovery smoke; there is no upload-signed/full physical matrix. Mutable main-worktree `build/outputs` are not this pinned candidate. |
| Wear OS | **BLOCKED** | detached exact-source standalone unsigned AAB `d5c681fb292596b8703cea3a1b40e33d1f9ce450202648777af02d69066437c5`; historical signed AAB `ac19a0eab1a60554db309166f135e754c97205b79c4f5182164a8b21594e7dc6` | The unsigned bundle embeds exact revision `9342824`; the signed bundle embeds historical revision `4d9492a`. Mutable main-worktree `build/outputs` are excluded. There is no exact-current signed bundle or physical-watch pass. |
| Apple app/widget/watch | **BLOCKED** | app `0db3db757a7c0c497f7712c565a9b40e71edf271505cf0d0887c0ff3d59c0a76`; widget `57e2fcafc984c050104ceb29d16ea49a1c97c563522426833094692882edf022`; watch `c6e8ff6543aa4ece0ccab7c7ee740eaef720fa07ab211e3846ca2cb00a48da66` | Exact-source Release simulator executables carry only linker-generated ad-hoc signatures. UUID-matched dSYMs verify, but an exact-source device archive attempt failed in CodeSign and produced no archive or IPA; there is no distribution-signed or physical Apple pass. |

## Current verification

- The phone bundle reports package `uz.ganikhodjaev.weather`, versionCode `8`,
  versionName `1.1.0`, minSdk `24`, and targetSdk `36`. Bundletool 1.18.3
  validation passed, and embedded VCS metadata resolves to the full commit
  above. Archive inspection found zero signature entries.
- The exact phone debug APK SHA-256 is
  `40f3d15d9eed33761c4e53c86ed91ac26411817811fb93792e1eb65ef0a69227`.
  Its installed bytes matched on a physical Android 7.1.1 / API 25 phone after
  a fresh install. The localized first-forecast tip appeared after the first
  successful Tashkent forecast, opened the existing cancelable location picker,
  preserved Tashkent, and stayed acknowledged after a cold start. See
  `growth/quality/android-first-forecast-tip-current-head-2026-08-29.md`. This is
  debug evidence, not a source-synced signed release pass.
- A second exact-product rebuild produced debug APK SHA-256
  `c28a2ca94823a1bbcf54f5aa8e329dd217d4830e2831ae28e252e9646abba6c4`;
  pulled installed bytes matched on a fresh no-snapshot Android 7.0 / API 24
  emulator. Clean no-location Tashkent live weather, the first-forecast tip,
  acknowledgement persistence, online cold start, offline cached refresh, and
  network recovery passed. The bounded filter found zero TLS, CertPath,
  trust-anchor, fatal, or ANR lines. See
  `growth/quality/android-api24-current-product-smoke-2026-08-29.md`.
- Empty/Fresh/Stale phone-widget and round-Wear emulator coverage is retained in
  `growth/quality/surface-freshness-2026-08-29.md` as prior regression evidence
  for commit `ee7c36f`; it is not relabelled as exact-current physical proof.
- The Apple executables above are thin arm64 simulator products for iOS 15.0
  app/widget and watchOS 10.0. Their UUIDs are app
  `93135119-99F1-3E23-A5DC-97ADC7D9E0B7`, widget
  `5E2196A9-DDE9-3429-B003-78BCEA6E5322`, and watch
  `9A50D076-B33B-38C5-99CC-55B29C8ADDFD`; each matches its dSYM. They have no
  Team Identifier, bound Info.plist, or sealed resources. This is not archive
  or physical evidence.
- The exact Android phone and Wear bundles passed Bundletool 1.18.3 validation.
  The exact shared iOS simulator test, 18-case Swift surface suite, and Release
  simulator builds for app, WidgetKit, and watch passed.
- The retained signed Wear bundle embeds full revision
  `4d9492a343283344ac80f3248a73c6fc752906e1`; the fresh unsigned bundle embeds
  `9342824db7c0dcadfc4bdfe11f580377c108d968`. Exact-source signed provenance
  therefore remains blocked.
- Android Keychain item metadata and the existing mode-`600` keystore are
  present, but protected-value lookup remains unauthorized with `security`
  status `51` / `errSecAuthFailed`. A detached standalone checkout at the exact
  product source reproduced both authoritative unsigned AAB hashes and their
  embedded revision; the safe environment-only `jarsigner` path was not started
  after both password values remained unavailable, and no signed output was
  created. An exact-source Apple device archive attempt failed at `NimboWidget`
  CodeSign with `errSecInternalComponent` and produced no archive; its local log
  SHA-256 is
  `6e082e58720080d3cff0c09378f546446298df0f4704711358229e6a6a4659ec`.
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
