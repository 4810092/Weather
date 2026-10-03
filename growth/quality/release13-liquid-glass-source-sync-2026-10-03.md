# Liquid Glass test candidate 13

Source: `2ea72821fd16d508b85702b911cb452be2a3b2c3`. Prepared October 3, 2026.

The user requested Liquid Glass for Android/iOS, followed by Google Play Internal and TestFlight testing. Production publication is not authorized by this request.

Current candidates: phone `1.1.0 (13)`, Wear `1.1.0 (1000013)`, Apple `1.1.0 (13)`. Wear has a coordinated build-number/compile-SDK change only; its UI is unchanged.

Local `scripts/local-ci.sh full` passed on October 3 for this source: 367 Python/repository checks, 283 Kotlin tests (136 Android shared, 124 iOS shared, 13 phone, 10 Wear), 24 Android instrumented UI tests across API24 phone/API36 phone/API36 tablet, and 37 Swift surface tests. Android release bundles and unsigned iOS/watchOS simulator Release builds succeeded. Light/dark Android screenshots were inspected; the API24 opaque fallback rendered correctly. Full log: `/tmp/nimbo-glass-full-complete.log`. iOS visual/motion QA remains pending because the Mac is locked. Xcode emitted minimum-simulator-version linker warnings for XCTest/ICU; these successful builds do not establish runtime compatibility on the oldest supported iOS release.

Signing, signed-byte verification, store delivery, and runtime distribution evidence are pending. Current hashes and signing/runtime evidence remain null. Local builds and tests do not establish signed-byte identity.

Build-12 source `0faf1105cc5da072e4e9ee043c46e2e9de4f4ada` and its store submissions remain separate. The following bytes are historical relative to the new source; this transition does not cancel, publish, or replace any existing store submission:

| Artifact | Historical build | SHA-256 |
| --- | --- | --- |
| android_phone | 12 | `5fdc866094226d7cde09696e6fd2de27683af0ee6955674b3a1d29a7c203a2cd` |
| wear_os | 1000012 | `51a1d4f0a8e5b8cfa6cb6d752e1a3aad56de36749eaa6fb551039a1f429b23e4` |
| apple | 12 | `b42d0bf6a218ba1b5ed3d607a18611fbf700fadef856b02861f618411585474d` |
