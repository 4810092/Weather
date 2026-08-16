# Store privacy declarations — Nimbo 1.0

Reviewed against the Android manifest, iOS Info.plist/privacy manifest, Ktor
endpoints, SQLDelight schema, and dependency graph on August 10, 2026.

## Source-of-truth behavior

| Data or capability | Behavior |
| --- | --- |
| Approximate location | Optional foreground permission. Coordinates are rounded to two decimals before local storage, HTTPS transmission to Open-Meteo, or system reverse geocoding for the displayed city name. |
| Precise location | Not retained or transmitted by Nimbo, even if iOS grants precise access. |
| City search | Query text is sent over HTTPS to Open-Meteo geocoding. |
| Local storage | Up to ten saved places, bounded weather/AQI cache and snapshots, units, refresh metadata, and a compact widget/watch snapshot. Android backup is disabled; iOS backup follows the user's system settings. |
| Provider retention | Open-Meteo states that API logs may include IP, URL, coordinates, and are deleted after 90 days. |
| Accounts/identifiers | No account, advertising ID, vendor ID, installation ID, or custom identifier. |
| Analytics/ads/crashes | No analytics, advertising, attribution, telemetry, or crash-reporting SDK. |
| Store reviews | After four distinct successful updates, Nimbo may invoke the platform-owned in-app review prompt once per version. Review content is handled by the store and is not stored by Nimbo. |
| Tracking | None. |

## Google Play Data safety answers

- Data collected: **Yes**.
- Data encrypted in transit: **Yes** (HTTPS only).
- Account creation/deletion: **No account is offered**.
- Approximate location: collected optionally; purpose **App functionality**; not
  used for advertising, analytics, or personalization. It is not ephemeral because
  the provider documents API-log retention. Open-Meteo is the weather service
  provider; answer **not shared** under the service-provider exception only if the
  console's current wording still matches this relationship.
- In-app search history: collected optionally when city search is used; purpose
  **App functionality**; same provider/service-provider treatment and retention.
- Precise location, personal information, financial information, messages, media,
  contacts, app activity other than city search, web browsing, app diagnostics,
  and device IDs: **not collected**.
- Data deletion: active local data is removed on uninstall; users can replace the
  active place in-app. iOS system backups remain governed by the user's backup
  settings. Provider logs expire under Open-Meteo's 90-day policy.

Google defines collection as transmission off-device and specifically lists a
weather app sending location as an example. Reconfirm the service-provider answer
in the live form before publishing:
[Google Play Data safety guidance](https://support.google.com/googleplay/android-developer/answer/10787469?hl=en).

## Apple App Privacy answers

- Data collection: **Yes**.
- Coarse Location: **App Functionality**, not linked to identity, not used for
  tracking.
- Search History: **App Functionality**, not linked to identity, not used for
  tracking.
- Precise Location and all other categories: **not collected**.
- Tracking: **No**; ATT is not used or required.

These answers match `iosApp/Nimbo/PrivacyInfo.xcprivacy`. Apple defines collection
as off-device transmission retained beyond real-time servicing; Open-Meteo's
90-day log policy makes disclosure appropriate:
[Apple App Privacy details](https://developer.apple.com/app-store/app-privacy-details/).

## Required policy URLs

- Privacy: `https://github.com/4810092/Weather/blob/master/docs/PRIVACY.md`
- Support: `https://github.com/4810092/Weather/issues`

The public privacy URL is also reachable from inside Nimbo. Re-audit this document
before any provider, endpoint, dependency, permission, or telemetry change.
