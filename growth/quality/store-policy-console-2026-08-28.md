# Store policy console check — 2026-08-28, Google refreshed 2026-08-29

Status: **PASS for the current point-in-time policy gate**. This is a mutable
console observation, not a substitute for the next complete weekly export.

## App Store Connect

- Public iOS version `1.0.1` is `Ready for Distribution`.
- The two latest submitted versions, iOS `1.0.1` and iOS `1.0`, show
  `Review Complete`.
- No pending submission, rejection, unresolved App Review conversation, or
  compliance action is shown in the current review-submissions view.

## Google Play Console

- `Policy status` explicitly reports `No issues found` for Nimbo.
- The publishing overview shows no pending unpublished change and records the
  latest publication on 2026-08-27.
- Phone `1.0.2 (6)` and Wear OS `1.0.2 (1000007)` remain published.

The authenticated read-only recheck at `2026-08-29 06:24 +05:00` again showed
`No issues found`, no pending publishing change, and production phone
`Nimbo 1.0.2 (6)` active across 177 countries and regions. The source-current
phone `1.1.0 (8)` is not published. App Store Connect could not be refreshed in
the same window because the browser session was logged out, so the Apple
observation above remains dated 2026-08-28 rather than being silently promoted
to current evidence.

## Non-policy quality warning

Play Console separately warns that production phone bundle `1.0.2 (6)`
contains deprecated `androidx.fragment:fragment:1.1.0`. This is tracked as a
release-quality dependency issue and does not contradict the explicit
`No issues found` policy status.

The refreshed console also showed two edge-to-edge compatibility
recommendations. Recommendations are tracked as release-quality input; they
are not open policy issues and do not change the explicit policy result.

The current unreleased candidate now pins `androidx.fragment:fragment:1.9.0`
in the phone, shared Android, and Wear OS graphs. Dependency reports resolve
the transitive `1.0.0`/`1.1.0` requests to `1.9.0`, and both generated AAB
`dependencies.pb` manifests contain `fragment 1.9.0`:

- phone AAB SHA-256:
  `12da2a0d69d6ff5b5925a03cec419d7ae988e1092b5748f0662c795ea31771cc`
- Wear OS AAB SHA-256:
  `ac19a0eab1a60554db309166f135e754c97205b79c4f5182164a8b21594e7dc6`

This closes the candidate dependency defect. The production-console warning
will remain visible until a newer accepted bundle replaces phone `1.0.2 (6)`.

## Edge-to-edge recommendations

Current commit `80cdd608b93056edd05e29873da43834a916cd3a` closes the
app-owned findings behind the two Play recommendations:

- the phone themes no longer configure deprecated `statusBarColor`,
  `navigationBarColor`, or redundant `windowLightStatusBar` attributes;
- `enableEdgeToEdge()` remains the backwards-compatible system-bar owner;
- weather content applies `WindowInsets.safeDrawing` on all four sides instead
  of discarding side cutout and waterfall insets;
- light mode supplies a dark navigation fallback for API 24–25, where dark
  navigation icons are unavailable.

Repository checks pass across 620 source paths, the current unsigned AAB above
passes Bundletool validation, and the exact debug bytes passed physical API 25
three-button contrast plus API 36 portrait, IME, dark/light, true-offline, and
landscape side-cutout/three-button runtime paths. See
`android-current-head-device-smoke-2026-08-29.md`.

This is source and bounded-runtime closure, not Play Console closure. The cards
remain recommendations on the currently published vc6 until a new bundle is
processed. Their expanded origins must then be rechecked because compatibility
calls inside the current AndroidX Activity library can still be attributed to
the application by static Play analysis.

## Boundary

The console state can change after this observation. The weekly KPI importer
must still receive explicit `apple_policy_issues=0` and
`google_policy_issues=0` rows from a complete seven-day console evidence
period before the evaluator's metric guardrail can become `pass`.
