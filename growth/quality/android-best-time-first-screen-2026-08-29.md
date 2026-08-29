# Android Best Time first-screen smoke — 2026-08-29

## Verdict

**PASS within the exact-product-source/debug scope** for commit
`24ea3734c105e259374ad3b41a6f7e6476ea70db`. The primary
`Best Time Outside` recommendation now renders immediately after the current
weather summary and before the one-time first-forecast tip and hourly details.

The exact debug APK was installed on a physical General Mobile 4G Dual running
Android 7.1.1 / API 25 in Russian. A clean onboarding flow selected Tashkent
without location permission, loaded live weather, and rendered the complete
`Лучшее время для прогулки` card in the initial 720 x 1280 viewport. At 150%
system text, the card remained readable and scrollable; after one scroll it
preceded the `24 часа назад · сейчас · 24 часа вперёд` timeline. No matching
fatal exception, process death, startup-storage failure, or ANR was captured.

This is not a signed-release or complete physical-matrix pass. It does not
replace source-current upload signing, tablet/widget/Wear OS physical QA, Apple
physical QA, or the iOS crash gate.

## Exact artifact and device

| Field | Value |
| --- | --- |
| Product commit | `24ea3734c105e259374ad3b41a6f7e6476ea70db` |
| APK | `app/build/outputs/apk/debug/app-debug.apk` |
| APK SHA-256 | `968ac46930c6175562855b1e5229a74f9d49c47e3b4da107334d337291530ad4` |
| Installed bytes SHA-256 | `968ac46930c6175562855b1e5229a74f9d49c47e3b4da107334d337291530ad4` |
| Package / version | `uz.ganikhodjaev.weather` / `1.1.0 (8)` |
| Build type | debuggable, Android debug certificate |
| Device | General Mobile 4G Dual (`gm4g_sprout`) |
| OS / display / locale | Android 7.1.1, API 25, 720 x 1280, Russian |

## Scenarios

| Scenario | Result | Exact observation |
| --- | --- | --- |
| Clean onboarding | PASS | Value-led Russian onboarding exposed Uzbekistan quick cities, ordinary city search, and optional approximate location |
| Tashkent without permission | PASS | Selecting the Tashkent quick city loaded live weather without requesting location permission |
| Primary-value order | PASS | Current conditions were followed by the complete Best Time card; the hourly timeline was below it and absent from the initial visible UI tree |
| 150% text | PASS | The card text wrapped without truncation and remained scrollable; the visible tree placed its heading at y=266–404 and the timeline heading later at y=733–871 |
| Installed-byte identity | PASS | Pulling the installed `base.apk` produced the same SHA-256 as the rebuilt local APK |
| Process stability | PASS within exercised paths | Filtered logcat contained zero matching fatal, ANR, process-death, or startup-storage entries |
| Cleanup | PASS | Temporary package removed; `font_scale=1.0`, airplane mode off, and accessibility services unchanged/disabled |

The repository validator now also fails closed if the source order stops being
current summary → Best Time Outside → first-forecast tip → hourly details.

## Evidence

| Capture | SHA-256 |
| --- | --- |
| `api25-ru-first-screen.png` | `f2fff204fe22d309778dfadc23d32d090660096a312c1f0602cd9567373ca6c9` |
| `api25-ru-first-screen.xml` | `edd0ef4e2cd73f1425afc77e40a984b97b12a722f819d0f3f2be312a7807d7a6` |
| `api25-ru-large-text.png` | `af617c1875db96ded4f58cdda4e2b95542aed45fa7664f991456ca843280cf30` |
| `api25-ru-large-text.xml` | `3836c431d5344a9852319655c18450f761dc9405606a66a5c7e894a47493ed8a` |
| `api25-ru-large-text-scrolled.png` | `21aa964bf75fb7be0437b2f22111593a9f5da088457faad3e14a7183d29b95a5` |
| `api25-ru-large-text-scrolled.xml` | `c842cb979926acc8a4f48c88e0e9e77d46ab2b532d71a541746cfb9f7d5d986e` |

Files are stored under
`growth/quality/evidence/android-best-time-first-screen-2026-08-29/`.

## Boundary

The result proves the bounded activation-path layout on one exact debug APK and
one physical phone. It does not prove upload signing, store processing,
production availability, retention lift, conversion lift, or ranking impact.
