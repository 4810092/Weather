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
203 tests passed

python3 scripts/check_repository.py
776 source paths passed

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

git diff --check
passed
```

Regression coverage includes missing bytes, stale Git revisions, dirty product
source, release/filename drift, incomplete blocked records, hash substitution,
unsigned and partially signed AABs, wrong Android signer, unexpected feature
modules, Wear capability drift, self-certifying or aliased evidence records,
Apple source-key omission, missing/mismatched archive products, external
symlink attempts, expired profiles, and positive synthetic Android/Apple
byte-verification paths.

## Remaining trust boundary

An embedded commit and a clean checkout at verification time do not
cryptographically prove that an externally supplied binary was originally
built from a clean tree. The verifier also relies on the invoking operator and
resolved JDK tools not being maliciously replaced. These are explicit build
provenance and operator-trust boundaries, not closed evidence.

Consequently, the first `verified-current` promotion must be produced and
verified from the same clean checkout in a protected GitHub-hosted macOS
release job, with immutable artifact delivery and retained workflow
provenance/attestation. CI and Pages deliberately receive no signing material
today and pass only while all three manifest entries remain blocked. A local or
self-hosted Mac runner is not required.

## Decision

Keep `release_artifact_source_sync`, Android physical smoke, and Apple physical
smoke blocked. Do not begin acquisition or store submission from historical,
unsigned, debug, simulator-only, or receipt-only evidence. The next release
step is the protected hosted signing/provenance path followed by exact-artifact
physical QA; neither is claimed by this report.
