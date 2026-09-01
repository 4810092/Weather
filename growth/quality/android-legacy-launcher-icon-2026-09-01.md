# Android legacy launcher icon — 2026-09-01

Status: **FAIL FOR THE PLAY-DELIVERED API-25 PACKAGE**. This is a production
release blocker for the current phone candidate; it does not invalidate the
separately proven forecast, offline, accessibility, widget, or background
behavior.

At `2026-09-01 06:32` Asia/Tashkent, the dedicated General Mobile Android
7.1.1 / API 25 / xhdpi device displayed the Google-Play-installed Nimbo
`1.1.0 (8)` launcher entry with the green Android Studio template icon rather
than the Nimbo brand mark. The same launcher screen rendered the bound Nimbo
3 x 2 weather widget correctly. Its aggregate screenshot SHA-256 is
`02713f3762360cec4a430897d83bf03a63da22d71d6fd443146a75fa9c857cc1`;
the raw capture remains outside Git under the aggregate-only device-evidence
policy.

The source explains the device result. `AndroidManifest.xml` resolves the
legacy application icon to `@mipmap/ic_launcher`, while
`app/src/main/res/mipmap-xhdpi/ic_launcher.webp` is the 96 x 96 template asset
with SHA-256
`398340dad816fc9a6338cb151a8cf1e45b926f9bfb70628b24c4bd2523cc94d4`.
The mdpi, hdpi, xxhdpi, and xxxhdpi legacy resources are the corresponding
template family. The API-26 adaptive foreground instead resolves to
`@drawable/nimbo_mark`, so this observation is scoped to the physically proven
legacy API-25 path; it is not extrapolated into a newer-device runtime claim.

## Decision

Do not promote phone version code 8 to production. Generate branded legacy
square and round mipmaps from the canonical Nimbo artwork, guard those
resources in repository checks, increment the phone version code, and repeat
the exact signed/internal-delivery plus API-24/25 launcher smoke. Existing
version-code-8 runtime evidence remains truthful historical evidence and must
not be relabeled as evidence for the replacement artifact.
