# Release artifact source sync — 2026-08-30 hosted Linux verification closure

Status: **HISTORICAL PREDECESSOR CHECKPOINT; it recorded 0/3 byte-verified
artifacts and has been superseded by `ed1b791`**.

The product/build-input commit at this checkpoint was
`65b2eb939466c493557a3ddac580e913cd0f58f3`. It resolves to Android phone
`1.1.0 (8)`, Wear OS `1.1.0 (1000008)`, and Apple app/widget/watch
`1.1.0 (6)`.

## Change boundary

The only release-input change from predecessor
`5b98f23d0320fba4eef77f2d7c43fcbd0afd0594` is
`gradle/verification-metadata.xml`. Strict verification metadata now binds
1,715 artifacts across the hosted-Linux Android and macOS/`iosArm64` graphs.
The added `aapt2-9.3.1-15703166-linux.jar` is 2,369,543 bytes with SHA-256
`e772a3dae8354764f1b0793903218427f483982445207f2e4ffc8c2026755bd4`,
independently downloaded from the official
[Google Maven artifact](https://dl.google.com/dl/android/maven2/com/android/tools/build/aapt2/9.3.1-15703166/aapt2-9.3.1-15703166-linux.jar)
and verified as an intact ZIP. The complete metadata SHA-256 is
`c126775b855f3759f3c94e201dd3dec5569c739b454562ebecd60baecb151ce2`.

Public GitHub Actions run `33289915383`, job `99199625944`, exposed the missing
OS-specific checksum on `ubuntu-24.04`: strict verification rejected that
Linux AAPT2 artifact before the Android build. Its independent `macos-26` iOS
job passed, and the same 241-task Gradle invocation passed on macOS because it
resolved the already-pinned macOS binary. This change addresses that precise
hosted-Linux failure without changing product behavior, versions, signing
identity, store state, or physical-QA evidence. At this historical checkpoint,
a post-fix hosted rerun was still required before its hosted CI result could be
called green. Later exact-source run
[`33297505825`](https://github.com/4810092/Weather/actions/runs/33297505825)
passed at successor authority `704fd893e59d94d8e9a4971313a773b3fa545ab6`;
that later result does not transfer artifact or signing evidence back to this
checkpoint.

## Exact clean-room regression evidence

Both current audits used brand-new standalone `git clone --no-local` checkouts
at the exact authority, removed the remote and any alternates, started with
empty dependency/build caches, and used strict dependency verification without
write, refresh, lenient, or override flags. Identical pre/post seals covered
256 release entries. The canonical compact-JSON inventory SHA-256 is
`ef3ddacdbad75043300e2fb8b0ad6267bcf8894046bb6378df2025ecf8214edb`.
No release-source byte, path, mode, symlink, Git index flag, or non-generated
untracked input changed during either build.

- Android used Java 21 and passed the exact 241-task CI invocation in 14m59s:
  222 tasks executed and 19 came from the new build's cache. The unsigned phone
  AAB is 5,449,724 bytes with SHA-256
  `9a4d113fda6601f18cd6614f5b0797a715c9081fd52ecc41f0ec5401cfb2d8f4`;
  the unsigned Wear AAB is 2,580,892 bytes with SHA-256
  `2801b13123a4da6f70f448cc7f638a4315a08c4e4ab21c73acfb665c48515b45`.
  Both contain the full exact revision, have zero signature entries, pass ZIP
  validation, and pass SHA-pinned Bundletool 1.18.3 validation. The phone R8
  mapping SHA-256 remains
  `4fdfeefa05c8f71eb3cc2ac538732672ae2c5ba5793ddd35f03bfa7f6b714d18`
  and is byte-identical to its embedded copy.
- Apple used Xcode 26.6 and Gradle 9.7 and passed all 28 fresh-cache tasks plus
  the generic iOS Release archive in 7m05s. The unsigned canonical archive-tree
  SHA-256 is
  `8fc6c4693542f15d9518ea2217bf373986e4c10a96ebbb06e39f3dcfef4fe85f`.
  App, widget, and watch all embed the full exact revision. Executable SHA-256
  values are app
  `dfa106ab018f51e49059858e49ad746f481c40af4125c363da9f83139f7c8f02`,
  widget
  `a2d1cda754ff3dfeae785501acb8322339bf61bd8f3e79d5939862fb8a0716a6`,
  and watch
  `43cd07cd7895a7e81738027081d5e19573345599801f6e465e7d90071910848d`.
  Every executable UUID matches its dSYM and every dSYM passes
  `dwarfdump --verify`.

These unsigned hashes prove only exact-source clean-room compilation and
identity checks. They are deliberately not promoted into the upload manifest
and do not prove upload signing, physical-device QA, TestFlight, Play Console,
review, rollout, or public availability.

## Current artifact authority

| Surface | Exact identity | Current signed bytes | Decision |
| --- | --- | --- | --- |
| Android phone/tablet | `1.1.0 (8)` | none bound to this revision | **BLOCKED** |
| Wear OS | `1.1.0 (1000008)` | none bound to this revision | **BLOCKED** |
| Apple app/widget/watch | `1.1.0 (6)` | no distribution-signed archive or IPA bound to this revision | **BLOCKED** |

The schema-v2 upload manifest keeps every current SHA-256, signing-evidence
path, and physical-QA path null. Historical candidates, unsigned artifacts,
and device results from predecessor revisions remain non-transferable.

## Remaining unblock

1. Obtain a green public hosted CI rerun for this exact authority.
2. Provision the existing signing material into the protected
   `release-signing` environment without sending credentials through chat.
3. Run the manual hosted workflow at this exact authority and retain its
   receipt-bound candidate tar and schema-v2 receipt.
4. Promote the manifest only from the verified receipt and a separate committed
   signing record.
5. Run the exact signed physical phone/tablet/widget/watch matrix and bind its
   evidence to the recomputed artifact SHA-256 values.

No artifact was signed, uploaded, submitted, or published by this source-sync
update.
