# Current-source crash hardening — 2026-08-29

## Verdict

**PASS within the bounded source, simulator, and debug-device scope** for exact
product commit `df5f82401348a2cca7405feec36c03621af43ea7`.

The current product descends directly from crash-hardening commit `97c26cb` and
adds only the localized, user-initiated support and store-rating paths plus
their tests. No automatic review-policy or crash-hardening implementation was
removed.

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
  verification, lint-vital/R8, phone bundle, and Wear bundle. Parsed reports
  contain 212 tests with zero failures.
- Repository, localization, store metadata/assets/previews, dashboard, and two
  site builds passed. Python growth tooling passed 114 tests.
- Exact-commit Android phone `1.1.0 (8)` AAB SHA-256 is
  `8e590cca0d7e9945874c58a412520142e9d965584236f73cb2836f98a9b9bb19`;
  mapping SHA-256 is
  `1e87fc59cbfae641bd70e980d33d9696284494f08aff0240d35995d912dc7846`.
  Bundletool 1.18.3 validation passed and the embedded VCS metadata names the
  full commit above. The AAB has zero signature entries and is not uploadable.
- Exact-commit arm64 simulator executables built with
  `CODE_SIGNING_ALLOWED=NO`:

  | Product | Version | Minimum OS | SHA-256 |
  | --- | --- | --- | --- |
  | iOS app | `1.1.0 (6)` | iOS 15.0 | `d293763bc3dcf0eee73ebac9db1d5f0e4eda7aca7849c6000e3caf714041f5d9` |
  | Widget | `1.1.0 (6)` | iOS 17.0 | `74b6c6af76d5dc01efb61c2cd66c4fa4b28975704b690bc1371ea21579fd533b` |
  | Watch app | `1.1.0 (6)` | watchOS 10.0 | `0ebc1c8f49f390e57bee86420b5be977ead8f086cb4b9a7ed0ab6849c26068c7` |

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

The installed executable hash matched
`d293763bc3dcf0eee73ebac9db1d5f0e4eda7aca7849c6000e3caf714041f5d9`;
10,252 bounded process-log entries were scanned. App, widget, and watch dSYM
UUIDs match their executables and verify, but all remain simulator products.

The Skiko `libicu.icudtl_dat.o` simulator object still carries an iOS Simulator
18.5 minimum-version warning while the final app links for iOS 15.0. The device
slice does not carry that mismatch. The warning is non-fatal for the tested
simulator but remains an upstream packaging/runtime-compatibility caveat until
an iOS 15 device or simulator is exercised.

### Android exact debug bytes

Debug APK SHA-256
`fb039c02964a0cbd49d9702998a2cba967c63bbc9ff368bcda9ea44936f0c753`
was installed fresh on the dedicated physical General Mobile Android 7.1.1 /
API 25 phone. Pulling the installed base APK reproduced the same hash.

- Russian onboarding selected Tashkent without requesting or granting location
  and loaded a live forecast.
- The support and Rate Nimbo footer actions rendered as clickable. Help opened
  exact `https://nimbo.uz/support/`; Rate opened the package's Play details
  surface. No review or data was submitted.
- The bounded log contained no matching Nimbo FATAL/ANR line.
- The debug package and temporary device-side dumps were removed; the Samsung
  public installation remained untouched.

Broader physical API 25 and isolated API 36 crash-path evidence remains scoped
to preceding commit `97c26cb`; the current bounded follow-up is recorded in
`growth/quality/android-trust-feedback-smoke-2026-08-29.md`.

## Remaining gates

- Obtain and symbolicate the actual production iOS crash report.
- Restore protected private-signing authorization without replacing existing
  identities or exporting secrets.
- Build upload-signed Android phone and Wear OS artifacts plus
  distribution-signed Apple artifacts from the current source, and run the full
  physical phone/tablet/widget/watch matrix.
- Confirm post-rollout production stability before changing the crash gate.
