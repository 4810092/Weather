# Release artifact source sync — 2026-08-30 provider decoding hardening

Status: **BLOCKED for Android phone, Wear OS, and Apple signing; exact-source
hosted CI #117 green; 0/3 current signed artifacts byte-verified**.

The authoritative product/build-input commit is
`2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652`. It resolves to Android phone
`1.1.0 (8)`, Wear OS `1.1.0 (1000008)`, and Apple app/widget/watch
`1.1.0 (6)`.

## Change boundary

Compared with predecessor `704fd893e59d94d8e9a4971313a773b3fa545ab6`,
the current authority changes Open-Meteo response handling and its tests:

- omitted hourly precipitation probability, precipitation, gust, and UV arrays
  decode as empty optional series and retain the existing safe per-row defaults;
- omitted air-quality pollutant arrays decode as empty optional series while
  the provider timeline remains required;
- hourly time, temperature, apparent temperature, weather code, wind speed,
  and humidity remain required at JSON decoding; no empty required-row result
  is persisted;
- MockEngine HTTP fixtures prove that omitted optional forecast and air-quality
  arrays remain usable and that missing required time or temperature fails;
- Android-host repository tests prove a failed missing/empty-time refresh does
  not replace cached weather or the saved location timezone.

No version, provider endpoint, request shape, signing identity, store payload,
or release policy changed.

## Current-source local verification

The following targeted checks passed for the exact committed bytes:

- Android host: 14 tests across `OpenMeteoServiceTest`,
  `ForecastResponseMappingTest`, and
  `WeatherRepositoryCachePreservationTest`; zero failures or errors;
- iOS Simulator: 12 tests across `OpenMeteoServiceTest` and
  `ForecastResponseMappingTest`; zero failures or errors;
- common-main, common-test, and Android-host-test ktlint checks;
- repository validation for 804 source paths and `git diff --check`.

These checks prove the bounded mapping/cache behavior only. The hosted matrix
below supplies broader unsigned regression evidence, but neither result
replaces distribution signing, signed-artifact byte verification,
physical-device QA, or post-rollout crash evidence.

## Current-source hosted verification

Evidence-head commit `fb877d30b2179a489f5ce18dd06d892461436540`
resolved the exact product/build-input authority
`2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652` and passed GitHub-hosted CI
[run `33300967788`](https://github.com/4810092/Weather/actions/runs/33300967788),
workflow run #117, in 24m01s. All five jobs succeeded:

- `android-and-shared`: 5m05s;
- `Android UI (phone-api24)`: 2m36s, all 5/5 tests green;
- `Android UI (phone-api36)`: 3m48s, all 5/5 tests green;
- `Android UI (tablet-api36)`: 4m18s, all 5/5 tests green;
- `ios`: 23m59s, including all 18/18 Apple surface tests green.

The run retained these GitHub artifact archives:

| Archive | Bytes | GitHub archive SHA-256 |
| --- | ---: | --- |
| `android-ui-results-phone-api24` | 52,269 | `0f385db95e55c31fbf1789d9e9e57cbdfc7f02e7b5ab249ab69745a62a9d7517` |
| `android-ui-results-phone-api36` | 302,815 | `f934996c9addce8543df6eecfb5bbd5404c83b8b51182098437d2cf8d27a77f1` |
| `android-ui-results-tablet-api36` | 281,718 | `20d21e0a392b0e03058fe053b08912bdf6f4eb0b9470c5e4b7439f6cb432ee5c` |
| `android-release-unsigned` | 5,345,884 | `e499fce976974fbed15cfb5e525d738990a285215e81271954f86f5605c9cf8f` |
| `wear-release-unsigned` | 2,534,295 | `5a4b372e475c4c63ab58522397e7071e85928c6a1309d3c550c8b6f8cf8f6817` |
| `ios-simulator-test-results` | 80,294 | `c406decbf5eed88c830f4139532d6ebc7a69fa761355e8a07a3fb2555c450ffe` |

These values identify GitHub-created archive bytes. They are unsigned build
and test-result proof only, not inner signed AAB/IPA hashes, a signed-candidate
receipt, physical-device evidence, or crash-gate closure.

## Current-source bounded physical regression

At `2026-08-30 14:07–14:21 +05:00`, a clean isolated checkout of the exact
product authority produced a debug APK whose local and pulled installed bytes
share SHA-256
`d66c8f0f9b05232cf484bd95223328a44f2a0bddf1d2f76817ef9504f87fe047`.
The APK passed a bounded physical General Mobile Android 7.1.1 / API 25 smoke
covering denied approximate location, ordinary Bukhara search, live forecast,
cached cold start and failed-refresh warning, recovery, populated home widget
render/tap, process health, and cleanup. The full evidence and device-state
boundary are in
[`android-current-product-physical-smoke-2026-08-30-2cdd438.md`](android-current-product-physical-smoke-2026-08-30-2cdd438.md).

This physical result uses the debug certificate. It is not a retained
upload-signed AAB, Play-delivered build, physical tablet, or paired Wear OS
result and therefore is not promoted into the upload manifest. The source-sync
gate remains blocked and every current signing/physical path in the manifest
remains null.

## Predecessor hosted evidence

GitHub Actions run
[`33297505825`](https://github.com/4810092/Weather/actions/runs/33297505825)
passed for predecessor authority
`704fd893e59d94d8e9a4971313a773b3fa545ab6`, including ordinary Android/iOS
and all three API 24/API 36 phone/tablet UI profiles. Evidence commit
`ac1a07a14db72739b96c869eeefba79297f07e1d` also passed CI run
[`33299592101`](https://github.com/4810092/Weather/actions/runs/33299592101)
for that same predecessor release-source tree. Both runs predate the provider
decoding change and remain non-transferable predecessor evidence. They are
retained for chronology; current hosted truth is run #117 above.

## Protected signing state

At `2026-08-30 12:29 +05:00`, the branch-restricted `release-signing`
environment contained 4/8 required secrets: the Android keystore payload and
the app, widget, and watch provisioning profiles. The two Android passwords,
Apple distribution P12, and its transport password remain absent behind local
Keychain authorization. The candidate workflow has not run.

## Current artifact authority

| Surface | Exact identity | Current signed bytes | Decision |
| --- | --- | --- | --- |
| Android phone/tablet | `1.1.0 (8)` | none bound to this revision | **BLOCKED** |
| Wear OS | `1.1.0 (1000008)` | none bound to this revision | **BLOCKED** |
| Apple app/widget/watch | `1.1.0 (6)` | no distribution-signed archive or IPA bound to this revision | **BLOCKED** |

The schema-v2 upload manifest keeps every current SHA-256, signing-evidence
path, and physical-QA path null. Historical candidates, unsigned artifacts,
and device results from predecessor revisions remain non-transferable.

## Remaining unblock

1. Unlock the local login Keychain, provision the four remaining protected
   signing inputs, and run the manual candidate workflow.
2. Promote the manifest only from the verified receipt and a separately
   committed signing record.
3. Run the exact signed physical phone/tablet/widget/watch matrix and bind its
   evidence to the retained artifact hashes.
4. Obtain and symbolicate the suppressed iOS crash diagnostic, reproduce or
   disposition it against the current signed build, and close the crash gate.

No release artifact was signed, uploaded, submitted, or published by this
source-sync update.
