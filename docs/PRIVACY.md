# Nimbo privacy policy

Effective date: August 10, 2026

Nimbo is published by GANIKHODJAYEV KHASAN ASKAROVICH, YATT. The app has no
account, advertising, analytics, crash-reporting SDK, or background location.

## Data used to provide weather

Location permission is optional. Nimbo requests foreground approximate location
only after the user chooses that option. Before any storage or network request,
device coordinates are reduced to two decimal places (roughly kilometre-scale).
The reduced coordinates are sent over HTTPS to Open-Meteo to return weather for
that area. A user may instead search for a city without granting location access;
the search text is sent over HTTPS to Open-Meteo's geocoding service.

Open-Meteo says its free API server logs may contain IP addresses, requested
coordinates, and request URLs for troubleshooting and abuse prevention, and that
individual log files are deleted after 90 days. Open-Meteo does not receive a
Nimbo account ID, advertising ID, or other identifier from the app. Its current
terms and privacy notice are available at
[open-meteo.com/en/terms](https://open-meteo.com/en/terms).

## Data stored on the device

Nimbo stores one selected place, cached weather, short-lived forecast snapshots,
unit preferences, and refresh metadata in its local database. Selecting another
place removes the previous place and its cached weather. Weather rows are kept for
at most eight days in the past and three days in the future; forecast snapshots are
kept for 14 days. Uninstalling Nimbo removes its data because cloud/device backup
is disabled on Android. On iOS, system backups can retain app data according to
the user's iCloud or device-backup settings; removing those backups is controlled
by the user in Apple settings. Nimbo does not maintain a location trail or access
location in the background.

## Tracking and sharing

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
