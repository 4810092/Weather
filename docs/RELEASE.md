# Release process

This is a chronological release journal. Statements inside a dated paragraph describe
that checkpoint and may be superseded later in the same document. The latest recorded
public state is Android phone/tablet 1.0.2 (6), iOS/iPadOS 1.0.1 (4), and Wear
OS 1.0.2 (1000007). The current coordinated source candidate is 1.1.0: phone 11,
Wear 1000011, and Apple build 9 from source `052d12c7`. It contains the iPad
share popover-anchor fix. Protected run `33616952267` signed and candidate-byte-
verified the exact set, and run `33626711140` durably materialized those exact
bytes. Independent trusted verification remains absent; the committed manifest
is atomically `3/3 blocked`. The prior phone vc10, Wear vc1000010, and Apple build-8 set is
historical internal-delivery evidence. Build 8 passed bounded iPhone QA but
reproduced two iPad Share crashes, so none of its evidence transfers to build 9.
On August 31, the earlier
exact Apple `1.1.0 (6)` IPA completed
Transporter delivery and App Store Connect processing with build state `VALID`
and audience `APP_STORE_ELIGIBLE`. The exact phone `1.1.0 (8)` and Wear
`1.1.0 (1000008)` AABs were published to their separate Google Play Internal
tracks. On September 1 the phone opt-in was accepted and Google Play installed
the Play-signed split set on the dedicated API 25 target; bounded
cold/onboarding/live Tashkent/Best Time/share/process-health checks pass. The
four-account `License testers` group is also attached to Wear Internal and that
track is active, but no physical Wear install exists. These results do not
transfer to the replacement identities. No production submission, rollout,
review, public availability, or complete delivery-linked physical matrix is
claimed. Store consoles remain the authority for live status.

<!-- release-authority-current:start -->
<!-- source_revision:052d12c7dfa6411428d85205d9568462d20ff87d -->
<!-- artifact:android_phone;source_sync=blocked;byte_verified=false;physical_qa_evidence=none -->
<!-- artifact:wear_os;source_sync=blocked;byte_verified=false;physical_qa_evidence=none -->
<!-- artifact:apple;source_sync=blocked;byte_verified=false;physical_qa_evidence=none -->
<!-- physical_gate:android_physical_smoke=blocked;reason_sha256=4862377115e5ad6e46da19f87f0c2001e608892b0247363571ab207fdf68481e -->
<!-- physical_gate:ios_physical_smoke=blocked;reason_sha256=1a728bc136819f5bca6a1762637a56e91b49ee2ee434e3f43b2abfed1c592c55 -->
<!-- release-authority-current:end -->

## Nimbo 1.1.0 successor build-9 signing checkpoint — 2026-09-02

Exact hosted CI run `33615065268` passed all five jobs at evidence head
`0b7104aa69430306fb06af40d504400bd17fb320`. Protected signing run
[`33616952267`](https://github.com/4810092/Weather/actions/runs/33616952267)
then produced and candidate-byte-verified phone vc11, Wear vc1000011, and Apple
build 9 from source `052d12c7dfa6411428d85205d9568462d20ff87d`. Its exact
schema-v3 receipt and hashes are recorded in
[`growth/quality/signed-candidate-run-33616952267.md`](../growth/quality/signed-candidate-run-33616952267.md).

This closes protected signing only. The transient Actions artifact has not yet
been durably materialized or independently trusted-hosted verified, so the
manifest remains `3/3 blocked`. No build-9 store upload, TestFlight/Internal
delivery, physical distribution-signed Share pass, review, rollout, or public
availability is claimed.

## Nimbo 1.1.0 successor build-8 checkpoint — 2026-09-01

Physical TestFlight QA installed exact historical build `1.1.0 (7)` on the
iPhone 14 Pro and passed cold/live/refresh/share-sheet execution, but the copied
share payload contained `0%%`. Source `8fc43b4` normalizes that payload to a
single percent, adds a regression test, and advances phone/Wear/Apple identities
to vc10/vc1000010/build 8. Protected signing run `33493356066` produced and
byte-verified the complete successor set. Materialization run `33498085260`
durably retained the exact package and receipt in an unpublished draft.
Trusted hosted run `33508130379` revalidated the mutable draft and returned
`byte_verified=true` for all three artifacts; the manifest is atomically
current. Post-promotion trusted run `33514410839` repeated the live draft and
byte checks immediately before use. Phone vc10 and Wear vc1000010 are now
available on their separate Play Internal tracks; Apple build 8 completed
Transporter processing, entered the internal TestFlight group, and was
installed on an iPhone 14 Pro. The phone and iPhone bounded smokes passed,
including a copied iOS share payload with one literal percent sign. Production
remains unchanged, and the incomplete physical/crash matrices remain blocked.

## Nimbo 1.1.0 internal store-delivery checkpoint — 2026-08-31

Transporter reported exact Apple build `1.1.0 (6)` as delivered at 21:40
Asia/Tashkent; at 21:51 it still reported `THE APP IS PROCESSING`. A subsequent
authenticated App Store Connect relationship GET returned the same build as
`VALID` and `APP_STORE_ELIGIBLE`, uploaded at 21:47:14. TestFlight beta-group
distribution and installation remain unverified. Google Play reported exact
phone `1.1.0 (8)` available to internal testers at 21:47 on
track `4700083514281298386`, with the existing four-tester `License testers`
group attached. The General Mobile invite opens but has not been accepted, so
there is no Play-delivered install. At 21:49 Play reported exact Wear OS
`1.1.0 (1000008)` available on Internal track `4699242452771231163`, while
the track remained inactive because it has zero tester groups. Production was
untouched. Exact hashes and the processing, tester, installation, and
publication boundaries are recorded in the
[internal store-delivery evidence](../growth/quality/internal-store-delivery-2026-08-31.md).

## Nimbo 1.1.0 Play-delivered phone and Wear tester checkpoint — 2026-09-01

The phone Internal opt-in is accepted. Google Play installed exact version
`1.1.0 (8)` on the dedicated General Mobile API 25 target with installer
`com.android.vending`, API 25 `armeabi-v7a`/`xhdpi`/locale splits, and the
expected Google-managed Play App Signing certificate. Cold onboarding without
location, live Tashkent forecast, Best Time, native share dispatch, and bounded
process-health checks pass. A separate `font_scale=1.3` onboarding and live-
forecast render also passes. The installed TalkBack 12.2 update fails to
initialize on this Android 7.1 device because it references API-26-only classes.
Its signed system TalkBack 5.0.4 was therefore temporarily exposed after the
exact 12.2 update splits were backed up. With the spoken-feedback service
active, Nimbo cold launch and focus traversal reached the forecast plus Share,
Refresh, and Change location with visible focus and TTS AudioTrack activity.
The original 12.2 update and disabled accessibility/TTS settings were restored
exactly. The physical offline/cache/recovery path also passes: the counted
system-UI transition proved
`wifi_on=0` and failed direct-IP reachability before cold start and the localized
saved-weather warning, then `wifi_on=1` and successful direct-IP reachability
before recovery refresh. The existing four-account License testers group is
attached to Wear Internal and the exact vc1000008 track now reports active; no
physical watch install or paired handoff is claimed. A later natural hourly
WorkManager run completed while Google Launcher remained foreground, transferred
17,568 received and 3,504 transmitted DEFAULT-set bytes, returned `SUCCESS`,
and updated the bound physical widget's AQI from 48 to 46. The widget rendered
and opened the live forecast in 215 ms without a Nimbo fatal exception or ANR.
This same physical check exposed the API-25 legacy Android template launcher
icon instead of the Nimbo brand mark, so vc8 must not be promoted to production;
a replacement phone version code is required. See the
[Play-delivered Android record](../growth/quality/play-delivered-android-smoke-2026-09-01.md).

At that historical checkpoint, `byte_verified=true` recorded the exact
vc8/vc1000008/build-6 bytes reopened by the full verifier. A later historical
checkpoint similarly verified vc9/vc1000009/build 7, delivered them internally,
and found the build-7 share defect. The current vc10/vc1000010/build-8 manifest
is atomically `3/3 verified-current`; none of the predecessor evidence can
satisfy successor delivery or physical gates.

## Nimbo 1.1.0 exact phone physical checkpoint — 2026-08-31

Pinned Bundletool produced an upload-key-signed universal APK directly from the
retained phone AAB; its installed bytes matched SHA-256 `e970352d…`. A clean
physical API 25 run passed localized onboarding, Tashkent live forecast, share,
proven-offline cache/fallback, online recovery, and PID-scoped health checks.
This bounded PASS is not Play Internal or Play-app-signing delivery and does
not cover the physical tablet/widget or paired Wear matrix, so the shared
Android/Wear gate remains blocked. See the [exact phone record](../growth/quality/android-phone-vc8-physical-smoke-2026-08-31.md).

## Version identity

- Product name: Nimbo.
- Android application ID: `uz.ganikhodjaev.weather` — never change.
- iOS bundle ID: `uz.ganikhodjaev.weather`.
- Every Android upload must exceed the highest store-accepted code; at this checkpoint phone must be greater than 6 and Wear OS greater than 1000007.
- iOS marketing version starts at 1.0; build numbers are monotonically increasing.

## Nimbo 1.1.0 local full-byte promotion checkpoint — 2026-08-31

A fresh local macOS run downloaded unpublished draft release `379745439`,
required its exact draft/prerelease state and two-asset inventory, safely
extracted the 104-file closed tree, and verified pinned Bundletool `1.18.3`.
The full verifier returned `byte_verified=true` for phone AAB
`d4a90676f32745ea314b50ced2c9955e86923589534a1a7654ac6f1207e88a62`,
Wear AAB
`e76d685b20e86f8878be7c9a1a59ac6edb5781ec8e61d5ecd36feb52ddc1cccf`,
and Apple IPA
`7466afb1a06f3000ad5d095734082d57cf58e992bdd7a8bed326e90d26ba39d0`.

At this local-verifier checkpoint, the manifest promoted the complete set
atomically to `verified-current`; all physical-QA evidence was still null and
top-level status remained `draft-blocked`. Successful CI on current `master`
must be followed by the
protected no-checkout staging job and separate read-only macOS verifier. This is not store upload,
internal delivery, physical QA, crash diagnosis, publication, or ranking
evidence. See the [full-verification record](../growth/quality/release-artifact-full-verification-2026-08-31-local.md).

## Nimbo 1.1.0 hosted draft-materialization checkpoint — 2026-08-31

Manual GitHub-hosted
[run `33392732428`](https://github.com/4810092/Weather/actions/runs/33392732428)
passed from `master` at evidence head
`30a67edf2968878e22bd05497bcd20c64cba7fc7`. It bound the exact successful
signing run/artifact/workflow, verified source artifact ZIP SHA-256
`f1754ff767d908cd6be5ce5652e05e6f3dc8721ffa1b0db303d72a5d27cf5478`,
safely admitted the expected package/receipt inventory and bindings, and stored
only those two files in unpublished draft release `379745439`.

Package asset `537966386` is 58,073,521 bytes with SHA-256
`60c827ef9f5d2cdc51add5344bd33ab780ab1be3154a3f3da8c22074ddb518d9`;
receipt asset `537966414` is 11,711 bytes with SHA-256
`c852c61e07289d2a7a8f211efc91d7f30fab2c3475465ba000625780a21de19c`.
The workflow re-read the release and asset APIs and required `draft=true`,
`prerelease=true`, `published_at=null`, target
`30a67edf2968878e22bd05497bcd20c64cba7fc7`, and no Git tag.

This is a durable draft-materialization PASS relative to the expiring Actions
artifact, not release readiness. GitHub reports the draft as mutable rather
than immutable, and the single Ubuntu job did not run the complete verifier.
The later local checkpoint above supplies the atomic `3/3 verified-current`
promotion; the protected hosted chain remains mandatory and physical QA, store
delivery, crash diagnosis, review, release, and availability remain
independent. See the
[materialization record](../growth/quality/release-materialization-2026-08-31-run-33392732428.md).

## Nimbo 1.1.0 hosted signed-candidate checkpoint — 2026-08-31

Product/build-input authority
`2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652` remains unchanged. Protected
GitHub Actions
[run `33381050098`](https://github.com/4810092/Weather/actions/runs/33381050098),
attempt 1 at evidence head
`dd6e275e840947ec6b22b9485ebeb63d5eaa320c`, passed both hosted macOS jobs
with all 8/8 protected signing inputs. It produced schema-v3 receipt-bound
candidates for phone `1.1.0 (8)`, Wear `1.1.0 (1000008)`, and Apple app/widget/
watch `1.1.0 (6)`.

The exact signed hashes are phone AAB
`d4a90676f32745ea314b50ced2c9955e86923589534a1a7654ac6f1207e88a62`,
Wear AAB
`e76d685b20e86f8878be7c9a1a59ac6edb5781ec8e61d5ecd36feb52ddc1cccf`,
and Apple IPA
`7466afb1a06f3000ad5d095734082d57cf58e992bdd7a8bed326e90d26ba39d0`.
The package SHA-256 is
`60c827ef9f5d2cdc51add5344bd33ab780ab1be3154a3f3da8c22074ddb518d9`
and closed-tree SHA-256 is
`c91ea40ae12fd59aacfee77f03ba75240951b5797c16b23487ce334eb85502fa`.
The GitHub ZIP matched its API digest, the archive inventory was safely
extracted, and all three candidates passed an independent second verifier run.
The exact hosted files and metadata are retained outside Git under a complete
checksum manifest; the non-secret receipt is committed.

This closes protected signing and pre-manifest candidate verification only.
At this checkpoint the schema-v2 upload manifest remained fail-closed because
there was no hosted materialization route to the private retained bytes. The
later draft-materialization and local full-byte checkpoints above close that
storage and manifest-promotion gap. The protected staged hosted verifier is
mandatory for each current master. The Android candidate still needs an upload-derived
physical phone/tablet/widget/Wear matrix. The App Store-profile IPA must be
uploaded unchanged and exercised through TestFlight; it is not directly
installable. Crash diagnosis, store processing, review, rollout, and public
availability are not claimed. See the [signed-candidate
record](../growth/quality/signed-candidate-run-33381050098.md) and [current
source-sync record](../growth/quality/release-artifact-source-sync-2026-08-31-2cdd438.md).

## Historical Nimbo 1.1.0 provider decoding checkpoint — 2026-08-30 (superseded)

The authoritative product/build-input revision is
`2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652`. It keeps phone `1.1.0 (8)`,
Wear `1.1.0 (1000008)`, and Apple `1.1.0 (6)` unchanged. It inherits the
pinned dependency graph, deterministic locale/UI harness, API 24 desugaring,
and standard hosted API 24/API 36 phone/tablet jobs from predecessor
`704fd893e59d94d8e9a4971313a773b3fa545ab6`. It adds tolerant decoding for
omitted optional Open-Meteo forecast/AQI arrays while keeping required
weather/time inputs fail-closed. Fourteen Android-host and twelve iOS Simulator
provider tests pass, including cache/timezone preservation on rejected required
rows. At evidence head `fb877d30b2179a489f5ce18dd06d892461436540`, hosted
CI [run #117](https://github.com/4810092/Weather/actions/runs/33300967788)
(`33300967788`) succeeded for this exact source authority. All five jobs passed:
Android/shared in `5m05s`; Compose UI API 24 phone `5/5` in `2m36s`, API 36
phone `5/5` in `3m48s`, and API 36 tablet `5/5` in `4m18s`; and iOS in `23m59s`,
including `18/18` surface tests. The six archived outputs are unsigned/test
evidence only. No predecessor AAB/archive hash, signed artifact, physical QA,
crash diagnosis, or store state transfers. At this dated checkpoint the
protected signed workflow had not run, the environment had `4/8` required
secrets, and the manifest was `0/3` byte-verified. That signing state is
superseded by the August 31 checkpoint above: protected run `33381050098`
passed with `8/8` inputs and verified `3/3` candidate bytes, while the manifest
correctly remains `0/3 verified-current`.
An isolated exact-`2cdd438` debug APK and its pulled installed bytes share
SHA-256
`d66c8f0f9b05232cf484bd95223328a44f2a0bddf1d2f76817ef9504f87fe047`
and passed a bounded physical General Mobile Android 7.1.1 / API 25 smoke:
denied-location fallback, Bukhara search, live forecast, cached-offline warning,
recovery, populated home widget render/tap, process health, and cleanup. This
uses the debug certificate and is not an upload-signed artifact, Play delivery,
physical-tablet, or paired Wear result. It does not change the blocked gate or
the `0/3` upload manifest. See the
[exact-current physical record](../growth/quality/android-current-product-physical-smoke-2026-08-30-2cdd438.md).
The current boundary is recorded in the
[source-sync evidence](../growth/quality/release-artifact-source-sync-2026-08-30-2cdd438.md)
and [schema-v2 upload manifest](../store/upload-manifest-1.1.0.json).

## Historical Nimbo 1.1.0 hosted Linux verification closure — 2026-08-30

The product/build-input revision at this predecessor checkpoint was
`65b2eb939466c493557a3ddac580e913cd0f58f3`. It keeps phone `1.1.0 (8)`,
Wear `1.1.0 (1000008)`, and Apple `1.1.0 (6)` unchanged. Strict dependency
metadata now covers 1,715 artifacts across the hosted-Linux Android and
macOS/`iosArm64` graphs. The only new release input is the Linux AAPT2 runner;
its official Google Maven bytes have SHA-256
`e772a3dae8354764f1b0793903218427f483982445207f2e4ffc8c2026755bd4`.
This addresses the precise Ubuntu verification failure in public CI run
`33289915383` without changing product behavior.

Independent standalone empty-cache runs at this exact revision passed all 241
Android tasks and the 28-task Apple framework/archive path with the same
sealed 256-entry source inventory. Unsigned phone and Wear SHA-256 values are
`9a4d113fda6601f18cd6614f5b0797a715c9081fd52ecc41f0ec5401cfb2d8f4`
and `2801b13123a4da6f70f448cc7f638a4315a08c4e4ab21c73acfb665c48515b45`;
the unsigned Apple archive-tree SHA-256 is
`8fc6c4693542f15d9518ea2217bf373986e4c10a96ebbb06e39f3dcfef4fe85f`.
All embed the exact authority and pass their identity checks. These outputs are
regression evidence only: no protected workflow run, signed artifact, physical
QA, or store upload is claimed, and the manifest remains `0/3` byte-verified.
Its historical boundary is recorded in the
[source-sync evidence](../growth/quality/release-artifact-source-sync-2026-08-30-65b2eb9.md)
and [schema-v2 upload manifest](../store/upload-manifest-1.1.0.json).

## Historical Nimbo 1.1.0 hosted-CI provenance hardening — 2026-08-30

The product/build-input revision at this predecessor checkpoint was
`5b98f23d0320fba4eef77f2d7c43fcbd0afd0594`. It keeps phone `1.1.0 (8)`,
Wear `1.1.0 (1000008)`, and Apple `1.1.0 (6)` unchanged. Strict dependency
metadata covers 1,714 resolved artifacts across the Android and fresh-cache
`iosArm64` release graphs, including the module descriptor exposed only by an
empty Android cache. The hosted unsigned build uses a standalone clone,
requires both AABs to embed the exact manifest revision, forbids dependency-
verification overrides, and independently verifies the actual release-source
bytes, path set, file modes, symlinks, and Git index flags before and after
compilation. Independent empty-cache runs at this exact revision passed all
241 Android release tasks and the 28-task Apple framework build plus generic
iOS archive; both produced the same sealed 256-entry source inventory. The
protected signing runner verifies the complete canonical
`ExportOptions.plist` with `destination=export` before secrets are decoded, so
the candidate workflow cannot turn export into a store upload. No protected
workflow run, signed artifact, store upload, or physical QA is claimed. The
historical boundary is recorded in the
[source-sync evidence](../growth/quality/release-artifact-source-sync-2026-08-30-5b98f23.md)
and [schema-v2 upload manifest](../store/upload-manifest-1.1.0.json).

## Historical Nimbo 1.1.0 deterministic Apple signing correction — 2026-08-30

The product/build-input revision at this predecessor checkpoint was
`aa6496d0ac9011ff818d2c0dd2ec5c565317400c`. It keeps the coordinated phone,
Wear, and Apple identities and the source-binding setting, while replacing the
obsolete global provisioning-profile override with bundle-specific App Store
profiles for the app, widget, and watch plus a matching manual export map.
Read-only Xcode build settings prove the three mappings. Exact-source unsigned
Android phone/Wear release gates and Apple device build/archive plus matching
dSYMs passed. Real Apple private-key use remained blocked, no signed candidate,
IPA, or physical QA was produced, and 0/3 artifacts were byte-verified. Its
historical decision is recorded in the
[source-sync evidence](../growth/quality/release-artifact-source-sync-2026-08-30-aa6496d.md)
and [schema-v2 upload manifest](../store/upload-manifest-1.1.0.json).

## Protected GitHub-hosted candidate signing

`.github/workflows/signed-candidate.yml` is the only signed-candidate CI entry
point. It is manual-only, restricted to `4810092/Weather` `master`, has
read-only repository permissions, and uses two isolated standard GitHub-hosted
`macos-26` jobs. The first job has no environment or secret access: it creates a
standalone non-local clone at the manifest's exact revision, runs the complete
Android release gate, creates an unsigned Apple archive, verifies embedded AAB
revisions and the sealed release-source tree, and transfers only an inert,
checksummed one-day input package. A fresh second runner uses the protected
`release-signing` environment, validates that input, then decodes signing
material and signs phone, Wear OS, app, widget, and watch products. It validates
the exact non-upload export-options contract before any secret becomes
available.

`scripts/verify_signed_candidate.py` re-opens a single closed six-entry
candidate tree. It binds the two AABs, IPA, Android mapping, ExportOptions, the
complete Apple archive, and all dSYMs; the mapping must equal the copy embedded
in the phone AAB. It also rejects unexpected files, symlinks, special nodes,
source mutation, and mutate-restore attempts. A successful run uploads only a
receipt-bound candidate tarball and its machine-readable receipt for seven
days; decoded keys, profiles, raw staging directories, and unsigned inputs are
not included.

The signing job requires these environment secrets. If any is absent, the
unsigned job may complete, but signing fails before any candidate is produced:

- `NIMBO_ANDROID_UPLOAD_KEYSTORE_B64`;
- `NIMBO_ANDROID_UPLOAD_STORE_PASSWORD`;
- `NIMBO_ANDROID_UPLOAD_KEY_PASSWORD`;
- `NIMBO_APPLE_DISTRIBUTION_P12_B64`;
- `NIMBO_APPLE_DISTRIBUTION_P12_PASSWORD`;
- `NIMBO_APPLE_APP_PROFILE_B64`;
- `NIMBO_APPLE_WIDGET_PROFILE_B64`;
- `NIMBO_APPLE_WATCH_PROFILE_B64`.

Binary signing inputs are base64-encoded only for secret transport and are
decoded under the runner's temporary mode-700 directory. Android passwords go
to `jarsigner` only through its standard-input prompts with xtrace disabled;
they never appear in command arguments. The Apple identity is imported into a
new ephemeral keychain, profiles are checked against their exact bundle IDs,
team, distribution entitlements, and expiry, and all temporary key/profile
material is destroyed in an `always()` cleanup step. Do not place any of these
values in repository variables, workflow inputs, logs, artifacts, or tracked
files.

Every third-party action is pinned to a reviewed full commit SHA. Repository
checks bind the complete workflow bytes, complete action-step blocks (including
artifact paths), run bodies, shells, and exact secret-step environments. This
is intentionally narrow: any workflow mutation requires an explicit policy
update and regression run. The Gradle 9.7.0 wrapper ZIP is pinned to its
official SHA-256, and every resolved Gradle dependency artifact is covered by
`gradle/verification-metadata.xml`.

The protected runner does not execute mutable repository Python while signing
material is available. Reviewed hashes of the two verifier scripts are checked
and copied before secret decoding. After export, the Keychain, P12, keystore,
profiles, and decoded profile plists are destroyed; only then does an isolated
Python process execute those rehashed copies. Candidate verification also
checks both the standalone build clone and the current checkout against the
manifest source revision, preventing an old manifest from signing stale product
bytes after `master` advances.

This workflow does not write to Git, upload to either store, submit for review,
publish metadata, or promote `store/upload-manifest-1.1.0.json`. Its receipt is
pre-manifest byte evidence only. The resulting hashes and a separate committed
signing record must promote the manifest before the ordinary artifact verifier
can return `verified-current`; exact-byte physical QA remains a separate gate.
The historical readiness/provisioning boundary is recorded in
[the hosted signing readiness evidence](../growth/quality/github-hosted-signed-candidate-readiness-2026-08-30.md);
the successful execution and retained-byte boundary are in the
[run evidence](../growth/quality/signed-candidate-run-33381050098.md).

## Nimbo 1.1.0 Apple source-binding checkpoint — 2026-08-30

The authoritative product/build-input revision is
`44c189209c793cf097fcc293faf8db88033e6902`. It keeps phone `1.1.0 (8)`, Wear
OS `1.1.0 (1000008)`, and Apple `1.1.0 (6)`, while adding a fail-closed
`NimboSourceRevision` build setting to the iOS app, WidgetKit extension,
simulator app, and watch app. A one-time unsigned Release simulator smoke
confirmed that an explicitly supplied full revision reaches all produced
Info.plists. No retained upload artifact was built or signed from this revision,
so all earlier Android, Apple, screenshot, and device evidence is historical
and non-transferable. This predecessor checkpoint is recorded in the
[source-sync evidence](../growth/quality/release-artifact-source-sync-2026-08-30.md)
and [schema-v2 upload manifest](../store/upload-manifest-1.1.0.json).

## Nimbo 1.1.0 historical source-sync checkpoint — 2026-08-29

Review-prompt, background-refresh, and forecast-storage failure hardening landed
after the retained phone vc7 and Apple build-5 artifacts were produced. At this
checkpoint the authoritative product source was
`9c2dce4200dbba5487c8c458ade4616005fde6e6`; its identities are phone
`1.1.0 (8)`, Wear OS `1.1.0 (1000008)`, and Apple `1.1.0 (6)`.
Exact-current unsigned Android bundles and ad-hoc Apple simulator products have
recorded hashes, but all remain blocked without source-current distribution
signing and matching physical-QA evidence. That predecessor phone debug APK
passed bounded physical API 25 onboarding/live/late-day Best Time/tip/offline/
recovery/process-health QA, but its debug certificate does not satisfy the
upload-signed physical matrix. Byte-identical debug bytes also passed the
bounded API 36 tablet/widget emulator scope in Uzbek, including widget
render/tap, large text, and rotation; that is not physical-tablet or signed-
candidate QA. The Wear application payload is unchanged, but
its retained signed AAB embeds historical revision `4d9492a`, not the current
product source `9c2dce4`; payload parity does not satisfy exact-source
provenance.
The exact boundary and preserved historical hashes are recorded in the
[source-sync evidence](../growth/quality/release-artifact-source-sync-2026-08-29.md)
and [upload manifest](../store/upload-manifest-1.1.0.json); the bounded debug
phone run is recorded in the
[current-product physical smoke](../growth/quality/android-current-product-physical-smoke-2026-08-29.md).
The tablet/widget emulator boundary is recorded separately in the
[current-product tablet/widget smoke](../growth/quality/android-current-product-tablet-widget-smoke-2026-08-29.md).

## Nimbo 1.1.0 historical internal checkpoint — 2026-08-28

At this historical checkpoint the coordinated candidate used Android phone `1.1.0 (7)`, Wear OS `1.1.0
(1000008)`, and Apple `1.1.0 (5)`. The phone and Wear AABs are upload-signed,
Bundletool-validated, and retained outside the repository; a universal phone APK
passed physical API 25 clean/live/cold-start, denied-location/manual-search,
share, 150% text, TalkBack, cached-network recovery, and contextual
review-prompt smoke. The Apple archive and distribution-signed IPA have exact
app/widget/watch dSYM coverage. See the
[growth checkpoint](GROWTH_RELEASE.md), [signed Android artifact evidence](../growth/quality/android-release-artifacts-2026-08-28.md),
and [Apple artifact evidence](../growth/quality/apple-release-artifacts-2026-08-28.md).
This section records local readiness only: no 1.1.0 store upload, review,
approval, rollout, or public availability is claimed.

## App Store 1.0.1 submission — 2026-08-23

App Store Connect accepted Nimbo 1.0.1 build 4 and reports submission
`2655e3c2-03eb-4ca4-be40-e8f74e87a12b` as `Waiting for Review`. The submitted
binary contains the iOS/iPadOS app, WidgetKit extension, and Apple Watch
companion. The product page includes iPhone, iPad, and Apple Watch screenshots;
release notes are populated for all 12 App Store localizations used by Nimbo.
Automatic release is enabled, with an immediate full rollout after Apple
approval and no phased release. This is not yet a live App Store release; App
Store Connect remains authoritative until review and storefront propagation
complete.

The exported IPA is retained at
`/Users/khasan/work/ganikhodjaev/.nimbo-release/ios/1.0.1-4/export/Nimbo.ipa`
with SHA-256
`5f2b260023bedf2450174de2be4f299a2a2c7adbf4cfcec45ff34f13614425c4`.
Release simulator build, shared tests, repository/localization/store checks,
archive/export, distribution signing, and deep code-sign verification passed
before upload.

## Wear OS policy rejection and hotfix — 2026-08-20

Google rejected Wear OS version code 1000006 because the in-app background was
not pure black and startup did not show the launcher icon at 48 dp on black. The
1000007 source hotfix makes the default and night app/window backgrounds
`#000000`, adds AndroidX Core SplashScreen 1.2.0, and uses the existing launcher
glyph through a centered 48 dp splash drawable. Repository checks guard the
policy resources, starting theme, launcher-theme assignment, call ordering, and
version-code floor.

The hotfix passes `assembleDebug`, `lintDebug`, and `bundleRelease`. Its
upload-signed AAB has SHA-256
`aeecf509e977036f9af3f0d48c55e80413619a3fa5ea6061fa9f070f73ba2b91`,
matches the accepted upload certificate, and passes Bundletool 1.18.3
validation. A Bundletool-generated universal APK is v3-signed with the same
certificate and reports package `uz.ganikhodjaev.weather`, version 1.0.2
(1000007), min SDK 30, and target SDK 36. Rapid
cold-start captures on the 480 x 480 / 320 dpi Wear OS XL Round emulator show
the centered branded glyph on black followed by a readable black app surface in
both UI modes. The unchanged NimboWatch target also builds successfully with
Xcode 26.6/watchOS 26.5 SDK; no Apple launch-screen change is required.
Play Console accepted build 1000007 into Production release
`Nimbo Wear 1.0.2 (1000007) — Policy fix`; build 1000006 appears under `Not
Included` and rollout is 100%. At 17:50 Asia/Tashkent on August 20, the same
replacement became the latest internal Wear release, with 1000006 excluded. At
17:51, Play Console accepted the Production change for review and now lists it
under `Changes under review`. The internal track has no selected testers, and
managed publishing remains off, so an approved Production release will publish
automatically.

## Android prerequisites

Verify Play App Signing and the upload certificate in Play Console. A local or CI release build must use protected credentials and must match the accepted upload identity. Build an AAB with R8, validate package/version/permissions, install a Play-derived production APK, then install the Nimbo update before any rollout.

Play Console inspection on August 10, 2026 confirmed the existing production
listing at version code 2 / version name 1.0.1 and confirmed Play App Signing is
enabled. The Nimbo candidate at that checkpoint was version code 4 / version name 1.0.0.
The original extensionless upload keystore was recovered outside the repository
with alias `weather`; the
matching store/key passwords remain in macOS Keychain. Its file and Keychain
dates align with the March 2024 legacy release. Keychain access and certificate
verification completed on August 10: the certificate exactly matches the
accepted upload SHA-256 below. Keep all private material outside Git. The current
Play role cannot request an upload-key reset (`Permission required`), but no
reset is needed.

The accepted upload certificate SHA-256 reported by Play is
`43:15:48:A4:87:1C:9C:09:0E:EE:80:8A:C3:A3:48:98:F5:D7:86:02:D9:E7:47:DF:E8:1E:22:84:15:AA:C2:52`.

The production legacy input is no longer inferred from package metadata. App
Bundle Explorer artifact `4859919545693253619` was downloaded as Google's signed
universal APK and verified as version code 2 / version name 1.0.1. On the API 36
emulator it passed clean install, real network rendering, background/foreground,
repeat launch, and offline cold launch. Its Play signing certificate SHA-256 is
`99:B8:76:1F:7E:FB:2F:02:90:E4:A1:98:E9:46:54:36:C7:3B:CA:D0:DD:61:91:14:12:6F:F5:67:FF:80:BF:63`.
Installing a locally QA-signed Nimbo APK over it fails with
`INSTALL_FAILED_UPDATE_INCOMPATIBLE`, as it must. The remaining upgrade gate is
therefore specifically a Play-signed version code 3 internal-track build, not
legacy artifact availability.

Play accepted the unchanged signed AAB as version code 3 / version name 1.0.0,
target API 36. Internal release `Nimbo 1.0.0 (3) — Internal` became active for
the existing three-account license-testers list at 10:42 Asia/Tashkent on August
10. Its signed file SHA-256 is
`90f4b3c0a002341855701fbf2c8714f48dcff0ba5c820acd89edd0123a0674c6`.
The real upgrade gate passed on August 10 on the Android 16 / API 36
`Small_Phone` Play Store emulator (720 x 1280). Production 1.0.1 (2) was
installed from Google Play and launched at 11:08 Asia/Tashkent. The same
installation opted into Internal Testing and accepted the Play-delivered Nimbo
1.0.0 (3) update at 11:12 without uninstalling. Package-manager evidence shows
the original `firstInstallTime`, a later `lastUpdateTime`, installer and
initiating package `com.android.vending`, and the unchanged expected Play
app-signing certificate.

The preserved post-update installation passed background/foreground,
force-stop and online cold launch, offline cold launch with database-backed
saved weather, manual city change and persistence, metric unit persistence,
light/dark appearance, English, Russian, Arabic RTL, timeline selection and
hour semantics, yesterday comparison, recent-day history, and Best Time
Outside. Logcat and process exit history showed no crash or ANR. This closes the
legacy Play 1.0.1 (2) -> Nimbo 1.0.0 (3) release gate; listing/policy completion
and production promotion remain.

The production listing draft was completed on August 10. The legacy icon,
feature graphic, and two legacy phone screenshots were detached, while the
version-controlled Nimbo icon, feature graphic, five phone screenshots, four
7-inch tablet screenshots, and four 10-inch tablet screenshots were assigned.
The final asset counts are 1/1 icon, 1/1 feature graphic, 5/8 phone, 4/8
7-inch, and 4/8 10-inch. The saved draft uses the Nimbo name and source-backed
copy.

The Play app-content overview reports every declaration complete. Health is
declared as having no health functions or regional health requirements. Data
Safety records encrypted transport, no account, no third-party sharing,
optional approximate location and in-app search history collected for app
functionality, and automatic deletion within 90 days. The privacy-policy URL
was corrected to the current repository `docs/PRIVACY.md`.

The first Production review draft used the Play-tested version code 3 binary.
Play correctly warned that the coarse-location permission implicitly made
`android.hardware.location` required, excluding one phone and five tablets.
That contradicted the product contract because manual city search works without
location permission or hardware. RC2 therefore adds only an explicit
`android:required="false"` location-hardware declaration and increments Android
version code to 4 while retaining version name 1.0.0. A repository check now
guards the optional-hardware declaration.

The upload-signed RC2 AAB was accepted by Play with SHA-256
`919fa79df1f52cc7ed4750f3f979f812c84e796741aa7ec5adf0251e42b05dd3`.
Internal review reports all six devices restored, totals of 11,361 phones and
6,279 tablets, and no device-loss warning. The only remaining warning is the
non-blocking recommendation to upload native debug symbols. Internal release
`Nimbo 1.0.0 (4) — Internal RC2` became active for the existing three testers at
12:35 Asia/Tashkent on August 10, 2026. The preserved version code 3 install then
updated through Google Play to version code 4 at 13:20 without uninstall;
`firstInstallTime` and the Play installer were preserved. Online and
airplane-mode cached cold launches passed with the expected saved-weather state
and no crash. Version code 3 must not be promoted to Production.

RC2 is tagged `v1.0.0-rc.2` at master commit
`692c0acbb1a807ae1b9024f104f0dbf657cad4f7`. Pull request 5 passed both
Android/shared and unsigned iOS CI before merge.

The obsolete Production draft containing version code 3 was replaced with the
already validated version code 4 artifact. Google Play accepted Production
release `Nimbo 1.0.0 (4)` for review at 14:21 Asia/Tashkent on August 10, 2026.
The common-issues pre-submit check completed without another issue. The
Publishing overview reports `Изменения на проверке` and
`Изменения находятся на рассмотрении`. The release requests a 100% rollout
across all target countries because Production reports zero active installs; a
staged percentage cannot produce a meaningful risk sample. Managed publishing
is off, so an approved change will roll out automatically. The only validation
warning is the non-blocking native-debug-symbol recommendation.

Google Play made `Nimbo 1.0.0 (4)` available in Production at 14:32
Asia/Tashkent on August 10, 2026, across 177 countries. The localized city
search, resolved current-location city name, and rounded timeline interaction
update was then built as `Nimbo 1.0.1 (5)`. Its upload-signed AAB has SHA-256
`42f3d107c6a7e71c6895f13e34822604ac35632f774a86d9a75196769ac1f581`
and the accepted upload certificate documented above. Play accepted the new
Production release with English and Russian release notes and a requested 100%
rollout across all target countries. At 23:14 Asia/Tashkent, the Publishing
overview reported the change under review; the automated common-issues check
will pass it to Google review when complete. Managed publishing remains off,
and the only validation warning remains the non-blocking native-debug-symbol
recommendation.

As of 2026-08-31, Google Play updates must target Android 16 / API 36. Nimbo targets API 36 from its first release candidate.

## iOS prerequisites

Verify or create App ID `uz.ganikhodjaev.weather` in the named Apple Developer team, then configure distribution signing and App Store Connect. Since 2026-04-28, uploads must be built with Xcode 26 or later and an iOS 26 SDK. Archive, validate, upload, complete privacy/age-rating metadata, smoke-test through TestFlight, then submit.

The device archive command is:

```sh
nimbo_source_revision="$(python3 scripts/verify_release_artifacts.py --print-source-revision)"
xcodebuild -project iosApp/Nimbo.xcodeproj -scheme Nimbo \
  -configuration Release -destination 'generic/platform=iOS' \
  -archivePath build/Nimbo.xcarchive \
  DEVELOPMENT_TEAM=5SWEZ7HTYP \
  NIMBO_SOURCE_REVISION="$nimbo_source_revision" \
  archive
xcodebuild -exportArchive -archivePath build/Nimbo.xcarchive \
  -exportPath build/app-store-export \
  -exportOptionsPlist iosApp/ExportOptions.plist
```

The first command fails unless the manifest revision is a real commit and the
actual tracked/untracked product bytes match it. Never replace it with an
unvalidated `git rev-parse` value: the same validated full revision must be
expanded into the signed app, widget, and watch Info.plists.

Release signing is target-specific in `iosApp/project.yml` and the generated
Xcode project. The app, WidgetKit extension, and watch app each select their own
App Store provisioning profile; `iosApp/ExportOptions.plist` repeats that exact
bundle-to-profile map and uses the Apple Distribution identity. Do not pass one
global `PROVISIONING_PROFILE_SPECIFIER` on the command line: Xcode applies it to
all embedded targets, where the main-app profile is invalid for the widget and
watch bundle identifiers.

On August 10, 2026 these commands produced and exported a valid arm64 App Store
archive without requiring an Xcode account login. The archive and exported IPA
use the explicit Nimbo profile and the existing Apple Distribution private key;
the post-export verification below is mandatory before upload.

The current Admin has Certificates, Identifiers & Profiles access, and explicit App ID
`uz.ganikhodjaev.weather` was registered as `Nimbo` in team `5SWEZ7HTYP` on
August 10, 2026 without optional capabilities. Xcode 26.6 is authenticated for
the same team, and the valid Apple Distribution private key is present locally. App Store profile
`Nimbo App Store 1.0` was generated and installed, and Xcode 26.6 exported a
distribution-signed iOS 1.0 (1) IPA with SHA-256
`cb5c75bdcb574770e887aede7b05a36f33b2d4c4eb944f2dcf42032e23a46335`.
Deep codesign validation passed; the embedded profile has
`beta-reports-active=true` and `get-task-allow=false`. Apple rejected `Nimbo` as
a globally occupied App Store name, so the minimal store-only fallback
`Nimbo Weather` is used for App Store Connect record `6799886897`; the binary
display name remains `Nimbo`. Xcode uploaded the verified IPA at 13:29
Asia/Tashkent, Apple processed build 1, and the build is attached to version
1.0 with export compliance recorded as no custom encryption. English metadata,
review notes/contact, manual release, and real production-UI iPhone/iPad
screenshots are saved. App Information is saved with Weather category, subtitle,
and a 4+ rating. App Privacy is published with only Coarse Location and Search
History disclosed for App Functionality, not linked to identity and not used for
tracking; the public privacy-policy URL targets `docs/PRIVACY.md` on `master`.
Build 1 reports `Ready to Submit`. At the owner's explicit direction to proceed
directly to release, no internal TestFlight tester was assigned and no physical
TestFlight smoke is claimed. Pricing is free with United States as the base
storefront, all 175 countries or regions are selected, and untested Apple
Silicon Mac and Apple Vision Pro distribution are disabled. Content-rights
information records the necessary rights for the third-party weather and place
data. App Store version 1.0 build 1 was submitted at 14:18 Asia/Tashkent on
August 10, 2026. Submission
`1e305187-129c-466b-bc74-3347254eaea1` is `Waiting for Review`; manual release is
selected for the first version.

The same localized-location and timeline update was archived as iOS 1.0 build
2. During verification, the hard-coded bundle version values in `Info.plist`
were replaced with `MARKETING_VERSION` and `CURRENT_PROJECT_VERSION`, making
the Xcode project settings the source of truth. The final distribution-signed
IPA has SHA-256
`3988430bd6fd85e84f830dbd24ff020059e5ebcb4de6fc160a0042fed58eaf2d`;
deep codesign validation passed, and the embedded profile again has
`beta-reports-active=true` and `get-task-allow=false`. Xcode uploaded build 2 at
23:01 Asia/Tashkent. The obsolete build 1 review submission was canceled,
build 1 was removed from version 1.0, and build 2 was attached with export
compliance recorded as no encryption. Submission
`d44f3a55-ae31-4a17-9195-371ba9efa478` was sent at 23:14 Asia/Tashkent and is
`Waiting for Review`. Manual release remains selected.

## Credentials

No signing key, certificate, provisioning profile, API key, Play service account, App Store Connect key, or password belongs in Git. CI receives short-lived or encrypted secrets. Release artifacts are attached to releases or uploaded to stores, not committed.
