# Signing readiness — 2026-08-29

Status: **BLOCKED for Android phone, Wear OS, and Apple**.

No artifact was uploaded, submitted, or published during this check. Protected
credentials, private keys, aliases, passwords, and provisioning contents were
not printed, exported, replaced, or reset.

## Current source

The exact product commit is
`24ea3734c105e259374ad3b41a6f7e6476ea70db`.

### Android phone

- The current `1.1.0 (8)` phone AAB SHA-256 is
  `f91d0dce82aad7596118a6563d64b94f9f90daa2550cfb4b345fc3ef966bfdab`;
  mapping SHA-256 is
  `d749110783872a36406c56a99b11d9c67764a7973d767656c3bd6f0ed59addfd`.
- Bundletool 1.18.3 validation passed. The bundle manifest reports package
  `uz.ganikhodjaev.weather`, versionCode `8`, versionName `1.1.0`, minSdk `24`,
  and targetSdk `36`. Embedded VCS metadata identifies the full commit above.
- Archive inspection reports zero signature entries. This is an unsigned local
  release artifact and cannot be uploaded.
- A protected Android signing-value lookup through `security` exits with status
  `51`; no secret was exposed and no credential mutation was attempted.
- Exact debug APK SHA-256
  `968ac46930c6175562855b1e5229a74f9d49c47e3b4da107334d337291530ad4`
  passed fresh-install physical API 25 Russian onboarding, live Tashkent
  without location permission, first-screen Best Time rendering, and 150%
  text. Pulled installed bytes matched and the exercised log path had zero
  matching fatal/ANR entries. Debug signing does not satisfy upload signing or
  the full release-device matrix.

### Wear OS

- The retained signed `1.1.0 (1000008)` AAB SHA-256 is
  `ac19a0eab1a60554db309166f135e754c97205b79c4f5182164a8b21594e7dc6`.
  It embeds VCS revision `4d9492a343283344ac80f3248a73c6fc752906e1`,
  not the current product commit, so it remains a historical signed artifact
  and is not labelled exact-current.
- A fresh exact-commit local Wear output SHA-256
  `6bcf5f9b947cb52887ba2e5c7a48c59cd5a1428c4680c67d63edd6a708bcd439`
  embeds revision `24ea3734c105e259374ad3b41a6f7e6476ea70db` and has zero
  signature entries. The retained signed bundle remains historical and cannot
  be promoted as exact-current.
- No physical-watch pass is recorded.

### Apple app, widget, and watch

Exact-commit Release simulator executables built with
`CODE_SIGNING_ALLOWED=NO`:

| Product | Version | SHA-256 |
| --- | --- | --- |
| iOS app | `1.1.0 (6)` | `421b867257004a15e6042cb98817190570b91cb8c54ac61b3c4e8df049f94ad7` |
| Widget | `1.1.0 (6)` | `e639f0661cd6e96924803d8aa5982706ee0d78c981b7d2d4375b920d2eac1b27` |
| Watch app | `1.1.0 (6)` | `9f29f22984185f2c5cf072357434b442b5e95f90b6c292b9aabfc97993bd689d` |

These products contain only Xcode linker-generated ad-hoc signatures. They
have no Team Identifier, bound Info.plist, sealed resources, distribution
signature, xcarchive, exported IPA, or upload eligibility.

The current source passed the shared iOS simulator test, 18 Swift surface tests,
and fresh Release simulator builds for app, WidgetKit, and watch. The executable
UUIDs are app `6F1E3580-866F-3F7B-B4E2-73A22488CDBF`, widget
`3DF79B39-B3BF-3898-9A5D-DBE9F872C74E`, and watch
`77A04CF4-4666-38C7-AC65-5A658831BA02`; all match their dSYMs. This is simulator
evidence, not signing or physical Apple evidence. The earlier 40-cycle
simulator stability record remains historical to commit `df5f824` and is not
promoted as exact-current proof.

Keychain Access visibly contains valid Apple Development and Apple Distribution
identities with associated private keys. A command-line private-key operation
still reports `errSecAuthFailed (-25293)`. A prior GUI Xcode archive for the
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
