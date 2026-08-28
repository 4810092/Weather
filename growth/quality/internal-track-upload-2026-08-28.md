# Internal-track upload readiness — 2026-08-28

Status: **HISTORICAL VC7/BUILD-5 CHECKPOINT; CURRENT VC8/BUILD-6 SOURCE-SYNC
BLOCKED; NOTHING UPLOADED**.

The upload-path observations below remain valid for the historical artifacts
tested on August 28. They are not a readiness claim for current Android phone
`1.1.0 (8)` or Apple `1.1.0 (6)`, which have no signed artifact, immutable hash,
or matching physical QA. No build was uploaded to TestFlight or Google Play by
these checks.

## Apple / TestFlight

The validated Apple `1.1.0 (5)` archive was exported with an upload-only option
set containing `destination=upload`, `testFlightInternalTestingOnly=true`,
`manageAppVersionAndBuildNumber=false`, and `uploadSymbols=true`. This would
have restricted a successful build to internal TestFlight testing rather than
making it eligible for production submission.

`xcodebuild -exportArchive -allowProvisioningUpdates` stopped at
`IDEDistributionUploadAccountStep` with exit `70` and:

```text
Failed to Use Accounts
App Store Connect access for “5SWEZ7HTYP” is required.
Failed to find an account with App Store Connect access for team 5SWEZ7HTYP
```

The failure occurred before an upload task was created. Local distribution
signing and App Store provisioning remain valid; the missing capability is an
authenticated App Store Connect upload account/API credential on this host.

## Google Play Internal

The active local `gcloud` user credential was tested only against the read-only
Android Publisher reviews endpoint for `uz.ganikhodjaev.weather`. It returned
HTTP `403 PERMISSION_DENIED` with `Request had insufficient authentication
scopes.` No Play edit, artifact upload, track assignment, or rollout request was
created.

An authenticated Android Publisher service account or OAuth credential with the
required Play Console application access and scope is still required.

## Boundary

This evidence distinguishes historically validated vc7/build-5 artifacts from
store-side state. TestFlight and Play Internal remain **not uploaded**. Current
vc8/build-6 artifacts must first be built, signed, hashed, and physically
tested. Production submission and public rollout remain separately gated by
crash, provider, physical-device, and console evidence even after an internal
upload path becomes available.
