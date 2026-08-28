# Nimbo privacy policy

Effective date: August 10, 2026

Last reviewed against the implementation and provider terms: August 28, 2026

Canonical public policy: [nimbo.uz/privacy](https://nimbo.uz/privacy/)

Nimbo is published by GANIKHODJAYEV KHASAN ASKAROVICH, YATT. The app has no
account, advertising, analytics, crash-reporting SDK, or background location.

## Data used to provide weather

Location permission is optional. Nimbo requests foreground approximate location
only after the user chooses that option. Before any storage or network request,
device coordinates are reduced to two decimal places (roughly kilometre-scale).
The reduced coordinates are sent over HTTPS to Open-Meteo to return weather for
that area. Nimbo also asks the device's Android or iOS reverse-geocoding service
to turn the reduced coordinates into a city and country for display. That system
service may process the request over the network under the platform provider's
terms. A user may instead search for a city without granting location access; the
search text is sent over HTTPS to Open-Meteo's geocoding service.

Open-Meteo says its free API server logs may contain IP addresses, requested
coordinates, and request URLs for troubleshooting and abuse prevention, and that
individual log files are deleted after 90 days. Open-Meteo does not receive a
Nimbo account ID, advertising ID, or other identifier from the app. Its current
terms and privacy notice are available at
[open-meteo.com/en/terms](https://open-meteo.com/en/terms).

## Data stored on the device

Nimbo stores up to ten selected places, cached weather and air quality, short-lived
forecast snapshots, unit preferences, and refresh metadata in its local database.
Weather rows are kept for at most eight days in the past and eleven days in the
future; forecast snapshots are kept for 14 days. A compact copy of current weather
is stored locally for home-screen widgets and synchronized to a paired watch. This
watch/widget data contains no account or device identifier. Uninstalling Nimbo
removes its data because cloud/device backup is disabled on Android. On iOS,
system backups can retain app data according to
the user's iCloud or device-backup settings; removing those backups is controlled
by the user in Apple settings. Nimbo does not maintain a location trail or access
location in the background.

## Tracking and sharing

Nimbo can open the platform-owned App Store or Google Play review prompt only
after at least three successful foreground forecasts on two different local days
and while useful forecast content is visible. A completed platform request is
recorded at most once per app version; a request that cannot be launched remains
eligible for retry. Any review a user chooses to submit is handled by the store
under Apple’s or Google’s terms; Nimbo does not receive or store review text.

Nimbo does not sell data, build advertising profiles, or track users across apps
or websites. Open-Meteo processes approximate location and city-search requests
only to provide weather/place results and operate its API. Its provider-side
processing and retention apply to those requests.

## User choices

Users can avoid location permission and use city search, change the selected place
inside Nimbo, revoke location permission in system settings, or uninstall the app
to delete local data. Provider log questions or deletion requests must be directed
to Open-Meteo using the contact in its privacy notice because Nimbo has no account
or identifier with which to locate a provider log entry.

Questions about Nimbo privacy can be raised through the public repository's
[security contact](../SECURITY.md).

This document is the release source of truth and must be updated before shipping
any analytics, diagnostics, account, advertising, or provider change.
