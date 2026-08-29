# Signing readiness — 2026-08-29

Status: **BLOCKED for Android phone, Wear OS, and Apple**.

No artifact was uploaded, submitted, or published during this check. Protected
credentials, private keys, aliases, passwords, and provisioning contents were
not printed, exported, replaced, or reset.

## Current source

The exact product commit is
`97c26cbec570468b4971daa7779e3839aa4c48ce`.

### Android phone

- The current `1.1.0 (8)` phone AAB SHA-256 is
  `c89b311f2227ecad6ff0f80d8f18529348f52118655b8c70112c2aef48d1c23c`;
  mapping SHA-256 is
  `0e1624387e2829c90b690a9c288d4140545df68ecbf523d98e36d704b8150988`.
- Bundletool 1.18.3 validation passed. The bundle manifest reports package
  `uz.ganikhodjaev.weather`, versionCode `8`, versionName `1.1.0`, minSdk `24`,
  and targetSdk `36`. Embedded VCS metadata identifies the full commit above.
- Archive inspection reports zero signature entries. This is an unsigned local
  release artifact and cannot be uploaded.
- A protected Android signing-value lookup through `security` exits with status
  `51`; no secret was exposed and no credential mutation was attempted.
- Exact debug APK SHA-256
  `5680f2bd8b7f2904cd61831c774614fb1bd147239ae37a78e858209346a180f0`
  passed bounded physical API 25 and isolated API 36 emulator QA. Debug signing
  does not satisfy the upload-signing or full release-device matrix.

### Wear OS

- The retained signed `1.1.0 (1000008)` AAB SHA-256 is
  `ac19a0eab1a60554db309166f135e754c97205b79c4f5182164a8b21594e7dc6`.
  It embeds VCS revision `4d9492a343283344ac80f3248a73c6fc752906e1`,
  not the current product commit, so it remains a historical signed artifact
  and is not labelled exact-current.
- A fresh exact-commit local Wear output SHA-256
  `0a0369d132d856c27625efed1b1cb3489b97e41b7c218f33957fe281ec77485c`
  embeds revision `97c26cbec570468b4971daa7779e3839aa4c48ce` and has zero
  signature entries. Its non-signature payload matches the retained signed
  bundle except for the version-control metadata entry, which correctly names
  the different build revision. That payload parity is useful provenance but
  does not turn the historical signed bundle into an exact-current artifact.
- No physical-watch pass is recorded.

### Apple app, widget, and watch

Exact-commit Release simulator executables built with
`CODE_SIGNING_ALLOWED=NO`:

| Product | Version | SHA-256 |
| --- | --- | --- |
| iOS app | `1.1.0 (6)` | `e6a43119ff23a1ffd3fb0da600bfad9334b94f3ce7a15d244afa9744d853c539` |
| Widget | `1.1.0 (6)` | `0df017e7e3f01e04acdba3b7cbb304e442318b2fad4e2ca68b1fba0a391afa94` |
| Watch app | `1.1.0 (6)` | `71452e1d08c9293aaf0c3b851b7335c8053b3568f06231cba0633c4758b6b462` |

These products contain only Xcode linker-generated ad-hoc signatures. They
have no Team Identifier, bound Info.plist, sealed resources, distribution
signature, xcarchive, exported IPA, or upload eligibility.

The exact app completed 40 simulator cold-launch/terminate cycles with zero
launch failures, terminate failures, new matching diagnostic reports, scene-
lifecycle faults, unexpected-executor faults, or matching crash/fatal lines in
the bounded log. This is simulator stability evidence, not signing or physical
Apple evidence.

Keychain Access visibly contains valid Apple Development and Apple Distribution
identities with associated private keys. A command-line private-key operation
still reports `errSecAuthFailed (-25293)`. A GUI Xcode archive for the exact
project, `Nimbo` scheme, and generic iOS device failed in the `NimboWidget`
CodeSign phase with `Command CodeSign failed with a nonzero exit code`; no
authorization prompt, xcarchive, or upload followed. Existing signing material
was left untouched.

At `2026-08-29 10:32 +05:00`, a new read-only readiness check listed the
previously used physical iPad as nominally available, but its lock-state query
timed out and the `--no-auto-mount-ddis` DDI-services query failed while opening
the CoreDevice tunnel. The current iPhone and paired watch remained unavailable.
No DDI was mounted, and no app was built, installed, launched, or removed during
this check, so the exact-current Apple physical matrix could not resume.

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
