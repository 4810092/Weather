# Android emulator smoke — 2026-08-28

## Verdict

- **API 36: PASS** on the final APK for clean install, localized English onboarding, quick-city Tashkent selection, live forecast, first-forecast tip, and persisted-location cold start. The immediately preceding runtime-identical candidate also passed denied approximate location and ordinary Bukhara search.
- **API 24: PASS** on the final APK for clean install, localized English onboarding, quick-city Tashkent selection, live forecast, first-forecast tip, and persisted-location cold start. The immediately preceding candidate also passed location-free Bukhara search, a clean-data offline error, non-cancellable `Change place` recovery, and a successful forecast after connectivity returned.
- The first API 24 pass found that the image's 2017 trust store could not validate the current Open-Meteo chain. The release candidate now adds a domain-scoped Android Network Security Configuration for the three exact Open-Meteo API hosts, using system roots plus checked-in official ISRG Root X1/X2 certificates. Cleartext traffic, user-installed roots, broad subdomains, and a global custom trust manager remain disabled.
- The independent `HttpsURLConnection` probe and system WebView still fail on that old image, as expected: the compatibility trust is intentionally scoped to Nimbo's declared API hosts and does not modify the device trust store.

No physical device result is claimed by this emulator report.

## Artifact under test

| Field | Value |
|---|---|
| APK | `app/build/outputs/apk/debug/app-debug.apk` |
| SHA-256 | `7cb445efd4e7fbc9454a451ea6ad80ad84f4381fcececac0198cf20071ba5e10` |
| Size | `16,502,495` bytes |
| APK timestamp | `2026-08-28T20:44:23+0500` |
| Package | `uz.ganikhodjaev.weather` |
| Version | `1.0.2 (6)` |
| SDK declaration | `minSdk=24`, `targetSdk=36` |
| Git HEAD | `7fd91b8bfef0` plus the current uncommitted growth-release worktree |
| Comprehensive predecessor | `b940a41c566347031cd0a47aca43b2a82d28fee931b16840fae7a00ff17cbcc9`; replaced only by quick-city localization/resource plumbing |

The final APK was installed after the TLS, stale-request, transient-retry, and
quick-city localization fixes. Pulling the API 24 installed `base.apk` and
hashing the API 36 installed `base.apk` on-device produced the same SHA-256 as
the host APK above.

## Environments

| AVD | API / Android | ABI | Build fingerprint | Security patch | Device time during TLS diagnosis |
|---|---:|---|---|---|---|
| `Steppe_API24` | 24 / 7.0 | arm64-v8a | `google/sdk_google_phone_arm64/generic_arm64:7.0/NYC/8695085:userdebug/dev-keys` | `2017-10-05` | `Fri Aug 28 19:21:01 UZT 2026` |
| `Nimbo_API_36` | 36 / 16 | arm64-v8a | `google/sdk_gphone64_arm64/emu64a:16/BE2A.250530.026.F3/13894323:userdebug/dev-keys` | `2025-07-05` | `Fri Aug 28 19:21:02 +05 2026` |

Both AVDs were started without loading or saving snapshots. The AVDs were not wiped; only Nimbo app data was cleared to exercise first launch.

## Observed scenarios

### API 24 (`Steppe_API24`)

| Scenario | Result | Direct evidence |
|---|---|---|
| Install final APK | PASS | `adb install -r` returned `Success`; installed APK hash matched the host APK |
| Clean first launch | PASS, final hash | Onboarding rendered `Find the best time to go outside.` with localized `Tashkent`, `Samarkand`, and `Namangan`, search, and optional approximate location |
| Select quick city `Tashkent` | PASS, final hash | Persisted `Tashkent, Uzbekistan`; live current conditions, comparison, first-forecast tip, and timeline rendered; no TLS/CertPath/FATAL line |
| Persisted-location cold start | PASS, final hash | Explicit force-stop/start reopened live Tashkent; `TotalTime: 153 ms` |
| Search `Bukhara` without location permission | PASS, predecessor hash | The first result was `Bukhara, Uzbekistan`; selecting it rendered a live 95°F forecast |
| Clean-data start without connectivity | PASS / handled, predecessor hash | UI rendered `Weather is out of reach`, `Try again`, and `Change place` without a process crash |
| Use `Change place` while offline | PASS, predecessor hash | The place picker remained available and showed quick cities, saved Toshkent, search, and optional location |
| Restore connectivity and select Toshkent | PASS, predecessor hash | Live weather rendered after the same recovery flow; no TLS/CertPath/FATAL line |
| Process stability | PASS within these paths | No Nimbo fatal process crash was present in logcat |

Screenshots and UI trees:

- [Initial clean onboarding](evidence/android-emulator-2026-08-28/api24-onboarding.png) · [UI tree](evidence/android-emulator-2026-08-28/api24-onboarding.xml)
- [Final localized onboarding](evidence/android-emulator-2026-08-28/api24-final-localized-onboarding.png) · [UI tree](evidence/android-emulator-2026-08-28/api24-final-localized-onboarding.xml)
- [Final localized Tashkent forecast](evidence/android-emulator-2026-08-28/api24-final-localized-tashkent.png) · [UI tree](evidence/android-emulator-2026-08-28/api24-final-localized-tashkent.xml) · [cold-start UI tree](evidence/android-emulator-2026-08-28/api24-final-localized-cold.xml)
- [Final live Bukhara forecast](evidence/android-emulator-2026-08-28/api24-final-bukhara.png) · [UI tree](evidence/android-emulator-2026-08-28/api24-final-bukhara.xml)
- [Final offline error UI tree](evidence/android-emulator-2026-08-28/api24-final-offline-error.xml)
- [Final offline Change place UI tree](evidence/android-emulator-2026-08-28/api24-final-offline-picker.xml)
- [Final recovered Toshkent forecast](evidence/android-emulator-2026-08-28/api24-final-recovered.png) · [UI tree](evidence/android-emulator-2026-08-28/api24-final-recovered.xml)

### API 36 (`Nimbo_API_36`)

| Scenario | Result | Direct evidence |
|---|---|---|
| Install final APK | PASS | `adb install -r` returned `Success`; installed APK hash matched the host APK |
| Clean first launch | PASS, final hash | Onboarding rendered the value statement, localized `Tashkent`, `Samarkand`, and `Namangan`, city search, and optional approximate location |
| Select quick city `Tashkent` | PASS, final hash | Live forecast rendered location, current conditions, yesterday comparison, first-forecast tip, and `24 hours before · now · 24 hours ahead` |
| Cold start with saved location | PASS, final hash | Explicit force-stop/start reported `LaunchState: COLD`, `TotalTime: 688 ms`; content reopened for Tashkent |
| Request location | PASS, predecessor hash | Platform prompt explicitly requested approximate location |
| Deny location | PASS, predecessor hash | Permission remained `granted=false`; app returned to onboarding with `Location access wasn’t granted. Search for a city instead.` |
| Search `Bukhara` after denial | PASS, predecessor hash | First visible result was `Bukhara, Uzbekistan`; additional country-disambiguated results were displayed |
| Select `Bukhara, Uzbekistan` | PASS, predecessor hash | Live forecast rendered location, current conditions, yesterday comparison, first-forecast tip, and timeline |
| Process stability | PASS within this path | No `Process: uz.ganikhodjaev.weather` crash line was present in logcat |

Screenshots and UI trees:

- [Clean onboarding](evidence/android-emulator-2026-08-28/api36-onboarding.png) · [UI tree](evidence/android-emulator-2026-08-28/api36-onboarding.xml)
- [Final localized onboarding](evidence/android-emulator-2026-08-28/api36-final-localized-onboarding.png) · [UI tree](evidence/android-emulator-2026-08-28/api36-final-localized-onboarding.xml)
- [Final localized Tashkent forecast](evidence/android-emulator-2026-08-28/api36-final-localized-tashkent.png) · [UI tree](evidence/android-emulator-2026-08-28/api36-final-localized-tashkent.xml) · [cold-start UI tree](evidence/android-emulator-2026-08-28/api36-final-localized-cold.xml)
- [Approximate-location prompt](evidence/android-emulator-2026-08-28/api36-location-permission.png) · [UI tree](evidence/android-emulator-2026-08-28/api36-location-permission.xml)
- [Denied-location fallback](evidence/android-emulator-2026-08-28/api36-location-denied.png) · [UI tree](evidence/android-emulator-2026-08-28/api36-location-denied.xml)
- [Bukhara search results](evidence/android-emulator-2026-08-28/api36-search-result.png) · [UI tree](evidence/android-emulator-2026-08-28/api36-search-result.xml)
- [First forecast](evidence/android-emulator-2026-08-28/api36-weather.png) · [UI tree](evidence/android-emulator-2026-08-28/api36-weather.xml)
- [Persisted-location cold start](evidence/android-emulator-2026-08-28/api36-cold-start.png) · [UI tree](evidence/android-emulator-2026-08-28/api36-cold-start.xml)
- [Final-APK Bukhara forecast](evidence/android-emulator-2026-08-28/api36-final-weather.png) · [UI tree](evidence/android-emulator-2026-08-28/api36-final-weather.xml)
- [Final-APK persisted cold start UI tree](evidence/android-emulator-2026-08-28/api36-final-cold.xml)

## API 24 initial TLS finding and scoped resolution

The emulator network was connected and validated:

```text
DNS: 10.0.2.3
ping api.open-meteo.com: 1 packet transmitted, 1 received, 0% packet loss
Connectivity capability: INTERNET ... VALIDATED
```

Before the compatibility fix, the standalone diagnostic source [TlsProbe.java](evidence/android-emulator-2026-08-28/TlsProbe.java) used Android's default `HttpsURLConnection`; it did not use Nimbo code or configuration. On API 24, both exact API calls produced the same complete cause chain:

Full captured stdout is in [tls-probe-output.txt](evidence/android-emulator-2026-08-28/tls-probe-output.txt).

```text
javax.net.ssl.SSLHandshakeException:
  java.security.cert.CertPathValidatorException:
    Trust anchor for certification path not found.
Caused by: java.security.cert.CertificateException:
  java.security.cert.CertPathValidatorException:
    Trust anchor for certification path not found.
Caused by: java.security.cert.CertPathValidatorException:
  Trust anchor for certification path not found.
```

The frames include `com.android.org.conscrypt.TrustManagerImpl.checkTrustedRecursive`, `OpenSSLSocketImpl.verifyCertificateChain`, and `com.android.okhttp.Connection.connectTls`. The same probe returned HTTP `200` and JSON on API 36 for both endpoints:

```text
https://geocoding-api.open-meteo.com/v1/search?name=Bukhara&count=1&language=en&format=json
https://api.open-meteo.com/v1/forecast?latitude=39.77&longitude=64.43&current=temperature_2m
```

The API 24 system WebView (`WebView Browser Tester 53.0.2785.124`) also logged:

```text
X509Util: Failed to validate the certificate chain, error:
java.security.cert.CertPathValidatorException: Trust anchor for certification path not found.
```

Its capture is [api24-webview-open-meteo.png](evidence/android-emulator-2026-08-28/api24-webview-open-meteo.png) with the corresponding [UI tree](evidence/android-emulator-2026-08-28/api24-webview-open-meteo.xml).

At test time, both Open-Meteo certificates were valid for the emulator clock:

```text
geocoding-api.open-meteo.com: 2026-08-17 through 2026-11-15 GMT
api.open-meteo.com:             2026-07-16 through 2026-10-14 GMT
```

Both hosts served this chain:

```text
Open-Meteo leaf
  -> Let's Encrypt YR2
  -> ISRG Root YR
  -> ISRG Root X1
```

The tested API 24 system CA directory had 148 certificates and **no ISRG root**. The API 36 system CA directory had both `ISRG Root X1` and `ISRG Root X2`. These observations distinguish the initial failure from an invalid or expired Open-Meteo certificate.

The fix is declared in `app/src/main/res/xml/network_security_config.xml` and referenced by the application manifest. It trusts the system store everywhere, and adds the official ISRG Root X1/X2 only for `api.open-meteo.com`, `air-quality-api.open-meteo.com`, and `geocoding-api.open-meteo.com`, with `includeSubdomains=false`. `scripts/check_repository.py` parses that policy and verifies the exact DER certificate fingerprints. The final API 24 app paths above succeeded while the independent system probes remained unchanged.

## Exact core commands

```sh
/Users/khasan/Library/Android/sdk/emulator/emulator -avd Steppe_API24 -port 5554 -no-window -no-audio -no-snapshot-load -no-snapshot-save -gpu swiftshader_indirect
/Users/khasan/Library/Android/sdk/emulator/emulator -avd Nimbo_API_36 -port 5556 -no-window -no-audio -no-snapshot-load -no-snapshot-save -gpu swiftshader_indirect

/Users/khasan/Library/Android/sdk/platform-tools/adb -s emulator-5554 install -r app/build/outputs/apk/debug/app-debug.apk
/Users/khasan/Library/Android/sdk/platform-tools/adb -s emulator-5556 install -r app/build/outputs/apk/debug/app-debug.apk
/Users/khasan/Library/Android/sdk/platform-tools/adb -s emulator-5554 shell pm clear uz.ganikhodjaev.weather
/Users/khasan/Library/Android/sdk/platform-tools/adb -s emulator-5556 shell pm clear uz.ganikhodjaev.weather
/Users/khasan/Library/Android/sdk/platform-tools/adb -s emulator-5554 shell am start -W -n uz.ganikhodjaev.weather/.MainActivity
/Users/khasan/Library/Android/sdk/platform-tools/adb -s emulator-5556 shell am start -W -n uz.ganikhodjaev.weather/.MainActivity

# UI evidence used adb input tap/text, uiautomator dump, screencap, and adb pull.
# The TLS probe was compiled with javac + Android build-tools d8, pushed to
# /data/local/tmp/nimbo-tls-probe/classes.dex, then run as follows:
CLASSPATH=/data/local/tmp/nimbo-tls-probe/classes.dex app_process /system/bin TlsProbe \
  'https://geocoding-api.open-meteo.com/v1/search?name=Bukhara&count=1&language=en&format=json' \
  'https://api.open-meteo.com/v1/forecast?latitude=39.77&longitude=64.43&current=temperature_2m'
```

## Remaining boundary

This is emulator evidence only. Physical API 24/36, tablets, RTL, TalkBack, widget, and Wear OS are not claimed by this report. API 24 live weather and recovery are no longer a blocker on the tested image; representative physical-device QA remains a separate release gate.

Both no-snapshot emulators were shut down after evidence capture. The final
`adb devices -l` contained only the two pre-existing physical devices; the
temporary General Mobile debug installation was removed as documented in the
physical-device report.
