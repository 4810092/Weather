# Android current-source physical smoke — 2026-08-29

## Verdict

**PASS within the bounded debug/source scope** on a physical General Mobile
4G Dual running Android 7.1.1 / API 25. The current phone identity `1.1.0 (8)`
completed clean onboarding, quick-city selection, a live Tashkent forecast, a
saved-place cold start without network access, cached-weather fallback, and
process-stability checks.

This is not a release-artifact pass. The APK is debuggable and signed with the
Android debug certificate, the worktree was not yet committed, and the current
upload-signed AAB/APK plus the remaining tablet, widget, and Wear OS physical
matrix are still missing. Therefore `android_physical_smoke` and
`release_artifact_source_sync` remain blocked.

## Artifact and device

| Field | Value |
|---|---|
| Local APK | `app/build/outputs/apk/debug/app-debug.apk` |
| APK SHA-256 | `d9e4107506589be1df2c9bc095d200ede8b80aaf09c542897024a471d3f11291` |
| Package / version | `uz.ganikhodjaev.weather` / `1.1.0 (8)` |
| APK signature | v2, `C=US, O=Android, CN=Android Debug` |
| Debug certificate SHA-256 | `7b112e7dce7a8e61ec85b2187fbc642fa196909a53351d298126ca2e23ffe3f8` |
| Source base | Git `584f47a83637ce3587ce980a69f392b84a57656b` plus the uncommitted growth-update worktree |
| Device | General Mobile 4G Dual (`gm4g_sprout`) |
| OS | Android 7.1.1 / API 25, release-key system build |
| Display | 720 x 1280 |
| Locale exercised | Russian |

## Scenarios

| Scenario | Result | Evidence observed |
|---|---|---|
| Clean install and launch | PASS | `dumpsys package` reported version `1.1.0 (8)`, `minSdk=24`, `targetSdk=36`, `DEBUGGABLE`, v2 signing, and a first-launch state with no runtime location permission |
| Onboarding without location | PASS | Russian onboarding rendered the value proposition, Tashkent/Samarkand/Namangan quick cities, ordinary search, and optional approximate-location action |
| Quick city | PASS | Selecting `Ташкент` loaded `Ташкент, Узбекистан`, current conditions, yesterday comparison, future hint, timeline, and the one-time post-forecast tip |
| API 25 HTTPS/live data | PASS | A live forecast rendered after the quick-city action; filtered logcat contained no TLS, certificate, fatal-process, or app crash entry |
| Offline saved-place cold start | PASS | Wi-Fi was disabled through the device Settings UI, the process was force-stopped, and a cold launch retained Tashkent data while showing `Не удалось обновить. Показана сохранённая погода.` |
| Expected offline error | PASS | Filtered logcat contained `Nimbo weather refresh failed: UnknownHostException`; the process stayed alive and rendered cached data |
| Device restoration | PASS | Wi-Fi was re-enabled and reconnected, airplane-mode setting remained off, the temporary Nimbo installation was uninstalled, and package absence was verified |

After the final review-history and cancellable-background-refresh changes, this
entire bounded sequence was rerun on the APK hash above. The decision-relevant
proof is the exact artifact identity, extracted UI text, filtered process log,
and verified device restoration; the existing store/evidence package already
contains representative UI captures.
