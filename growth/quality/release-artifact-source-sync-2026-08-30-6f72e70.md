# Release artifact source sync — 2026-08-30 hosted UI gate

Status: **BLOCKED for Android phone, Wear OS, and Apple; ordinary hosted CI
run 33295070238 failed; 0/3 current artifacts byte-verified**.

The authoritative product/build-input commit is
`6f72e70fff6eb7566e06dd862e1fad09055343a4`. It resolves to Android phone
`1.1.0 (8)`, Wear OS `1.1.0 (1000008)`, and Apple app/widget/watch
`1.1.0 (6)`.

## Change boundary

Compared with predecessor `ed1b791b8d1a059e62409713102740e08d014de2`, the
release-source change adds an Android Compose instrumentation harness and its
strictly verified dependencies. Five deterministic tests cover optional-
location onboarding and city search, useful forecast/tip/header semantics,
cached-error retry, Uzbek LTR and Arabic RTL ordering, and Russian UI at 200%
font scale. `NimboApp.kt` exposes the existing locale-direction decision as an
internal helper used by the test; the production LTR/RTL rule is unchanged.
The final authority also enables core-library desugaring for the KMP Android
library, preventing the API 24 test target from relying on unavailable direct
`java.time` classes used by `kotlinx-datetime`.

Per the hosted-only CI decision, the final authority was not assembled or
executed locally. A predecessor test APK compiled before the desugaring change
is not current and is excluded from release and execution evidence.

Strict dependency verification now contains `1,758` artifact entries. The
complete `gradle/verification-metadata.xml` SHA-256 is
`91b016e7fc72ca605d473634135b87e1d5b4e16f04608272a0bd809d263782a4`.
The added test dependencies are version-catalogued and the generated allowlist
remains fail-closed.

## CI placement and current evidence

Ordinary CI remains exclusively on standard GitHub-hosted runners. The
workflow now declares an independent Android UI matrix on `ubuntu-24.04` for:

- API 24 / Pixel 2 phone;
- API 36 / Pixel 7 phone;
- API 36 / Pixel Tablet.

The emulator action is pinned to full commit
`a421e43855164a8197daf9d8d40fe71c6996bb0d` (`v2.38.0`). Each matrix job runs
one tracked Bash entrypoint so the action cannot split stateful diagnostics
across shell invocations, then executes `:shared:connectedAndroidDeviceTest`
inside a 28-minute task budget. It captures a bounded post-run logcat, rejects
missing XML, and requires exactly five tests with zero failures, errors, or
skips before success. Reports are retained for seven days. GitHub Java setup is
pinned to `dd06d9cba3e5552c54d9f8ea23572deb30010f7c` (`v6.0.0`) across ordinary
and protected candidate workflows. The maintainer Mac is not a self-hosted
runner and is reserved for local signing authorization and physical-device QA.

Public GitHub Actions
[run 33295070238](https://github.com/4810092/Weather/actions/runs/33295070238)
executed at evidence commit
`2390a10a676d958b70a478f47932685413d15fbc`. That commit is the direct
evidence-only child of `6f72e70`; its release-source authority remains
`6f72e70fff6eb7566e06dd862e1fad09055343a4`. The run concluded **failure**
after 12m24s, so it does not close the ordinary hosted CI gate.

| Job | Outcome | Bounded evidence |
| --- | --- | --- |
| `android-and-shared` | **PASS**, 6m32s | Repository, growth, store, localization, strict Gradle test/lint/migration, and unsigned phone/Wear release stages completed. |
| `ios` | **PASS**, 12m21s | Shared iOS simulator tests completed in 3m28s, glanceable-surface tests in 2m29s, and unsigned app/watch simulator products in 5m49s. |
| `Android UI (phone-api24)` | **FAIL** | Exactly five tests executed; exactly two visibility assertions failed: the Uzbek onboarding title and the Russian 200% font-scale title. |
| `Android UI (phone-api36)` | **FAIL** | Exactly five tests executed; the same two title-visibility assertions failed. This is execution evidence, not a UI pass. |
| `Android UI (tablet-api36)` | **FAIL before emulator start** | `/dev/kvm` existed, but the runner user lacked read/write access. No tablet emulator test execution is claimed. |

The retained GitHub artifact archive digests exposed by the completed run are:

| Artifact | SHA-256 |
| --- | --- |
| `android-ui-results-phone-api24` | `acdaaedc212791e093d164c149f91d1f8395fd1db8442379bb643b1edf5f5afd` |
| `android-ui-results-phone-api36` | `e9824e6bf22ccada49f9aaa2bb53e46f3e3b53ead48745e18a93ceba4af6083e` |
| `android-release-unsigned` | `96257aa2b9011c35da6a464d80d7b29c2f825c578e5d78f043b82becabc0a2a7` |
| `wear-release-unsigned` | `da82df6006d330ee35719ee55e8a73a4542579f1defc84a09bbdbc3b5514d1d5` |
| `ios-simulator-test-results` | `22b8fdbb7144110febd0b438d9c60452c7a33f4ebfe81a5994b16fda2967634c` |

These are unsigned regression outputs or failed-test reports, not upload
candidates. The reported inner Wear AAB digest was available only in
abbreviated form (`2d73fdf6…d1d5`) and is therefore not promoted as an exact
artifact identity. No run output changes the upload manifest or transfers
predecessor physical-device evidence to this authority.

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

1. Correct the two phone visibility assertions and the standard-runner KVM
   permission setup, then obtain a green ordinary hosted CI rerun for the new
   exact release-source authority, including all three Android UI matrix jobs
   and the existing Android/iOS jobs.
2. Unlock the existing login Keychain locally, then provision the eight
   existing signing inputs into the branch-restricted `release-signing`
   environment without sending credentials through chat.
3. Run the manual hosted workflow and retain its receipt-bound candidate tar
   and schema-v2 receipt.
4. Promote the manifest only from the verified receipt and a separate committed
   signing record.
5. Run the exact signed physical phone/tablet/widget/watch matrix and bind its
   evidence to the retained artifact hashes.

No release artifact was signed, uploaded, submitted, or published by this
source-sync update.
