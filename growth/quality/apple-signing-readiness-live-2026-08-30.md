# Apple signing readiness live recheck — 2026-08-30

Checked read-only at `2026-08-29T23:43:44Z` (`2026-08-30 04:43:44 +05`).
No build, archive, export, install, or signing operation was run, and no
certificate, private-key, account, device, or profile secret is recorded here.

## Verdict

Apple `1.1.0 (6)` is **not safely archive-ready through the current checked-in
release command**. The local machine has the required toolchain, the
manifest-pinned Apple Distribution certificate/private-key identity, and valid
exact App Store profiles for the app, widget, and watch. The documented manual
archive command nevertheless forces the obsolete main-app-only profile onto all
three products. A noninteractive distribution archive has therefore not been
proved and should not be attempted through that command.

The current physical matrix is also incomplete: one iPad is an eligible Xcode
destination, but no concrete iPhone or Apple Watch destination is eligible.

## Source and toolchain

- The repository was clean at HEAD
  `76d9c3dd2de142714a2a22219f9778b4e7dfa682`.
- `python3 scripts/verify_release_artifacts.py --print-source-revision`
  resolved the canonical product/build-input revision
  `44c189209c793cf097fcc293faf8db88033e6902`. Later HEAD commits do not alter
  the verifier-owned release inputs.
- The upload manifest remains fail-closed: Apple is `source_sync: blocked`,
  with no current IPA SHA-256 or signing/physical evidence. The JSON verifier
  reports Apple `byte_verified: false`.
- Xcode 26.6 (`17F113`) is selected with the iPhoneOS 26.5 SDK. Java 17,
  Gradle wrapper, `codesign`, `security`, and XcodeGen are available. The data
  volume had approximately 51 GiB free.
- Repository and store-metadata checks passed. CI contains unsigned Apple
  builds only (`CODE_SIGNING_ALLOWED=NO`); it is not an alternative
  distribution-signing path.

## Certificate, key, and profiles

- The installed Apple Distribution certificate matches the manifest-pinned
  SHA-256 and team, and expires on 2027-01-15.
- `security find-identity -v -p codesigning` reports one valid Apple
  Distribution identity and recognizes the matching private-key pair.
  Because this audit deliberately performed no signing, noninteractive
  keychain ACL access remains unproved.
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

## Reproducible signing blocker

`docs/RELEASE.md` supplies one command-line
`PROVISIONING_PROFILE_SPECIFIER='Nimbo App Store 1.0'`. Command-line build
settings apply to every target. Read-only `xcodebuild -showBuildSettings`
confirmed that `Nimbo`, `NimboWidget`, and `NimboWatch` each receive that same
profile specifier while retaining three different bundle IDs. The command is
therefore deterministically incompatible with the current embedded products.

`iosApp/ExportOptions.plist` also uses `signingStyle=automatic`. No configured
Apple-ID entry was visible in the current Xcode account preference list
(although the cached last-selected team matches the manifest). Automatic
profile/cloud-certificate recovery is therefore not a safe noninteractive
fallback. The three installed profiles make a deterministic manual flow
possible once target-specific settings and export mapping are supplied.

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

1. Configure manual Release signing per target with the three exact profiles
   listed above; do not use one global profile specifier.
2. Change the export configuration to manual signing with `Apple Distribution`
   and a `provisioningProfiles` dictionary mapping all three bundle IDs to those
   exact profile names.
3. From a clean checkout, obtain the full revision only through
   `verify_release_artifacts.py --print-source-revision`, then run a bounded
   noninteractive key-access/archive preflight. Stop on any keychain prompt or
   profile substitution.
4. Only after a successful archive/export, verify the retained IPA, xcarchive,
   dSYMs, embedded `NimboSourceRevision`, all embedded profiles, certificate
   fingerprint, entitlements, and Mach-O UUID binding before upload.
5. Re-establish an eligible physical iPhone and paired watch, then complete the
   required TestFlight iPhone/iPad/widget/watch smoke. The current iPad alone
   does not close the matrix.
