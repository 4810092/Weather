# Release artifact/source sync — 2026-09-01 — ba824be

Status: **BLOCKED, FAIL CLOSED**.

The authoritative product/build-input revision is
`ba824beae5e72653e42af2b8b78286f61415e3ab`. It resolves to Android phone
`1.1.0 (9)`, Wear OS `1.1.0 (1000009)`, and Apple app/widget/watch
`1.1.0 (7)`.

The phone source replaces every pre-Android-8 Android Studio launcher template
with square and round Nimbo resources generated from
`branding/store/nimbo-app-icon-1024.png`. The generator's `--check` mode
compares every committed pixel to the canonical artwork. A debug APK assembled
successfully, declared package `uz.ganikhodjaev.weather`, min SDK 24, target SDK
36, and version `1.1.0 (9)`, and exposed all ten PNG launcher resources plus the
unchanged API-26 adaptive resources. On the API-24 emulator, Launcher3 rendered
the Nimbo mark for the installed app; the aggregate app-drawer screenshot
SHA-256 is
`d65e813b192980e9bccc0d846e1be78d2b2d46b61c05d744af2940d988ca70f3`.
This is debug-certificate implementation evidence, not upload or Play-delivery
evidence.

No signed artifact is bound to this revision. The previously verified phone
vc8, Wear vc1000008, and Apple build 6 bytes remain immutable historical
candidates tied to revision `2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652`.
Their prior Internal-track, Transporter, and physical observations remain true
only for those exact historical bytes. They do not transfer to this replacement
candidate.

Before any production promotion, hosted exact-source CI, a new protected signed
candidate run, independent full-byte verification, Internal/TestFlight
delivery, and the applicable physical matrix must pass for the replacement
identities. In particular, phone vc9 must show the Nimbo launcher icon through
Google Play on API 24 or 25. No production submission, review, rollout, public
availability, or rank effect is claimed.
