# Current-source crash hardening — 2026-08-29

## Verdict

**PASS within the bounded source, simulator, and debug-device scope** for exact
product commit `97c26cbec570468b4971daa7779e3839aa4c48ce`.

This result does **not** close `ios_crash_gate`. The production `1.0.1 (4)`
crash on 2026-08-25 still has no downloadable `.ips`, stack, incident ID, or
binary UUID, so none of the fixes below is attributed to that historical event.
It also does not produce an upload-signed Android bundle, Apple archive, or
physical Apple result.

## Hardened boundaries

- UIKit now uses a single `UISceneDelegate` lifecycle. Scene-aware key-window
  lookup replaced the legacy application window for sharing, theme updates, and
  StoreKit review presentation.
- `BGTaskScheduler` registers the `@MainActor` handler on the main queue, and
  the Kotlin completion returns to `MainActor` before completing the task.
- App and background startup catch storage-driver initialization failure.
  The first `unitPreference` and active-location SQL reads also fail closed to a
  retryable UI instead of escaping the Compose coroutine.
- The 11th saved location raises a typed limit result. SQLDelight rolls the
  transaction back, the location picker stays usable, and Cancel restores the
  previous forecast until persistence succeeds.
- A long-lived SQL observation failure preserves cached content, clears review
  eligibility, and reattaches with exponential backoff from 2 to 60 seconds.
- The released database fixture now migrates from schema 1 to the current
  schema 3 and verifies settings, daily forecast, and air-quality queries.
- Repository checks guard the scene manifest, removal of the legacy window,
  BGTask main-queue registration, and the completion actor hop.

## Automated and build evidence

- Focused Android-host startup, saved-limit, rollback, observation-reattach,
  and released-migration tests passed.
- A clean full Gradle gate passed: 214 actionable tasks, including ktlint,
  Android-host and iOS Simulator tests, app JVM tests, SQLDelight migration
  verification, lint-vital/R8, phone bundle, and Wear bundle. A preceding
  non-clean aggregate attempt exposed a missing Gradle in-progress result file;
  the standalone iOS test and the documented clean gate both passed, so that
  derived-output failure is not recorded as a product pass.
- Repository, localization, store metadata/assets/previews, dashboard, and two
  site builds passed. Python growth tooling passed 107 tests.
- Exact-commit Android phone `1.1.0 (8)` AAB SHA-256 is
  `c89b311f2227ecad6ff0f80d8f18529348f52118655b8c70112c2aef48d1c23c`;
  mapping SHA-256 is
  `0e1624387e2829c90b690a9c288d4140545df68ecbf523d98e36d704b8150988`.
  Bundletool 1.18.3 validation passed and the embedded VCS metadata names the
  full commit above. The AAB has zero signature entries and is not uploadable.
- Exact-commit arm64 simulator executables built with
  `CODE_SIGNING_ALLOWED=NO`:

  | Product | Version | Minimum OS | SHA-256 |
  | --- | --- | --- | --- |
  | iOS app | `1.1.0 (6)` | iOS 15.0 | `e6a43119ff23a1ffd3fb0da600bfad9334b94f3ce7a15d244afa9744d853c539` |
  | Widget | `1.1.0 (6)` | iOS 17.0 | `0df017e7e3f01e04acdba3b7cbb304e442318b2fad4e2ca68b1fba0a391afa94` |
  | Watch app | `1.1.0 (6)` | watchOS 10.0 | `71452e1d08c9293aaf0c3b851b7335c8053b3568f06231cba0633c4758b6b462` |

  Each has only a linker-generated ad-hoc signature with no Team ID, bound
  Info.plist, or sealed resources. These are simulator products, not archives.

## Runtime evidence

### iOS Simulator

The exact-commit app executable above was installed on simulator
`95DD015B-B4DC-4B20-AECD-1A7FC391E81B` and cold-launched/terminated 40 times:

- launch failures: 0;
- terminate failures: 0;
- new matching diagnostic reports: 0;
- `UIScene lifecycle will soon be required` faults: 0;
- unexpected-executor faults: 0;
- matching crash/fatal lines in the bounded process log: 0.

The Skiko `libicu.icudtl_dat.o` simulator object still carries an iOS Simulator
18.5 minimum-version warning while the final app links for iOS 15.0. The device
slice does not carry that mismatch. The warning is non-fatal for the tested
simulator but remains an upstream packaging/runtime-compatibility caveat until
an iOS 15 device or simulator is exercised.

### Android exact debug bytes

Debug APK SHA-256
`5680f2bd8b7f2904cd61831c774614fb1bd147239ae37a78e858209346a180f0`
was installed on the dedicated physical General Mobile Android 7.1.1 / API 25
phone and the isolated Android 16 / API 36 `Nimbo_API_36` emulator. Pulling the
installed base APK from both targets reproduced the same hash.

- Both targets rendered localized onboarding, selected Tashkent, and loaded a
  live forecast.
- Both passed 10 force-stop/cold-start iterations with zero launch failures and
  no captured Nimbo FATAL/ANR line.
- API 25 passed ordinary `Bukhara` search, live selection, IME resize evidence,
  and the localized platform share chooser.
- API 36 passed a true-offline cached cold start, failed-refresh saved-weather
  fallback, and online recovery; airplane mode was restored to `0`.
- On API 36, a schema-3 database with the `app_setting` table deliberately
  removed produced the retryable `Weather is out of reach` / `Try again` UI,
  not a crash. The temporary app data was then cleared and onboarding restored.
- The debug package was uninstalled from both QA targets, the emulator was
  stopped without a snapshot, and the Samsung public `1.0.1 (5)` installation
  remained untouched.

Evidence is under
`growth/quality/evidence/android-crash-hardening-2026-08-29/`.

## Remaining gates

- Obtain and symbolicate the actual production iOS crash report.
- Restore protected private-signing authorization without replacing existing
  identities or exporting secrets.
- Build upload-signed Android phone and Wear OS artifacts plus
  distribution-signed Apple artifacts from the current source, and run the full
  physical phone/tablet/widget/watch matrix.
- Confirm post-rollout production stability before changing the crash gate.
