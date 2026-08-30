# Release artifact byte verifier — 2026-08-30

Status: **PASS for the fail-closed contract; 0/3 current artifacts verified**.

This change does not sign, upload, submit, review, publish, or make any build
public. Android phone `1.1.0 (8)`, Wear OS `1.1.0 (1000008)`, and Apple
`1.1.0 (6)` remain `blocked` in the upload manifest because their exact-current
signed bytes and matching physical QA do not exist. At this verifier
implementation checkpoint, product/build-input revision
`44c189209c793cf097fcc293faf8db88033e6902` was the manifest authority; the
manifest now advances independently when a later committed release input is
proven by the same contract.

## Defects closed

The prior release matrix treated a syntactically valid SHA-256 plus a Markdown
path as sufficient evidence. A fabricated 64-hex value and generic evidence
file could therefore make a mocked/current row appear `READY` without opening
an AAB or IPA. The standalone artifact command also accepted a hollow blocked
record, and could report historical signed bytes as verified when paired with a
matching stale manifest revision even though the current source identities had
advanced.

The new schema-v2 verifier now fails closed unless all of these conditions hold
in the same invocation:

- the manifest source revision is a real Git commit and the checked-out product
  and build inputs have no tracked or untracked drift from it;
- Gradle, XcodeGen, and generated Xcode identities agree with the manifest
  release, build numbers, and exact filenames;
- every blocked or verified-current artifact has the complete exact schema,
  with historical evidence kept separate and current evidence bound to the
  declared digest; source, signing, and physical evidence must be distinct
  committed Markdown records under `growth/quality`, including after path and
  symlink canonicalization;
- every verified-current file is reopened from an external staging root,
  copied read-only, hashed before and after verification, and its declared
  digest matches the real bytes;
- Android ZIP/module structure, complete JAR signing, pinned upload certificate,
  certificate validity, embedded Git revision, package/version/SDK/Wear
  identity, and pinned Bundletool 1.18.3 validation pass;
- Apple IPA and retained `.xcarchive/Products/Applications/Nimbo.app` topology,
  bundle/version/platform/architecture identity, signed `NimboSourceRevision`,
  distribution/export and archive signer certificates, entitlements,
  provisioning profiles, export options, contained non-symlink products, and
  IPA/archive/dSYM executable UUID binding all pass.

The release matrix and store validator both call the same byte verifier. `READY`
also requires the release/source gate and the matching physical-device gate to
be `pass`, with signing and physical evidence containing the recomputed artifact
digest.

## Verification run

Executed from the repository root on 2026-08-30:

```text
python3 -m compileall -q scripts
python3 -m unittest discover -s scripts/growth/tests -p 'test_*.py'
242 tests passed

python3 scripts/check_repository.py
787 source paths passed

python3 scripts/verify_release_artifacts.py
0 byte-verified, 3 fail-closed blocked

python3 scripts/check_release_qa_matrix.py
passed

python3 scripts/check_localizations.py
passed: 121 resources x 12 Android overlays and 13 Apple surface localizations

python3 scripts/check_store_metadata.py
passed: schema v2, 14 locales, 4 listings, release 1.1.0

python3 scripts/check_store_assets.py
passed: 123 versioned delivery images

python3 scripts/check_store_previews.py
passed

python3 scripts/check_dashboard_report.py
passed

python3 scripts/build_site.py --output build/pages-ci
13 localized pages built

python3 scripts/build_site.py --output build/pages-drafts-ci --include-drafts
34 localized pages built

actionlint .github/workflows/ci.yml .github/workflows/signed-candidate.yml
passed

git diff --check
passed
```

Regression coverage includes missing bytes, stale Git revisions, dirty product
source, release/filename drift, incomplete blocked records, hash substitution,
unsigned and partially signed AABs, wrong Android signer, unexpected feature
modules, Wear capability drift, self-certifying or aliased evidence records,
Apple source-key omission, missing/mismatched archive products, external
symlink attempts, expired profiles, and positive synthetic Android/Apple
byte-verification paths. It now also covers the separate pre-manifest candidate
path, which accepts only a still-blocked committed manifest and snapshots a
closed six-entry root once into isolated staging. It binds the phone mapping to
the exact copy embedded in the AAB; hashes the full archive, dSYM, and export
trees; rejects extra/symlink/special entries and mutation or mutate-restore;
then packages, re-extracts, and rehashes a receipt-bound tar while preserving
verified internal file modes.

The candidate path separately validates the standalone build clone and the
current checkout's release-source paths against the manifest revision. A clean
old clone can no longer hide product/build-input drift on `master`. Receipt
schema v2 also requires exactly phone, Wear, and Apple results, distinct
receipt/package paths, and a final package existence/hash recheck.

## Remaining trust boundary

An embedded commit and a clean checkout at verification time do not
cryptographically prove that an externally supplied binary was originally
built from a clean tree. The verifier also relies on the invoking operator and
resolved JDK tools not being maliciously replaced. These are explicit build
provenance and operator-trust boundaries, not closed evidence.

Consequently, the first `verified-current` promotion must be produced and
verified in the protected two-job GitHub-hosted macOS path: an isolated
no-secret exact-source build followed by a fresh signing runner and immutable,
receipt-bound artifact delivery. All third-party actions are full-SHA pinned,
and the repository validator locks the complete workflow, action blocks, run
bodies, shells, secret environments, and artifact paths. The protected secrets
are not provisioned and the workflow has not run, so ordinary CI and Pages
receive no signing material and all three manifest entries remain blocked. A
local or self-hosted Mac runner is not required for CI; local hardware remains
necessary for the separate physical-device QA gate.

The Gradle wrapper distribution now has the official 9.7.0 SHA-256 pin, normal
and protected workflows use full-commit action pins, and dependency
verification metadata covers all 1,715 artifacts resolved by the complete
hosted-Linux Android and fresh-cache macOS `iosArm64` release graphs. The
Linux-specific AAPT2 runner is pinned to independently checked Google Maven
bytes with SHA-256
`e772a3dae8354764f1b0793903218427f483982445207f2e4ffc8c2026755bd4`.
This materially narrows but
does not eliminate hosted-runner,
toolchain, repository-review, or initially bootstrapped dependency trust; no
separate cryptographic build attestation is claimed.

## Decision

Keep `release_artifact_source_sync`, Android physical smoke, and Apple physical
smoke blocked. Do not begin acquisition or store submission from historical,
unsigned, debug, simulator-only, or receipt-only evidence. The next release
step is provisioning the protected environment after local Keychain unlock,
running the hosted signing/provenance path, promoting the manifest from its
verified receipt, and then completing exact-artifact physical QA. None of those
outcomes is claimed by this report.
