# Release artifact source sync — 2026-08-30 hosted Linux Kotlin closure

Status: **BLOCKED for Android phone, Wear OS, and Apple; 0/3 current
artifacts byte-verified**.

The authoritative product/build-input commit is
`ed1b791b8d1a059e62409713102740e08d014de2`. It resolves to Android phone
`1.1.0 (8)`, Wear OS `1.1.0 (1000008)`, and Apple app/widget/watch
`1.1.0 (6)`.

## Change boundary

The only release-input change from predecessor
`65b2eb939466c493557a3ddac580e913cd0f58f3` is
`gradle/verification-metadata.xml`. Strict verification metadata now binds
1,716 artifacts across the hosted-Linux Android and macOS/`iosArm64` graphs.

After the Linux AAPT2 checksum was added, public GitHub Actions run
`33291190834`, Android job `99202986004`, advanced to the next previously
unseen host payload and rejected
`org.jetbrains.kotlin:kotlin-native-prebuilt:2.4.10` artifact
`kotlin-native-prebuilt-2.4.10-linux-x86_64.tar.gz` under strict verification.
The exact 217,174,119-byte payload was downloaded from the official
[Maven Central artifact](https://repo.maven.apache.org/maven2/org/jetbrains/kotlin/kotlin-native-prebuilt/2.4.10/kotlin-native-prebuilt-2.4.10-linux-x86_64.tar.gz).
Its SHA-1 `5b439b7550031d5da7ca0861f08413042fd7ea8f` matches the authoritative
Maven response header, its computed SHA-256 is
`c9e356e8518144f275f1514cfe38b07db949f93e47e054832b8974fff1fd33e0`,
and `gzip -t` passes. The complete verification-metadata SHA-256 is
`739d003be95abb4d86fdaf8897c1c5fc1b8ff27a7810bfb84e9ac27929de9f69`.

An exhaustive classifier-name scan found no additional high-confidence
macOS-only host payloads. AAPT2 and Kotlin/Native prebuilt now each have both
the resolved macOS and required Linux variants pinned. Remaining Darwin/iOS
entries are target libraries rather than Linux build-host binaries; no
speculative checksums were added.

This release-input change does not alter product behavior, versions, signing
identity, store state, or physical-QA evidence. Standard GitHub-hosted runners
remain the CI authority; no local or self-hosted Mac runner is configured.

## Current evidence boundary

The exact predecessor `65b2eb9` clean-room Android and Apple builds passed, but
their unsigned AAB/archive hashes and embedded revisions do not transfer to
`ed1b791`. The exact current hosted Ubuntu/macOS rerun is therefore required
before CI or any current unsigned build identity can be called verified.

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
2. Provision existing signing material into the protected `release-signing`
   environment without sending credentials through chat.
3. Run the manual hosted workflow and retain its receipt-bound candidate tar
   and schema-v2 receipt.
4. Promote the manifest only from the verified receipt and a separate committed
   signing record.
5. Run the exact signed physical phone/tablet/widget/watch matrix and bind its
   evidence to the retained artifact hashes.

No artifact was signed, uploaded, submitted, or published by this source-sync
update.
