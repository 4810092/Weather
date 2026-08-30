# Apple signing readiness live recheck — 2026-08-30

Current release authority is
`704fd893e59d94d8e9a4971313a773b3fa545ab6`. Every `fb591e3`, `6f72e70`, `e552c0f`, `ed1b791`, `65b2eb9`, `5b98f23`, or `aa6496d` build or
Keychain statement below is historical, non-transferable evidence; it does not
prove current distribution-signed bytes.

The initial checkpoint at `2026-08-29T23:43:44Z` (`2026-08-30 04:43:44
+05`) was read-only. Later bounded checks recorded below performed one
disposable failing private-key operation and exact-source unsigned build/archive
actions. No distribution-signed archive, export, install, credential mutation,
or secret disclosure occurred.

## Verdict

Apple `1.1.0 (6)` is **not archive-ready in the current local security
session**. The local machine has the required toolchain, manifest-pinned Apple
Distribution certificate/private-key identity, and valid exact App Store
profiles for the app, widget, and watch. The initial audit also found that the
then-documented command forced one obsolete profile onto all three products;
that configuration defect has since been corrected. Actual private-key use
still fails while the login Keychain is locked, so a noninteractive
distribution archive remains unproved.

The current physical matrix is also incomplete: one iPad is an eligible Xcode
destination, but no concrete iPhone or Apple Watch destination is eligible.

The configuration defect found by this audit was corrected afterward in
product/build-input revision `aa6496d0ac9011ff818d2c0dd2ec5c565317400c`:
Release settings now select the three exact profiles per target and manual
ExportOptions maps the same three bundle IDs. This closes the deterministic
configuration blocker only. It does not prove private-key access, archive,
export, or physical QA.

At `2026-08-30 04:57 +05:00`, a bounded post-correction private-key preflight
copied `/usr/bin/true` into a disposable owner-local temporary directory and
asked `codesign` to replace its signature with the installed manifest-pinned
Apple Distribution identity, with timestamping disabled. `codesign` exited `1`
with `errSecInternalComponent`; no signed temporary result survived, and the
temporary files and directory were removed. This proves that noninteractive
private-key use remains blocked even after the profile-map correction. No app
archive, export, upload, device install, or credential mutation was attempted.
Keychain Access independently showed the selected login keychain action as
`Unlock Keychain “login”…`, confirming that it remained locked. The unlock item
was not invoked and no password or biometric prompt was opened.

## Source and toolchain

- At the initial checkpoint, the repository was clean at HEAD
  `76d9c3dd2de142714a2a22219f9778b4e7dfa682`.
- At that same checkpoint,
  `python3 scripts/verify_release_artifacts.py --print-source-revision` resolved
  the then-current product/build-input revision
  `44c189209c793cf097fcc293faf8db88033e6902`. The current manifest authority is
  `704fd893e59d94d8e9a4971313a773b3fa545ab6`; it inherits the corrected
  per-target signing configuration introduced at `aa6496d` and used by the
  historical 05:30 preflight.
- The upload manifest remains fail-closed: Apple is `source_sync: blocked`,
  with no current IPA SHA-256 or signing/physical evidence. The JSON verifier
  reports Apple `byte_verified: false`.
- Xcode 26.6 (`17F113`) is selected with the iPhoneOS 26.5 SDK. Java 17,
  Gradle wrapper, `codesign`, `security`, and XcodeGen are available. The data
  volume had approximately 51 GiB free.
- Repository and store-metadata checks passed. CI contains unsigned Apple
  builds only (`CODE_SIGNING_ALLOWED=NO`); it is not an alternative
  distribution-signing path.
- Historical run `33296238901` for predecessor authority `fb591e3` passed its
  ordinary unsigned iOS job in 20m38s, including shared simulator tests, Apple
  surface tests, and the unsigned application build. The overall run failed on
  all three Android UI profiles. It provides neither signing nor physical QA
  for current authority `704fd89`.
- Exact-source run
  [`33297505825`](https://github.com/4810092/Weather/actions/runs/33297505825)
  at evidence commit `163ff034c2b93ec302c4c5bee3c49168e0b33ada` passed
  `ios` in 17m25s: shared simulator tests took 5m20s, Apple surface tests took
  2m29s, and the unsigned build took 8m37s. The
  `ios-simulator-test-results` GitHub archive digest is
  `1eea44358a95c8e2b58af184fd1fabd46369aec22a12975e128aa54d122994ba`.
  This is unsigned simulator/build regression evidence, not a distribution-
  signed archive, physical QA, or crash-gate closure; Apple remains `0/1`
  byte-verified and blocked.

## Certificate, key, and profiles

- The installed Apple Distribution certificate matches the manifest-pinned
  SHA-256 and team, and expires on 2027-01-15.
- `security find-identity -v -p codesigning` reports one valid Apple
  Distribution identity and recognizes the matching private-key pair.
  The later disposable `codesign` attempt did exercise the private key and
  failed with `errSecInternalComponent`, proving that current noninteractive
  Keychain authorization is unavailable.
- These installed profiles are valid App Store profiles through 2027-01-23,
  allow the manifest-pinned certificate, use `get-task-allow=false`, expose
  `beta-reports-active=true`, and match their bundle IDs exactly:
  - `uz.ganikhodjaev.weather` →
    `iOS Team Store Provisioning Profile: uz.ganikhodjaev.weather`; includes
    `group.uz.ganikhodjaev.weather`.
  - `uz.ganikhodjaev.weather.widget` →
    `iOS Team Store Provisioning Profile: uz.ganikhodjaev.weather.widget`;
    includes `group.uz.ganikhodjaev.weather`.
  - `uz.ganikhodjaev.weather.watchkitapp` →
    `iOS Team Store Provisioning Profile: uz.ganikhodjaev.weather.watchkitapp`.
- The older `Nimbo App Store 1.0` profile is valid only for the main app and
  lacks the current App Group entitlement. It cannot sign the widget or watch
  bundle and is not the correct current main-app profile.

## Historical configuration blocker and current private-key blocker

At the initial checkpoint, `docs/RELEASE.md` supplied one command-line
`PROVISIONING_PROFILE_SPECIFIER='Nimbo App Store 1.0'`. Command-line build
settings apply to every target. Read-only `xcodebuild -showBuildSettings`
confirmed that `Nimbo`, `NimboWidget`, and `NimboWatch` each receive that same
profile specifier while retaining three different bundle IDs. The command is
therefore deterministically incompatible with the current embedded products.
Revision `aa6496d0ac9011ff818d2c0dd2ec5c565317400c` removed that override and
made the exact per-target mappings authoritative.

The initial `iosApp/ExportOptions.plist` also used `signingStyle=automatic`. No configured
Apple-ID entry was visible in the current Xcode account preference list
(although the cached last-selected team matches the manifest). Automatic
profile/cloud-certificate recovery is therefore not a safe noninteractive
fallback. The current plist now uses deterministic manual signing with all
three exact profiles. A fresh real `codesign` operation nevertheless returns
`errSecInternalComponent`, independently proving the remaining Keychain/private-
key authorization blocker.

## 05:30 exact-source unsigned preflight

The manifest resolver returned
`aa6496d0ac9011ff818d2c0dd2ec5c565317400c` in a clean isolated checkout. A
generic iOS-device Release build with signing disabled completed successfully.
Its packaged app, WidgetKit extension, and watch app all report version
`1.1.0 (6)`, embed the exact full source revision, and remain unsigned as
required for this preflight. Architectures are app `arm64`, widget `arm64`, and
watch `arm64_32` plus `arm64`.

Immediately before that build, the installed manifest-pinned Distribution
identity was again listed as valid, but a real disposable Mach-O signing
operation exited 1 with `errSecInternalComponent`. No archive/export was
attempted in that first pass.

A second clean isolated checkout then completed the Xcode `archive` action with
signing disabled. The resulting `.xcarchive` contains the app, widget, and watch
at `1.1.0 (6)` with exact source `aa6496d`; all products are intentionally
unsigned. All three dSYMs are present, and every executable UUID exactly
matches its corresponding dSYM. The temporary checkout and archive were
removed after inspection. This narrows the remaining distribution archive
blocker to actual private-key authorization; it does not produce a retained
IPA, distribution signature, device result, or upload evidence.

## Live device/CoreDevice state

- Xcode lists one concrete eligible iOS destination: an iPad mini (5th
  generation), iPadOS 26.6. Developer Mode is enabled. CoreDevice reports it
  paired over the local network, with the tunnel disconnected and DDI services
  currently unavailable.
- No concrete iPhone destination is eligible. Known iPhone records are paired
  but currently unavailable; the reachable metadata does not establish a live
  DDI/tunnel path.
- Apple Watch Series 5 on watchOS 10.6.2 is paired but has Developer Mode
  disabled, DDI services unavailable, and tunnel unavailable. Xcode lists only
  the generic watchOS destination, not a concrete watch.

This state is enough to inspect provisioning, but not to claim the required
signed iPhone/iPad/widget/paired-watch runtime matrix. App Store distribution
bytes should be exercised through TestFlight after export and upload; an App
Store profile is not a substitute for a locally installable development or
ad-hoc build.

## Next safe action

1. From a clean checkout, obtain the full revision only through
   `verify_release_artifacts.py --print-source-revision`, then run a bounded
   noninteractive key-access/archive preflight. Stop on any keychain prompt or
   profile substitution.
2. Only after a successful archive/export, verify the retained IPA, xcarchive,
   dSYMs, embedded `NimboSourceRevision`, all embedded profiles, certificate
   fingerprint, entitlements, and Mach-O UUID binding before upload.
3. Re-establish an eligible physical iPhone and paired watch, then complete the
   required TestFlight iPhone/iPad/widget/watch smoke. The current iPad alone
   does not close the matrix.
