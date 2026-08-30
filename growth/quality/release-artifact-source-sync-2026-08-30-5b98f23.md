# Release artifact source sync — 2026-08-30 hosted-CI provenance hardening

Status: **BLOCKED for Android phone, Wear OS, and Apple; 0/3 current
artifacts byte-verified**.

The authoritative product/build-input commit is
`5b98f23d0320fba4eef77f2d7c43fcbd0afd0594`. It resolves to Android phone
`1.1.0 (8)`, Wear OS `1.1.0 (1000008)`, and Apple app/widget/watch
`1.1.0 (6)`.

## Change boundary

Product behavior and version identities are unchanged from predecessors
`d8786f1784d7bbb9ef26bfec52836b153a89111a`,
`79be641d25387594d44899d817bd24bd3d40ad40`,
`28d61fb997ccfc07b6d3554d7d782e5fdc71d6cb`, and
`aa6496d0ac9011ff818d2c0dd2ec5c565317400c`. The current release-input
revision retains the official SHA-256 pin for the Gradle 9.7.0 wrapper and
strict verification metadata for all 1,714 artifacts exercised by the Android
and fresh-cache `iosArm64` release graphs. The final addition binds the
`junit-bom-5.12.2.module` descriptor that a truly empty Android cache exposed;
its SHA-256 was independently reproduced from the exact Maven Central bytes.
The workflow also seals actual release-source bytes, path inventory, modes,
symlinks, and Git index flags before and after compilation, closing
`skip-worktree` and `assume-unchanged` bypasses without changing product
behavior.

The manual workflow is split into an isolated no-secret exact-source build and
a fresh `release-signing` runner. The build uses a standalone non-local clone,
then requires both AABs to contain the exact manifest revision. Before and
after Android and Apple compilation it forbids dependency-verification override
flags and proves that every release-source path remains sealed. External
actions are pinned to reviewed full commit SHAs. Before any secret is decoded,
the signing runner validates the checksum/inventory-bound unsigned handoff and
the complete non-upload `ExportOptions.plist` contract, including
`destination=export`. It scopes secrets to their exact steps, destroys the
Keychain and decoded signing material before verification, and executes only
SHA-pinned verifier copies outside the checkout. The verifier requires both the
standalone build clone and current checkout release inputs to match this
revision, stages a closed six-entry candidate tree, binds the external R8
mapping to the phone AAB, checks the complete Apple archive/dSYM tree, and
produces only a receipt-bound tar plus schema-v2 receipt.

These controls do not constitute signing, physical-device QA, store upload,
review, rollout, publication, or public availability. Dependency metadata was
bootstrapped from the resolved release graph; it narrows mutable-download risk
but is not independent PGP provenance or a cryptographic build attestation.

## Exact clean-room regression evidence

Both final audits used brand-new standalone `git clone --no-local` checkouts at
the exact authority, removed every remote and alternate, started with empty
dependency/build caches, and used strict dependency verification without
write, refresh, lenient, or override flags. The identical pre/post source seal
covered 256 release entries and produced inventory SHA-256
`65d24b7c2e18db4340ba91d45d153a11fed91659925ba4c51468ef5e8a6cc625`.

- Android used Java 21 and passed all 241 actionable workflow tasks. The
  unsigned phone AAB is 5,449,724 bytes with SHA-256
  `c706b2c7b16923a16bdbbe9624cbaf23963e5bb0834e76c6a7c9641551e07ab2`;
  the unsigned Wear AAB is 2,580,892 bytes with SHA-256
  `a126fa60ce5c8b6001f3c1c38222df19439015dc85266a3df1a0b0e1b60ec869`.
  Both contain the exact full authority revision, have zero signature entries,
  pass ZIP validation, and pass checksum-pinned Bundletool 1.18.3 validation.
- Apple used Xcode 26.6 and Gradle 9.7 and passed the 28-task fresh-cache
  framework build plus the generic iOS Release archive. The unchanged archive
  tree SHA-256 is
  `5c255b8caea952d81cbe792fc9b2554a866c9d0ca40c1c0f129fc1045be0de03`.
  App, widget, and watch are unsigned `1.1.0 (6)` products that embed the exact
  full authority; every executable UUID matches its dSYM and every dSYM passes
  `dwarfdump --verify`.

These unsigned hashes prove only exact-source clean-room compilation and
identity checks. They are not promoted into the upload manifest and are not
upload, signing, physical-device, TestFlight, Play Console, review, rollout, or
availability evidence.

## Current artifact authority

| Surface | Exact identity | Current signed bytes | Decision |
| --- | --- | --- | --- |
| Android phone/tablet | `1.1.0 (8)` | none bound to this revision | **BLOCKED** |
| Wear OS | `1.1.0 (1000008)` | none bound to this revision | **BLOCKED** |
| Apple app/widget/watch | `1.1.0 (6)` | no distribution-signed archive or IPA bound to this revision | **BLOCKED** |

The schema-v2 upload manifest deliberately keeps every current SHA-256,
signing-evidence path, and physical-QA path null. Historical candidates,
unsigned artifacts, and all device results from predecessor revisions remain
non-transferable.

## Remaining unblock

1. Provision the existing signing material into the protected
   `release-signing` environment without sending credentials through chat.
2. Run the manual hosted workflow at this exact authority and retain its
   receipt-bound candidate tar and schema-v2 receipt.
3. Promote the manifest only from the verified receipt and a separate committed
   signing record.
4. Run the exact signed physical phone/tablet/widget/watch matrix and bind its
   evidence to the recomputed artifact SHA-256 values.
5. Upload or submit only after crash, device, policy, and release gates pass.

No artifact was signed, uploaded, submitted, or published by this source-sync
update.
