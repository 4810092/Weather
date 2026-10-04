# City search field candidate 13 — local source boundary

Source: `c7f87e4bd9d16860507bf7331c592a3e60d3911c`. Prepared October 4, 2026.

The shared Android/iOS city search field now uses a compact rounded glass surface with an inline placeholder and a subtle focus outline. The floating label and its cut-out border are removed. Search and clear icons have consistent sizing and muted color; typed text retains normal contrast. A persistent localized accessible name remains present for empty and populated input, while the decorative placeholder is excluded from duplicate semantics. Existing query, clear, keyboard Search, navigation and saved-city behavior are retained.

The existing compact-height UI regression now checks the editor's accessible name before typing, after Search, and after clearing. Fresh emulator, full local CI and native simulator checks are pending. The previous city-picker evidence in `growth/quality/release13-city-picker-source-sync-2026-10-04.md` applies to its earlier source only.

Current candidates remain phone1.1.0(13), Wear1.1.0(1000013), Apple1.1.0(13). The canonical registry atomically marks Apple, phone, and Wear artifacts blocked until new signing and independent byte/runtime verification. Distribution hashes and evidence remain null; build12 records are historical. No push, hosted CI, store upload or publication is authorized by this local change. Physical-device settings and Mac network configuration remain untouched.
