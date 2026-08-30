# Release artifact source sync — 2026-08-30 provider decoding hardening

Status: **BLOCKED for Android phone, Wear OS, and Apple; current hosted
regression pending; 0/3 current artifacts byte-verified**.

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

These checks prove the bounded mapping/cache behavior only. They do not replace
the complete hosted Android/iOS release matrix, distribution signing, artifact
byte verification, physical-device QA, or post-rollout crash evidence.

## Predecessor hosted evidence

GitHub Actions run
[`33297505825`](https://github.com/4810092/Weather/actions/runs/33297505825)
passed for predecessor authority
`704fd893e59d94d8e9a4971313a773b3fa545ab6`, including ordinary Android/iOS
and all three API 24/API 36 phone/tablet UI profiles. Evidence commit
`ac1a07a14db72739b96c869eeefba79297f07e1d` also passed CI run
[`33299592101`](https://github.com/4810092/Weather/actions/runs/33299592101)
for that same predecessor release-source tree. Both runs predate the provider
decoding change and are non-transferable regression evidence for this authority.

The next push must execute the standard hosted matrix against
`2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652`. Until that run succeeds, current
hosted regression evidence is explicitly pending.

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

1. Complete the standard hosted Android/iOS and API 24/API 36 UI matrix for
   the exact current source.
2. Unlock the local login Keychain, provision the four remaining protected
   signing inputs, and run the manual candidate workflow.
3. Promote the manifest only from the verified receipt and a separately
   committed signing record.
4. Run the exact signed physical phone/tablet/widget/watch matrix and bind its
   evidence to the retained artifact hashes.
5. Obtain and symbolicate the suppressed iOS crash diagnostic, reproduce or
   disposition it against the current signed build, and close the crash gate.

No release artifact was signed, uploaded, submitted, or published by this
source-sync update.
