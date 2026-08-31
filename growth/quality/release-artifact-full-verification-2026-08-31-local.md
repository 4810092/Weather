# Signed candidate full byte verification — 2026-08-31

Status: **PASS for a fresh local macOS pre-promotion verification; the
committed upload manifest remained BLOCKED at 0/3 during this check**.

At `2026-08-31T13:12:27Z`, repository HEAD
`681f54d16a09d48358f36fa7af770fbe2971b67d` was checked on macOS `26.5.2`
(`25F84`) with Xcode `26.6` (`17F113`), Python `3.11.9`, OpenJDK `17.0.13`,
and pinned Bundletool `1.18.3`.

The verification downloaded draft release `379745439` through the authenticated
GitHub API and required its exact unpublished state:

- `draft=true`, `prerelease=true`, `published_at=null`, `immutable=false`;
- name `[DRAFT STORAGE] Nimbo 1.1.0 signed candidate 2cdd438`;
- storage tag name
  `nimbo-candidate-v1.1.0-2cdd438-run-33381050098` with no Git tag/ref;
- target commit `30a67edf2968878e22bd05497bcd20c64cba7fc7`;
- exactly package asset `537966386` and receipt asset `537966414`.

The separately downloaded assets matched their pinned identities:

| Asset | Size | SHA-256 |
| --- | ---: | --- |
| `signed-candidate-bytes.tar.gz` | 58,073,521 | `60c827ef9f5d2cdc51add5344bd33ab780ab1be3154a3f3da8c22074ddb518d9` |
| `signed-candidate-receipt.json` | 11,711 | `c852c61e07289d2a7a8f211efc91d7f30fab2c3475465ba000625780a21de19c` |

The package was opened into a new temporary directory with manual safe
extraction. Absolute paths, `..`, duplicates, links, special files, unexpected
modes, counts, and expanded sizes were rejected. The admitted tree contained
104 regular files, 88 directories, and 152,161,477 file bytes. Its closed tree
SHA-256 was
`c91ea40ae12fd59aacfee77f03ba75240951b5797c16b23487ce334eb85502fa`.

Bundletool was freshly downloaded from the official `1.18.3` release, reported
version `1.18.3`, and matched SHA-256
`a099cfa1543f55593bc2ed16a70a7c67fe54b1747bb7301f37fdfd6d91028e29`.
The full `scripts/verify_release_artifacts.py` path then ran against an external
temporary manifest representing the intended atomic 3/3 promotion and the
freshly extracted private bytes. It returned `byte_verified=true` for exactly:

- Android phone `1.1.0 (8)`:
  `d4a90676f32745ea314b50ced2c9955e86923589534a1a7654ac6f1207e88a62`;
- Wear OS `1.1.0 (1000008)`:
  `e76d685b20e86f8878be7c9a1a59ac6edb5781ec8e61d5ecd36feb52ddc1cccf`;
- Apple app/widget/watch `1.1.0 (6)`:
  `7466afb1a06f3000ad5d095734082d57cf58e992bdd7a8bed326e90d26ba39d0`.

The Android package IDs, version identities, upload certificate, and embedded
source revision passed through pinned Bundletool. The IPA plus retained
xcarchive passed app/widget/watch bundle, build, source-revision, distribution
certificate, provisioning-profile, entitlement, executable, and dSYM UUID
checks.

This local pass authorizes preparation of one atomic manifest promotion only
when the separate read-only GitHub-hosted macOS verifier is committed in the
same protected path and repeats the check after CI succeeds on `master`. It is
not hosted-run evidence by itself. It is also not physical-device, TestFlight,
Play internal, store upload, processing, review, publication, public
availability, crash-gate, or ranking evidence. The draft remains mutable, so
every later use must recheck the exact release and asset IDs, sizes, and hashes.
