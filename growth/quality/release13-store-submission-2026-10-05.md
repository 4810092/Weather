# Candidate 13 store submission — October 5, 2026

The owner explicitly requested submission to App Store and Google Play. Product source is `44d3f7862b61ef95bf2b686820cfba3fc05a7b25`; exact signed hashes and independent byte checks are recorded in [signing evidence](signed-candidate-run-37322319203.md). No build12 result is transferred to build13.

## Google Play

The authenticated console accepted the verified phone `1.1.0 (13)` and Wear OS `1.1.0 (1000013)` AABs. Production release IDs are phone `7` on track `4697319837646598077` and Wear `4` on track `4699095335750135635`. Both retain all 12 existing release-note translations. No supported devices were lost relative to the preceding candidate: 12,320 phones, 6,749 tablets and 82 watches remain supported.

[Review request 16](https://play.google.com/console/u/0/developers/5513021445726079938/app/4975846491997599461/publishing/submission-activity/16/details) was submitted at **19:47 Asia/Tashkent**. The history shows **На рассмотрении**, covering exactly the phone and Wear production releases. The publishing overview placed 13 and 1000013 under **Изменения на проверке**; automatic preliminary checks completed without blocking the submission. A later observation explicitly said the changes are under review. This proves submission, not approval or publication.

There were no blocking upload/release errors. Google recommends native debug symbols for the phone AAB; its ReTrace mapping is embedded and attached. Wear has the generic missing-deobfuscation-file recommendation; its release build is not minified. No fabricated symbols or mapping were uploaded.

Managed Publishing remains on. The separate older request15, phone12/Wear1000012, was still ReadyToPublish and was not released. No metadata experiment, featuring submission, listing change or public rollout was performed.

## Apple

On **October 6 at 13:31 Asia/Tashkent**, Transporter confirmed **DELIVERED** for Nimbo Weather `1.1.0 (13)`, app ID `6799886897`. The exact `Nimbo.ipa` from `.codex/release13-artifacts/extracted/bytes/` was uploaded. Immediately before delivery, `scripts/verify_release_artifacts.py` rechecked the retained three-artifact set and exited0; all SHA-256 values and signatures/source identities still matched the current manifest. The local record is `/tmp/nimbo-release13-pre-apple-delivery-2026-10-06.json`.

Transporter currently reports **THE APP IS PROCESSING**. Delivery is confirmed; processing completion and App Review submission are not yet established. The browser's App Store Connect session expired and shows the password form. The owner was asked to sign in directly and complete any Apple verification; no password or verification code was requested in chat.

The existing version1.1.0 build12 remains Pending Developer Release according to Transporter; it was neither cancelled nor released. After browser access is restored and build13 finishes processing, replace the old candidate and submit build13 while preserving manual release and seven-day phasing.

Google Play was also reloaded on October6: phone13 and Wear1000013 remain under review, Managed Publishing is on, and the old12/1000012 remain separately ReadyToPublish. No production rollout was performed.

## Verification boundary

The manifest and source gate now identify the atomic 3/3 verified-current signed set. Runtime/crash gates remain blocked, with the [simulator/emulator acceptance limits](release13-runtime-acceptance-2026-10-05.md) unchanged. Fresh `scripts/local-ci.sh full` passed (exit0, `/tmp/nimbo-release13-submission-full-final.log`): 367 Python checks, Kotlin/shared/phone/Wear tests, all 60 Android UI tests on API24/API36 phone and API36 tablet, 37 Swift tests, lint, migrations, metadata/release contracts, Android bundles and iOS/watchOS simulator Release builds. The separate real-byte QA matrix check also passed (`/tmp/nimbo-release13-final-byte-qa.log`). Initial launch issues were diagnosed and corrected by removing private artifact environment variables from negative fixture tests and selecting the existing task AVD directory; no test or assertion was weakened. Store review, exact-distribution execution, production health and public availability are separate states.
