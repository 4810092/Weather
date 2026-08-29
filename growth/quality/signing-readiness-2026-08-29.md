# Signing readiness — 2026-08-29

Status: **BLOCKED for Android phone, Wear OS, and Apple**.

No artifact was uploaded, submitted, or published during this check. Protected
credentials, private keys, aliases, passwords, and provisioning contents were
not printed, exported, replaced, or reset.

## Current source

The exact product commit is
`df5f82401348a2cca7405feec36c03621af43ea7`.

### Android phone

- The current `1.1.0 (8)` phone AAB SHA-256 is
  `8e590cca0d7e9945874c58a412520142e9d965584236f73cb2836f98a9b9bb19`;
  mapping SHA-256 is
  `1e87fc59cbfae641bd70e980d33d9696284494f08aff0240d35995d912dc7846`.
- Bundletool 1.18.3 validation passed. The bundle manifest reports package
  `uz.ganikhodjaev.weather`, versionCode `8`, versionName `1.1.0`, minSdk `24`,
  and targetSdk `36`. Embedded VCS metadata identifies the full commit above.
- Archive inspection reports zero signature entries. This is an unsigned local
  release artifact and cannot be uploaded.
- A protected Android signing-value lookup through `security` exits with status
  `51`; no secret was exposed and no credential mutation was attempted.
- Exact debug APK SHA-256
  `fb039c02964a0cbd49d9702998a2cba967c63bbc9ff368bcda9ea44936f0c753`
  passed fresh-install physical API 25 onboarding, live Tashkent, and the
  localized support/rate destination smoke; pulled bytes matched. Broader API
  25/API 36 crash-hardening QA remains historical to commit `97c26cb`. Debug
  signing does not satisfy the upload-signing or full release-device matrix.

### Wear OS

- The retained signed `1.1.0 (1000008)` AAB SHA-256 is
  `ac19a0eab1a60554db309166f135e754c97205b79c4f5182164a8b21594e7dc6`.
  It embeds VCS revision `4d9492a343283344ac80f3248a73c6fc752906e1`,
  not the current product commit, so it remains a historical signed artifact
  and is not labelled exact-current.
- A fresh exact-commit local Wear output SHA-256
  `d4df3f2a4f7c315b8afd309ea9cd5d04825c8c9662faa2a7155faf982a155637`
  embeds revision `df5f82401348a2cca7405feec36c03621af43ea7` and has zero
  signature entries. The retained signed bundle remains historical and cannot
  be promoted as exact-current.
- No physical-watch pass is recorded.

### Apple app, widget, and watch

Exact-commit Release simulator executables built with
`CODE_SIGNING_ALLOWED=NO`:

| Product | Version | SHA-256 |
| --- | --- | --- |
| iOS app | `1.1.0 (6)` | `d293763bc3dcf0eee73ebac9db1d5f0e4eda7aca7849c6000e3caf714041f5d9` |
| Widget | `1.1.0 (6)` | `74b6c6af76d5dc01efb61c2cd66c4fa4b28975704b690bc1371ea21579fd533b` |
| Watch app | `1.1.0 (6)` | `0ebc1c8f49f390e57bee86420b5be977ead8f086cb4b9a7ed0ab6849c26068c7` |

These products contain only Xcode linker-generated ad-hoc signatures. They
have no Team Identifier, bound Info.plist, sealed resources, distribution
signature, xcarchive, exported IPA, or upload eligibility.

The exact app completed 40 simulator cold-launch/terminate cycles with zero
launch failures, terminate failures, new matching diagnostic reports, scene-
lifecycle faults, unexpected-executor faults, or matching crash/fatal lines in
10,252 bounded process-log entries. Its installed executable hash matched the
table above. This is simulator stability evidence, not signing or physical
Apple evidence.

Keychain Access visibly contains valid Apple Development and Apple Distribution
identities with associated private keys. A command-line private-key operation
still reports `errSecAuthFailed (-25293)`. A GUI Xcode archive for the exact
project, `Nimbo` scheme, and generic iOS device failed in the `NimboWidget`
CodeSign phase with `Command CodeSign failed with a nonzero exit code`; no
authorization prompt, xcarchive, or upload followed. Existing signing material
was left untouched.

At `2026-08-29 12:10 +05:00`, a read-only CoreDevice refresh showed the
previously used physical iPad as available and paired. Its lock-state query
succeeded with `unlockedSinceBoot=true`; `ddiServices --no-auto-mount-ddis`
reported the existing developer disk image as compatible and usable. A targeted
application query found no installed Nimbo build. The current iPhone and paired
watch remained unavailable, and `xctrace` still listed the iPad as offline. No
DDI was mounted, and no app was built, installed, launched, or removed during
this check. The iPad connection/DDI sub-blocker is therefore clear, but the
exact-current Apple physical matrix still cannot start without a distribution-
signed build 6 archive.

## Decision

Publication remains blocked until all of the following are true:

1. The existing protected signing identities authorize private-key use without
   replacing or exporting them.
2. The phone AAB is upload-signed from the exact current source and its package,
   version, certificate, Bundletool output, VCS metadata, and hash are verified.
3. Apple app, widget, and watch are archived and distribution-signed from the
   exact current source; provisioning, dSYMs, executable identities, and exported
   IPA are verified.
4. Wear OS is signed again from the exact current revision and its certificate,
   embedded revision, payload, and hash are verified.
5. The signed artifacts pass the required physical phone/tablet/widget/watch
   matrix. No physical Apple pass currently exists.

This record proves only current local readiness and the signing blocker. It is
not proof of store upload, review, rollout, or public availability.
