# Apple 1.1.0 (5) release artifacts — 2026-08-28

Status: **ARCHIVED, EXPORTED, AND LOCALLY VALIDATED; NOT UPLOADED**. The IPA is
an App Store Connect release candidate. It is not proof of upload, server-side
validation, TestFlight processing, review, or public availability.

## Source and artifact identity

- The checkout was clean at audit start and its full HEAD was
  `d593263e0b1f423d7999bc7402d1eeebcdc266a1`. The archive and IPA do not embed
  a Git commit field, so this records the contemporaneous source checkout but
  is not a cryptographic source-to-binary attestation.
- Artifacts are stored outside the repository at
  `/Users/khasan/work/ganikhodjaev/.nimbo-release/ios/1.1.0-5/` with owner-only
  permissions.
- `archive.log` ends with `** ARCHIVE SUCCEEDED **`; `export.log` ends with
  `** EXPORT SUCCEEDED **` and records the export destination.
- `export/Nimbo.ipa` is `22,510,901` bytes and has SHA-256
  `b36f8fddb225cd616e3833de6037b6434486ec3cbb9ed06f5cc8deb0627ed4dc`.

## Archive ApplicationProperties

The archive was created at `2026-08-28 23:41:06 +0500` with archive version
`2`, name/scheme `Nimbo`, and these application properties:

| Property | Value |
|---|---|
| `ApplicationPath` | `Applications/Nimbo.app` |
| `CFBundleIdentifier` | `uz.ganikhodjaev.weather` |
| `CFBundleShortVersionString` | `1.1.0` |
| `CFBundleVersion` | `5` |
| `Architectures` | `arm64` |
| `Team` | `5SWEZ7HTYP` |
| `SigningIdentity` | `Apple Development: Xasan Ganixodjayev (FJ9HA73H5R)` |

The archive command used automatic signing. The development identity above is
the archive-time identity; the successful App Store Connect export re-signed
the exported IPA with the distribution identity and store profiles documented
below.

## Exported bundle identity

The Info.plists inside the exported IPA report:

| Product | Bundle ID | Version/build | Architecture | Minimum OS |
|---|---|---|---|---|
| iOS/iPadOS app | `uz.ganikhodjaev.weather` | `1.1.0 (5)` | `arm64` | iOS `15.0` |
| Widget extension | `uz.ganikhodjaev.weather.widget` | `1.1.0 (5)` | `arm64` | iOS `17.0` |
| watchOS app | `uz.ganikhodjaev.weather.watchkitapp` | `1.1.0 (5)` | `arm64_32`, `arm64` | watchOS `10.0` |

The watch app declares companion bundle ID `uz.ganikhodjaev.weather`. The main
app's exported Info.plist explicitly contains
`ITSAppUsesNonExemptEncryption = false`.

## Distribution signing and provisioning

- `codesign --verify --deep --strict --verbose=4` passed for the unpacked main
  app, including its embedded widget and watch app: the bundle is valid on disk
  and satisfies its designated requirement.
- All three exported executables are signed by
  `Apple Distribution: Xasan Ganixodjayev (5SWEZ7HTYP)` with team
  `5SWEZ7HTYP`. The leaf certificate is identical for all three bundles:
  SHA-1 `E23D47902ADEE25A1EF16796AA025148709654D2`, SHA-256
  `FD4D8668A7E0F4EB9F64A12B5F0DDEC0075CCDE31DAD50A96E978926E0E743F1`,
  valid through `2027-01-15T07:09:56Z`.
- The embedded store profiles are:

| Product | Profile | UUID | Expires |
|---|---|---|---|
| Main app | `iOS Team Store Provisioning Profile: uz.ganikhodjaev.weather` | `bf8fbeb9-c6c7-411b-9aa9-f2c909d39643` | `2027-01-23T12:41:39Z` |
| Widget | `iOS Team Store Provisioning Profile: uz.ganikhodjaev.weather.widget` | `97aa4de4-ef16-4744-a767-eb6b9774977d` | `2027-01-23T12:41:39Z` |
| Watch | `iOS Team Store Provisioning Profile: uz.ganikhodjaev.weather.watchkitapp` | `12ff3c9b-4cd7-4504-b5c9-3b5507a60847` | `2027-01-23T12:41:39Z` |

The signed entitlements, read from each exported bundle rather than inferred
from source, are:

| Product | Signed entitlements |
|---|---|
| Main app | `application-identifier=5SWEZ7HTYP.uz.ganikhodjaev.weather`; `com.apple.developer.team-identifier=5SWEZ7HTYP`; app group `group.uz.ganikhodjaev.weather`; `beta-reports-active=true`; `get-task-allow=false` |
| Widget | `application-identifier=5SWEZ7HTYP.uz.ganikhodjaev.weather.widget`; same team and app group; `beta-reports-active=true`; `get-task-allow=false` |
| Watch | `application-identifier=5SWEZ7HTYP.uz.ganikhodjaev.weather.watchkitapp`; same team; `beta-reports-active=true`; `get-task-allow=false` |

These values are within the corresponding embedded profiles' allowed
entitlements. In particular, no exported product has the development
`get-task-allow` capability enabled.

## dSYM coverage

Every executable in the exported IPA has an exact architecture-and-UUID match
in the retained archive dSYMs:

| Executable | Architecture | Mach-O UUID | Matching dSYM |
|---|---|---|---|
| `Nimbo` | `arm64` | `E173F712-36D6-3471-8B63-3272920B8290` | `Nimbo.app.dSYM` |
| `NimboWidget` | `arm64` | `46A67F70-FAA1-37B6-8870-A73D15646F58` | `NimboWidget.appex.dSYM` |
| `NimboWatch` | `arm64_32` | `62FEDFDA-C363-3833-9F97-155EB08B4B46` | `NimboWatch.app.dSYM` |
| `NimboWatch` | `arm64` | `01AFDA2B-068C-3D0B-A596-4D04B7C1630F` | `NimboWatch.app.dSYM` |

`DistributionSummary.plist` also reports `symbols=true` for the app, widget,
and watch app, while the export options retain `uploadSymbols=true` for a
future App Store Connect upload.

## Boundary

No App Store Connect build upload, TestFlight distribution, review submission,
or production release was completed. A later internal-TestFlight-only upload
attempt stopped before transfer because this host has no App Store Connect
upload account for team `5SWEZ7HTYP`; see
`internal-track-upload-2026-08-28.md`. Local archive/export/signature/dSYM
success does not close the independent iOS production-crash or physical-iPhone
smoke gates.
