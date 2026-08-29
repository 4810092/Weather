# Signing readiness — 2026-08-29

Status: **BLOCKED for Android phone, Wear OS, and Apple**.

No artifact was uploaded, submitted, or published during this check. Protected
credentials, private keys, aliases, passwords, and provisioning contents were
not printed, exported, replaced, or reset.

## Current source

The exact product commit is
`9342824db7c0dcadfc4bdfe11f580377c108d968`.

### Android phone

- The current `1.1.0 (8)` phone AAB SHA-256 is
  `e1c65555ed6848e30b335af2312acd37200f741bc42f55e2754a79134b84c5f8`;
  mapping SHA-256 is
  `df9153ef1bc8973c39df369a2d5fb14825bcd0a04c9ea3ee5a2634e7494d9a6a`.
- Bundletool 1.18.3 validation passed. The bundle manifest reports package
  `uz.ganikhodjaev.weather`, versionCode `8`, versionName `1.1.0`, minSdk `24`,
  and targetSdk `36`. Embedded VCS metadata identifies the full commit above.
- Archive inspection reports zero signature entries. This is an unsigned local
  release artifact and cannot be uploaded.
- Both expected Android Keychain item metadata queries pass, and the existing
  keystore is present with mode `600`. A protected signing-value lookup through
  `security` still exits with status `51`; no password or private value was
  retrieved, and no credential mutation was attempted.
- A subsequent source-exact signing attempt used a detached standalone checkout
  at `9342824` because AGP cannot resolve valid VCS metadata through this
  repository's registered-worktree pointer. The standalone build reproduced the
  authoritative unsigned phone and Wear AAB hashes and embedded the full exact
  revision. Both password lookups again returned status `51`
  (`errSecAuthFailed`); the planned JDK 17 `jarsigner` flow would have consumed
  them only through protected environment variables, but it was not started.
  No signed output was created or retained, and all shell variables and
  temporary checkouts were removed.
- Exact debug APK SHA-256
  `40f3d15d9eed33761c4e53c86ed91ac26411817811fb93792e1eb65ef0a69227`
  passed fresh-install physical API 25 Russian onboarding and the exact durable
  first-forecast-tip path. The CTA opened the existing cancelable picker,
  retained Tashkent, persisted acknowledgement, and stayed suppressed after a
  cold start. Pulled installed bytes matched and the exercised log path had zero
  matching fatal/ANR entries. Debug signing does not satisfy upload signing or
  the full release-device matrix.

### Wear OS

- The retained signed `1.1.0 (1000008)` AAB SHA-256 is
  `ac19a0eab1a60554db309166f135e754c97205b79c4f5182164a8b21594e7dc6`.
  It embeds VCS revision `4d9492a343283344ac80f3248a73c6fc752906e1`,
  not the current product commit, so it remains a historical signed artifact
  and is not labelled exact-current.
- A fresh exact-commit local Wear output SHA-256
  `d5c681fb292596b8703cea3a1b40e33d1f9ce450202648777af02d69066437c5`
  embeds revision `9342824db7c0dcadfc4bdfe11f580377c108d968` and has zero
  signature entries. The retained signed bundle remains historical and cannot
  be promoted as exact-current.
- No physical-watch pass is recorded.

### Apple app, widget, and watch

Exact-commit Release simulator executables built with
`CODE_SIGNING_ALLOWED=NO`:

| Product | Version | SHA-256 |
| --- | --- | --- |
| iOS app | `1.1.0 (6)` | `0db3db757a7c0c497f7712c565a9b40e71edf271505cf0d0887c0ff3d59c0a76` |
| Widget | `1.1.0 (6)` | `57e2fcafc984c050104ceb29d16ea49a1c97c563522426833094692882edf022` |
| Watch app | `1.1.0 (6)` | `c6e8ff6543aa4ece0ccab7c7ee740eaef720fa07ab211e3846ca2cb00a48da66` |

These products contain only Xcode linker-generated ad-hoc signatures. They
have no Team Identifier, bound Info.plist, sealed resources, distribution
signature, xcarchive, exported IPA, or upload eligibility.

The current source passed the shared iOS simulator test, 18 Swift surface tests,
and fresh Release simulator builds for app, WidgetKit, and watch. The executable
UUIDs are app `93135119-99F1-3E23-A5DC-97ADC7D9E0B7`, widget
`5E2196A9-DDE9-3429-B003-78BCEA6E5322`, and watch
`9A50D076-B33B-38C5-99CC-55B29C8ADDFD`; all match their dSYMs. This is simulator
evidence, not signing or physical Apple evidence. The earlier 40-cycle
simulator stability record remains historical to commit `df5f824` and is not
promoted as exact-current proof.

Keychain Access visibly contains valid Apple Development and Apple Distribution
identities with associated private keys. A command-line private-key operation
still reports `errSecAuthFailed (-25293)`. The exact-source device archive for
the `Nimbo` scheme failed in the `NimboWidget` CodeSign phase with
`errSecInternalComponent`; no xcarchive or upload followed. The local archive
log SHA-256 is
`6e082e58720080d3cff0c09378f546446298df0f4704711358229e6a6a4659ec`.
Existing signing material was left untouched.

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

During the later exact-source archive attempt, the same iPad reported locked and
`ddiServicesAvailable=false`. The 12:10 unlocked/DDI-usable observation is
therefore retained only as point-in-time history, not as current readiness. No
exact-source Apple build was installed or physically exercised, and the device
matrix cannot resume until signing succeeds and CoreDevice readiness is
re-established at action time.

At `2026-08-29 20:44 +05:00`, a new read-only recheck found the iPad available
and paired in both CoreDevice and Xcode device discovery. It still was not
action-ready: the lock-state and no-auto-mount DDI queries failed because the
device had not been unlocked recently, so current DDI status could not be read.
The iPhone and paired watch remained unavailable. Apple Development and
Distribution identities for team `5SWEZ7HTYP` remained present; one historical
duplicate Development certificate was revoked while the other same-label
identity remained valid. No private-key operation was attempted, so this
connectivity change does not clear signing or physical QA.

## Protected Android signing recheck — 2026-08-29 21:46 +05:00

- The login keychain remained the default and only user keychain in the search
  list. Both expected generic-password item metadata records were readable, but
  `security show-keychain-info` and each protected value lookup exited `51`
  with `errSecAuthFailed (-25293)`. No secret value was obtained, printed,
  persisted, replaced, or reset, and no keychain ACL was changed.
- Android Studio's saved signing configuration still points to the existing
  PKCS12 keystore and expected private-key alias; no alternative Nimbo signing
  environment or Gradle credential source was found. Android Studio independently
  reported that the system keyring was unavailable, and its local log recorded
  `-25293`, so the trusted IDE path has the same authorization blocker.
- The keystore remains readable as metadata with mode `600`, and the expected
  alias remains a `PrivateKeyEntry`. Retained signed phone and Wear bundles pass
  `jarsigner -verify` and share certificate SHA-256
  `43:15:48:A4:87:1C:9C:09:0E:EE:80:8A:C3:A3:48:98:F5:D7:86:02:D9:E7:47:DF:E8:1E:22:84:15:AA:C2:52`,
  consistent with the accepted upload identity. The same protected CLI signing
  route succeeded on 2026-08-28, which isolates the fresh failure to the current
  login-keychain authorization state rather than the keystore, alias, or
  certificate mapping.
- Signing was not started, and no signed exact-source artifact was created. The
  remaining unblock is successful authentication to the existing login keychain;
  existing items, keys, and signing configuration do not need replacement.

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
