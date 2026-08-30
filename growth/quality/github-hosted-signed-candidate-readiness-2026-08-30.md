# GitHub-hosted signed-candidate readiness — 2026-08-30

Status: **IMPLEMENTED AND STATICALLY VERIFIED; NOT EXECUTED; 0/3 SIGNED
ARTIFACTS BYTE-VERIFIED**.

## CI placement decision

GitHub's public API reports `4810092/Weather` as a public repository. GitHub's
[Actions billing documentation](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
states that standard GitHub-hosted runners are free for public repositories,
and its [runner table](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job)
lists `macos-26` as a standard public-repository runner. Therefore normal CI
and the protected candidate workflow remain GitHub-hosted; no local or
self-hosted Mac runner is configured. Larger runners are excluded. Artifact
retention remains one day for unsigned inputs and seven days for the verified
candidate/receipt to bound the separate storage allowance. Local Apple
hardware is reserved for physical-device QA and bounded credential export,
not routine CI.

## Implemented boundary

`.github/workflows/signed-candidate.yml` is manual-only and fail-closed to
repository `4810092/Weather` branch `master`, with `contents: read`. It uses two
isolated standard GitHub-hosted `macos-26` jobs. `build-unsigned` has no
environment or secret access. It resolves the blocked manifest's full source
revision, creates a clean standalone non-local clone, runs all 241 Android release tasks,
creates the unsigned Apple archive, and transfers only a checksummed inert
package retained for one day. Checkout credentials are not persisted.
Before and after compilation, it rejects dependency-verification overrides,
unsafe Git index flags, path-set drift, byte drift, symlink or mode drift, and
unexpected untracked release inputs. Both completed AABs must also contain the
exact manifest revision.

`sign-verify` runs on a fresh runner behind `release-signing`. It validates the
declared revision, checksum, and exact unsigned-input inventory before any
secret becomes available. The full `ExportOptions.plist` must equal the
canonical non-upload contract, including `destination=export`, before any
secret is decoded. Signing secrets are scoped to exactly three
consuming steps. The job pins Bundletool 1.18.3 by SHA-256, upload-signs both
Android bundles without putting passwords in argv, imports the pinned Apple
Distribution identity into an ephemeral Keychain, validates the three exact
App Store profiles, and exports Apple build 6.

No mutable repository Python executes while protected material exists. Before
secret decoding, the job checks reviewed SHA-256 pins for
`verify_signed_candidate.py` and `release_artifact_verifier.py` and copies them
to a mode-restricted temporary directory. Immediately after Apple export it
deletes the ephemeral Keychain, keystore, P12, installed profiles, and decoded
profile plists. Only after those deletion checks pass does isolated Python
rehash and execute the reviewed verifier copies. Both the standalone build root
and current checkout release-source paths must match the manifest revision, so
an otherwise valid old clone cannot mask a stale manifest on `master`.

The pre-manifest verifier snapshots a closed six-entry candidate root exactly
once and verifies only the isolated copy. It binds both AABs, IPA, the phone R8
mapping and its byte-identical AAB-embedded copy, ExportOptions, the complete
Apple archive, every dSYM tree, file modes, source revision, and signer/profile
identity. Unexpected files, symlinks, special nodes, concurrent mutation, and
mutate-restore are rejected. Packaging preserves and re-extracts the verified
tree before producing a receipt-bound tarball. Only that tarball and receipt are
uploaded for seven days; raw staging directories and secret material are never
artifact paths. Cleanup always removes the temporary Keychain, profiles,
credentials, unsigned inputs, and build clone.

The workflow has no Git or store write permission. It does not promote the
committed upload manifest, perform physical QA, upload to App Store Connect or
Google Play, submit for review, release, or prove public availability.

## Verification performed

- `actionlint` accepts the workflow.
- Every third-party action is pinned to a reviewed full commit SHA.
- Gradle 9.7.0 is pinned to the official wrapper SHA-256, and checked-in
  verification metadata binds 1,716 resolved hosted-Linux Android and
  fresh-cache macOS `iosArm64` dependency artifacts. The Linux-specific
  `aapt2-9.3.1-15703166-linux.jar` is pinned to independently checked Google
  Maven bytes with SHA-256
  `e772a3dae8354764f1b0793903218427f483982445207f2e4ffc8c2026755bd4`.
  The Linux Kotlin/Native 2.4.10 prebuilt payload is pinned to independently
  checked Maven Central bytes with SHA-256
  `c9e356e8518144f275f1514cfe38b07db949f93e47e054832b8974fff1fd33e0`.
- `scripts/check_repository.py` binds the complete canonical workflow digest,
  complete action-step blocks (including `with` and artifact paths), all run
  bodies, every run shell, and each secret step's exact environment. Its
  adversarial regressions reject automatic triggers, permission escalation,
  mutable actions, xtrace, custom shells, extra environment variables,
  post-secret command changes, and broadened artifact uploads. Functional
  source-seal regressions prove a clean authority tree passes while hidden byte
  drift behind both `skip-worktree` and `assume-unchanged` fails.
- The signed-candidate verifier has positive all-three-artifact coverage and a
  fail-closed regression for any already-promoted manifest. Additional tests
  reject source mutation, unexpected root entries, stale but well-formed
  external mappings, build/current source divergence, receipt/package path
  aliasing, partial artifact inventories, and tar byte/mode drift.
- Current source `ed1b791b8d1a059e62409713102740e08d014de2`
  adds only the Linux Kotlin/Native prebuilt checksum exposed by public CI run
  `33291190834`. Its exact hosted rerun is pending; no current unsigned binary
  hash or hosted-green claim is transferred from its predecessor.
- Predecessor source `65b2eb939466c493557a3ddac580e913cd0f58f3`
  passed a standalone cold-cache Java 21 run of all 241 CI/release tasks.
  Unsigned phone vc8 SHA-256 is
  `9a4d113fda6601f18cd6614f5b0797a715c9081fd52ecc41f0ec5401cfb2d8f4`;
  unsigned Wear vc1000008 SHA-256 is
  `2801b13123a4da6f70f448cc7f638a4315a08c4e4ab21c73acfb665c48515b45`.
  Both embed the exact revision and pass ZIP and pinned Bundletool validation.
- A standalone cold-cache Xcode 26.6 archive at the same predecessor source passed all 28
  fresh-cache Gradle tasks. Its canonical archive-tree SHA-256 is
  `8fc6c4693542f15d9518ea2217bf373986e4c10a96ebbb06e39f3dcfef4fe85f`.
  App, widget, and watch are unsigned `1.1.0 (6)` products, embed the exact
  revision, and have UUID-matched dSYMs that pass `dwarfdump --verify`.
- Those predecessor audits produced the same pre/post 256-entry canonical source
  inventory SHA-256
  `ef3ddacdbad75043300e2fb8b0ad6267bcf8894046bb6378df2025ecf8214edb`.
- Public CI runs `33289915383` and `33291190834` diagnosed the two macOS-hidden
  host payload gaps in sequence: Linux AAPT2 and Linux Kotlin/Native prebuilt.
  A current post-fix hosted rerun is still required before hosted CI can be
  called green.
- At predecessor source
  `5b98f23d0320fba4eef77f2d7c43fcbd0afd0594` passed all 241 release tasks.
  Unsigned phone vc8 SHA-256 is
  `c706b2c7b16923a16bdbbe9624cbaf23963e5bb0834e76c6a7c9641551e07ab2`;
  unsigned Wear vc1000008 SHA-256 is
  `a126fa60ce5c8b6001f3c1c38222df19439015dc85266a3df1a0b0e1b60ec869`.
  Both embed the exact revision and pass ZIP and pinned Bundletool validation.
- A clean standalone cold-cache Xcode 26.6 archive at the same predecessor source passed
  all 28 fresh-cache Gradle tasks. Its canonical archive tree SHA-256 is
  `5c255b8caea952d81cbe792fc9b2554a866c9d0ca40c1c0f129fc1045be0de03`.
  App, widget, and watch are unsigned `1.1.0 (6)` products; architectures are
  app/widget `arm64` and watch `arm64_32` plus `arm64`, all embed the exact
  revision, and every executable UUID matches a verified dSYM.
- Those predecessor audits produced the same pre/post 256-entry source inventory
  SHA-256 `65d24b7c2e18db4340ba91d45d153a11fed91659925ba4c51468ef5e8a6cc625`.

## Current blocker

The workflow has not been dispatched or completed, and no signed candidate
tarball or receipt exists. The unsigned job does not need secrets; the
`sign-verify` job cannot complete until the `release-signing` environment
secrets are provisioned.
The local login Keychain remains locked: protected Android credential reads
return `errSecAuthFailed`, and a real disposable Apple Mach-O signing operation
with the installed pinned identity returns `errSecInternalComponent`. Current
GitHub CLI authentication is also invalid, so protected environment setup
cannot be completed through that CLI session.

The necessary human action is only to unlock the macOS login Keychain and
reauthorize GitHub locally; no password or private key should be sent in chat.
After that, the existing inputs can be exported directly into the protected
environment, the hosted workflow can run, and its receipt can drive a separate
manifest-promotion commit. Until then, the authoritative manifest remains
blocked and the byte-verification count remains `0/3`.
