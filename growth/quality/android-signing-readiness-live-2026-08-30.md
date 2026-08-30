# Android signing readiness live recheck — 2026-08-30

Status: **BLOCKED for source-current phone and Wear OS signing**.

Current release authority is
`6f72e70fff6eb7566e06dd862e1fad09055343a4`. Every `e552c0f`, `ed1b791`, `65b2eb9`, `5b98f23`, `aa6496d`, or `44c1892`
build and Keychain statement below is historical, non-transferable evidence;
it does not prove current signed bytes.

Observed at `2026-08-30 04:43:42 +05:00`. This was a read-only audit. No
password, private-key material, protected Keychain value, signing input, or
credential environment value was printed, exported, changed, or reset. No AAB
was built, signed, uploaded, submitted, or published.

After this observation, Apple release signing inputs first advanced the
coordinated manifest authority to `aa6496d0ac9011ff818d2c0dd2ec5c565317400c` without
changing the Android product identity or clearing Keychain authorization. The
`44c1892` statements below remain point-in-time audit evidence; they are not an
instruction to build the superseded revision.

## Source and release identities

- The working tree is clean at repository HEAD
  `76d9c3dd2de142714a2a22219f9778b4e7dfa682`.
- `store/upload-manifest-1.1.0.json` names product/build-input authority
  `44c189209c793cf097fcc293faf8db88033e6902`. A direct Git comparison found no
  changed release-source path between that commit and the current checkout,
  and `scripts/verify_release_artifacts.py --print-source-revision` resolves the
  same full revision.
- Android phone remains package `uz.ganikhodjaev.weather`, version `1.1.0 (8)`,
  min SDK 24, target SDK 36. Wear OS remains the same package, version
  `1.1.0 (1000008)`, min SDK 30, target SDK 36.

## Keystore and Keychain

- The extensionless upload keystore is present at
  `/Users/khasan/work/ganikhodjaev/mykeys`, mode `600`, owner UID 501, size
  2730 bytes, and modification time `2024-03-27 20:27:30 +05:00`. Its outer
  ASN.1 structure is a version-3 PFX/PKCS12 container. No container payload was
  exported.
- The expected key alias remains `weather`. This is independently consistent
  with the key-password record identity and the `META-INF/WEATHER.SF` /
  `META-INF/WEATHER.RSA` entries in retained upload-signed Nimbo bundles.
- Both exact generic-password metadata records exist in
  `/Users/khasan/Library/Keychains/login.keychain-db`:
  - service `IntelliJ Platform APK Signing Keystore Step — KEY_STORE_PASSWORD__/Users/khasan/work/ganikhodjaev/mykeys`, account `KEY_STORE_PASSWORD__/Users/khasan/work/ganikhodjaev/mykeys`, created/modified `2024-03-29 14:47:50Z`;
  - service `IntelliJ Platform APK Signing Keystore Step — KEY_PASSWORD__/Users/khasan/work/ganikhodjaev/mykeys__weather`, account `KEY_PASSWORD__/Users/khasan/work/ganikhodjaev/mykeys__weather`, created/modified `2024-03-29 14:47:51Z`.
- Metadata-only lookups return status 0. `security show-keychain-info` and both
  protected-value reads return status 51, the CLI mapping of
  `errSecAuthFailed (-25293)`. Android Studio's latest recorded PasswordSafe
  access reports the same `-25293` system-keyring failure.
- No Nimbo signing variable is present in the process environment. The
  repository has no release `signingConfig`, and neither repository-local nor
  user Gradle properties provide a Nimbo credential route. No alternate Nimbo
  keystore was found.

## Artifact boundary

The retained signed artifacts are healthy only as historical evidence:

| Artifact | SHA-256 | Embedded revision | Signature |
| --- | --- | --- | --- |
| phone `1.1.0 (7)` | `e476a124c33854873add9061140f68f1720ff098202b52e7758038bb50f5a77c` | `4d9492a343283344ac80f3248a73c6fc752906e1` | `WEATHER`, upload certificate below |
| Wear OS `1.1.0 (1000008)` | `ac19a0eab1a60554db309166f135e754c97205b79c4f5182164a8b21594e7dc6` | `4d9492a343283344ac80f3248a73c6fc752906e1` | `WEATHER`, upload certificate below |

Both pass ordinary `jarsigner -verify`. Their self-signed upload certificate is
valid from 2024-03-27 through 2049-03-21 and has SHA-256
`43:15:48:A4:87:1C:9C:09:0E:EE:80:8A:C3:A3:48:98:F5:D7:86:02:D9:E7:47:DF:E8:1E:22:84:15:AA:C2:52`, matching the pinned Google Play upload identity. Strict verification
returns 4 only for the expected self-signed-chain/timestamp warnings; no
integrity failure was observed.

The current local `app/build/outputs/bundle/release/app-release.aab` and
`wearApp/build/outputs/bundle/release/wearApp-release.aab` have zero JAR
signature entries and embed revision
`dd88d77f0ccce74bb2a3b3390885fa87a642f536`, not the manifest authority. They
are neither source-current candidates nor uploadable artifacts. No retained
AAB currently combines source revision `44c1892…`, the phone/Wear release
identities above, and the pinned upload certificate.

## 05:30 exact-source recheck

A fresh authorization probe against current authority `aa6496d` returned the
same fail-closed result: `security show-keychain-info` and both protected-value
reads exited 51, while a passwordless unlock attempt exited 152 with
`Unable to obtain authorization for this operation`. No protected value was
printed or changed.

The complete Android release gate was nevertheless rerun in a mode-700 detached
checkout at exact commit `aa6496d0ac9011ff818d2c0dd2ec5c565317400c`.
All 241 Gradle tasks passed, including ktlint, shared and Android tests,
SQLDelight migration verification, both release lints, and both release bundle
builds. The resulting unsigned bytes were:

- phone `1.1.0 (8)` SHA-256
  `c80a61365f6d06529a3adb97f41afcede0b0b69a6963a444be200c138daa0be8`;
- Wear OS `1.1.0 (1000008)` SHA-256
  `2b8b06fa6a0c21de2dd40429a746b8b88ff71942670f0814feea4ff7f650b4e8`.

Both pass ZIP integrity and pinned Bundletool 1.18.3 validation and embed only
the exact full source revision. Both intentionally contain zero JAR signature
entries, so these hashes are build-preflight evidence rather than uploadable
candidates.

## Next safe action

Source-current signing cannot proceed noninteractively while the existing login
Keychain rejects both protected reads. The narrow unblock is successful
authorization of that Keychain; the accepted upload keystore, alias, and
certificate must not be replaced or reset.

A post-audit read-only Keychain Access inspection independently exposed
`Unlock Keychain “login”…` for the selected login keychain. The unlock action
was not invoked and no password or biometric prompt was opened.

After both exact protected lookups return status 0, resolve the current full
revision only through `verify_release_artifacts.py --print-source-revision`,
build from a standalone checkout detached at that revision, and retain outputs under a new
mode-700 external directory such as
`/Users/khasan/work/ganikhodjaev/.nimbo-release/android/1.1.0-source-aa6496d/`,
and sign to the manifest filenames `nimbo-phone-1.1.0-vc8.aab` and
`nimbo-wear-1.1.0-vc1000008.aab`. The live JDK 17 `jarsigner` does not support
the previously proposed `-storepass:env` / `-keypass:env` modifiers. The safe
replacement was verified with a disposable keystore: keep xtrace disabled,
omit both password options, pipe the two short-lived shell-variable values to
the tool's password prompts over standard input, and unset them immediately.
No password value may appear in argv, a file, or logs. Verification must
re-open the final bytes, prove the manifest's full revision, identities,
ZIP/JAR integrity, certificate DER SHA-256, Bundletool 1.18.3 validation, and
hashes before any manifest or readiness state can advance.

This record proves local signing readiness and the current authorization
blocker only. It is not evidence of device QA, Play upload, review, rollout, or
public availability.
