# City picker candidate 13 — local source boundary

Source: `b8270b7ce31061c285d8d9af495986cb152a72bc`. Prepared October 4, 2026.

The shared Android/iOS city picker now has a compact fixed heading and close action, a prominent search field, grouped saved/search rows, explicit selected-city treatment, wrapping quick-city chips, and a single quiet geolocation panel. The content width is constrained on tablets. Discovery sections give way to results during a query; a one-character query explains the search minimum. All13 existing locales include the new strings. Search cancellation, stored cities, permission consent, deletion confirmation, keyboard Search and system-back handlers are retained.

Two new instrumented regressions cover constrained search width, search before saved cities, vertical access to the last quick city, selected/deletion semantics, compact-height query/results/clear/close behavior and the IME Search action retaining its query. Existing search race, deletion, geolocation, Russian200%, Uzbek/Arabic ordering and navigation checks remain intact. The result gate now requires17 tests per device. These automated tests do not claim real IME dismissal or screen-reader speech. The compact viewport represents space remaining above the keyboard, and consumes the host keyboard inset to avoid subtracting it twice.

Targeted API24 UI tests and localization completeness passed. API36 phone/tablet verification, fresh full local CI and native simulator review are in progress; earlier source3155d62 test/signing results do not validate this changed UI. New screenshots are collected per device in `build/android-ui-diagnostics/*-glass/city-picker-{light,dark,ru-font-200}.png`.

Current candidates remain phone1.1.0(13), Wear1.1.0(1000013), Apple1.1.0(13). The canonical registry atomically marks Apple, phone, and Wear artifacts blocked until new signing and independent byte/runtime verification. Distribution hashes and evidence remain null; build12 records are historical. The request authorizes local changes and checks only. No physical-iPhone settings, Mac network configuration, push, hosted CI, store upload or publication are part of this change.
