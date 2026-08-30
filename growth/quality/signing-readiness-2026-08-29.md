# Signing readiness — 2026-08-29

Status: **BLOCKED for Android phone, Wear OS, and Apple**.

This is a historical point-in-time checkpoint for `9c2dce4`. Current release
authority is `704fd893e59d94d8e9a4971313a773b3fa545ab6`; current signing truth is
recorded in the Android and Apple live readiness records dated 2026-08-30. Any
use of `current` or `exact-current` below is scoped to this 2026-08-29
checkpoint and does not transfer artifact or device evidence to `704fd89`.

No artifact was uploaded, submitted, or published during this check. Protected
credentials, private keys, aliases, passwords, and provisioning contents were
not printed, exported, replaced, or reset.

## Source at this checkpoint

The exact product commit at this checkpoint was
`9c2dce4200dbba5487c8c458ade4616005fde6e6`.

### Android phone

- The current `1.1.0 (8)` phone AAB SHA-256 is
  `b7c7acb6e90189e8d73e5b8a5f780bf1d3ab36f43edaf3d5076a1dba4e22d4e5`;
  mapping SHA-256 is
  `4fdfeefa05c8f71eb3cc2ac538732672ae2c5ba5793ddd35f03bfa7f6b714d18`.
- Bundletool 1.18.3 validation passed. The bundle manifest reports package
  `uz.ganikhodjaev.weather`, versionCode `8`, versionName `1.1.0`, minSdk `24`,
  and targetSdk `36`. Embedded VCS metadata identifies the full commit above.
- Archive inspection reports zero signature entries. This is an unsigned local
  release artifact and cannot be uploaded.
- Both expected Android Keychain item metadata queries pass, and the existing
  keystore is present with mode `600`. A protected signing-value lookup through
  `security` still exits with status `51`; no password or private value was
  retrieved, and no credential mutation was attempted.
- An earlier source-exact signing attempt used a detached standalone checkout
  at prior product source `9342824` because AGP cannot resolve valid VCS
  metadata through this repository's registered-worktree pointer. That
  standalone build reproduced the then-authoritative prior-source unsigned
  phone and Wear AAB hashes and embedded the full prior revision. Both password
  lookups again returned status `51`
  (`errSecAuthFailed`); the planned JDK 17 `jarsigner` flow would have consumed
  them only through protected environment variables, but it was not started.
  No signed output was created or retained, and all shell variables and
  temporary checkouts were removed. The current `9c2dce4` standalone refresh
  did not read Keychain values or retry signing; it reproduced the unsigned
  hashes above with exact embedded VCS metadata.
- Exact-product debug APK SHA-256
  `52146b883a04e4c2d272ea4e3ecc9b1277a8c78c117b547a121de3a7d90c3730`
  passed fresh-install physical API 25 Russian onboarding, Tashkent without
  location permission, live forecast, the late-day Best Time boundary,
  first-forecast-tip acknowledgement/cold-start suppression, cached offline
  fallback, and fresh network recovery. Pulled installed bytes matched and the
  exercised post-recovery log path had zero matching fatal, ANR, TLS, CertPath,
  or trust-anchor entries. This closes the stale-product physical-phone gap for
  source `9c2dce4`; debug signing still does not satisfy upload signing or the
  full release-device matrix. The earlier APK
  `40f3d15d9eed33761c4e53c86ed91ac26411817811fb93792e1eb65ef0a69227`
  remains prior-product evidence for source `9342824` only.
- The byte-identical exact-current debug APK and pulled API 36 installed bytes
  SHA-256
  `52146b883a04e4c2d272ea4e3ecc9b1277a8c78c117b547a121de3a7d90c3730`
  also passed a fresh no-snapshot Pixel Tablet emulator smoke in Uzbek.
  Landscape onboarding, live forecast, Best Time, durable-tip persistence,
  home-screen widget render/tap, large text, rotation, process health, and
  cleanup passed. This closes the stale-product tablet-layout/widget emulator
  gap only; debug signing and an emulator do not satisfy upload signing,
  physical-tablet QA, or the signed release-device matrix.

### Wear OS

- The retained signed `1.1.0 (1000008)` AAB SHA-256 is
  `ac19a0eab1a60554db309166f135e754c97205b79c4f5182164a8b21594e7dc6`.
  It embeds VCS revision `4d9492a343283344ac80f3248a73c6fc752906e1`,
  not the current product commit, so it remains a historical signed artifact
  and is not labelled exact-current.
- A fresh exact-commit local Wear output SHA-256
  `2d73fdf1e4fd661a96a699a9fd2ef7b2e989b0f4ab019692ce7c97465673d3fa`
  embeds revision `9c2dce4200dbba5487c8c458ade4616005fde6e6` and has zero
  signature entries. The retained signed bundle remains historical and cannot
  be promoted as exact-current.
- No physical-watch pass is recorded.

### Apple app, widget, and watch

Exact-commit Release simulator executables built with
`CODE_SIGNING_ALLOWED=NO`:

| Product | Version | SHA-256 |
| --- | --- | --- |
| iOS app | `1.1.0 (6)` | `b7c3ba937658007b07ee9ad8e85ddc892e90f423e7839e0dc112a1070ea04849` |
| Widget | `1.1.0 (6)` | `7191acd40334d4d9fec6062bc5023450fefbb55006fbd92f57109f41eb27a7ff` |
| Watch app | `1.1.0 (6)` | `c310c785750ffa779e5dfdc30384088fca889deddb11417f2b4e8e0e30109728` |

These products contain only Xcode linker-generated ad-hoc signatures. They
have no Team Identifier, bound Info.plist, sealed resources, distribution
signature, xcarchive, exported IPA, or upload eligibility.

The checkpoint source passed the shared iOS simulator test, 18 Swift surface tests,
and fresh Release simulator builds for app, WidgetKit, and watch. The executable
UUIDs are app `44F5F65F-080A-3F89-B5E5-D052EDF9A219`, widget
`4DB04672-B8CF-3BD7-909B-D0869C744ABB`, and watch
`58CE68C5-A8B1-32B9-BE4D-BEE8A8C531C0`; all match their dSYMs. This is simulator
evidence, not signing or physical Apple evidence. The earlier 40-cycle
simulator stability record remains historical to commit `df5f824` and is not
promoted as exact-current proof.

Keychain Access visibly contains valid Apple Development and Apple Distribution
identities with associated private keys. A command-line private-key operation
still reports `errSecAuthFailed (-25293)`. The device-archive attempt for prior
product source `9342824` failed in the `NimboWidget` CodeSign phase with
`errSecInternalComponent`; no xcarchive or upload followed. The current
`9c2dce4` source was not relabelled with that archive attempt and has only the
simulator build evidence above. The prior-source local archive log SHA-256 is
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

During that prior-source archive attempt, the same iPad reported locked and
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

## Exact credential-path recheck — 2026-08-29 22:56 +05:00

- A metadata-only audit of the earlier signing commands recovered the exact
  Android Studio generic-password records without reading any command output or
  secret value. The keystore-password service/account pair is
  `IntelliJ Platform APK Signing Keystore Step — KEY_STORE_PASSWORD__/Users/khasan/work/ganikhodjaev/mykeys`
  / `KEY_STORE_PASSWORD__/Users/khasan/work/ganikhodjaev/mykeys`; the key-password
  service/account pair is
  `IntelliJ Platform APK Signing Keystore Step — KEY_PASSWORD__/Users/khasan/work/ganikhodjaev/mykeys__weather`
  / `KEY_PASSWORD__/Users/khasan/work/ganikhodjaev/mykeys__weather`.
- Both exact metadata lookups succeeded. Protected reads with stdout and stderr
  fully redirected exited `51` for exact service-plus-account, service-only,
  and account-only lookups. The legacy `weather` / `weather` candidate does not
  exist (`44`), and no Nimbo signing credential environment variables or safe
  alternate Gradle source were present. No password was guessed.
- All five currently available Apple code-sign identities were checked with a
  private-key operation against disposable copied bytes. Every attempt failed
  with `errSecInternalComponent`; the temporary inputs were removed. No keychain
  ACL, identity, certificate, signing setting, or credential was changed.
- This closes the remaining noninteractive fallback audit: exact-current signed
  artifacts cannot be produced until the existing login Keychain authorizes its
  protected values and private keys. It does not justify replacing the accepted
  Android upload identity or any Apple identity.
- The authenticated GitHub repository settings were also checked read-only.
  The repository and its `github-pages` environment contain no Actions secrets
  or variables, so there is no existing CI-held signing fallback. No repository,
  environment, workflow, secret, or variable setting was changed.

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

This record proves only point-in-time local readiness and the signing blocker. It is
not proof of store upload, review, rollout, or public availability.
