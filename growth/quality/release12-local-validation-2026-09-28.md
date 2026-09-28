# Build 12 local validation — September 28, 2026

Product source: `0faf1105cc5da072e4e9ee043c46e2e9de4f4ada`.
Release preparation head: `9d96056`.
Candidates: phone `1.1.0 (12)`, Wear `1.1.0 (1000012)`, Apple `1.1.0 (12)`.

All three modes of `scripts/local-ci.sh` completed successfully in the existing
checkout, without cleaning caches or dispatching ordinary hosted CI:

- `core`: 367 Python tests; 258 shared Android/native, 13 phone, and 10 Wear unit
  tests; repository, source contract, localization, store assets/previews,
  dashboard, ktlint, SQLDelight migration, release lint, and both Android AABs.
- `android-ui`: five instrumentation tests each on API 24 phone, API 36 phone,
  and API 36 tablet; each result verifier confirmed five tests and no failures.
  Disposable AVDs and downloaded system images live under the ignored
  `.codex/release12-android` directory. The connected Samsung was untouched.
- `apple`: shared iOS simulator tests, 37 Swift surface/widget tests, and
  unsigned Release builds for NimboSimulator and NimboWatch. Xcode 27.0 was used.

The local build-12 app was exercised in Device Hub on iPhone 18 Pro/iOS 27.0
and iPad Pro 11-inch (M4)/iPadOS 18.5. Both loaded the Tashkent forecast and
opened/dismissed the native Share sheet without terminating the app. English
and Russian layouts were observed respectively. Both produced the versioned
App Group JSON and lock, with configured weather state.

The simulator app and widget received ad-hoc signatures with their checked-in
App Group entitlements for runtime testing. This changed generated build
outputs only, used no login Keychain, and is not distribution-signing evidence.
The unsigned CI output alone lacked runtime App Group access.

Local logs are retained temporarily at `/tmp/nimbo-release12-core.log`,
`/tmp/nimbo-release12-android-ui.log`, and `/tmp/nimbo-release12-apple.log`.

These results prove local validation only. Protected signing run
`36361077488`, independent verification of its exact bytes, store delivery,
signed-candidate runtime coverage, natural widget/background completion,
fresh crash inspection, review, rollout, and public availability remain
separate. No release-quality gate is promoted by this note.
