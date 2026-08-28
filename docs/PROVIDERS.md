# Provider attribution and deployment terms

Last reviewed against Open-Meteo’s published terms, licence, and geocoding documentation on August 28, 2026.

## Current integrations

- [Open-Meteo](https://open-meteo.com/) provides forecast/recent historical model data, air-quality data, and the geocoding endpoint used by manual city search.
- [GeoNames](https://www.geonames.org/) is the location database underlying Open-Meteo geocoding. Nimbo does not call GeoNames directly.
- Android and iOS platform geocoders may resolve a coarsened device coordinate to a display city/country under the platform provider’s terms.

The endpoints and requested fields are visible in [OpenMeteoService](../shared/src/commonMain/kotlin/uz/ganikhodjaev/weather/shared/data/OpenMeteoService.kt). Provider DTOs are mapped to Nimbo models before persistence or UI use.

### Android API 24 trust compatibility

Some Android 7 system images predate the ISRG roots used by Open-Meteo's current
Let's Encrypt certificate chain. The phone/tablet app therefore keeps system
trust as its base and adds the official public ISRG Root X1 and X2 certificates
only for these exact hosts:

- `api.open-meteo.com`;
- `air-quality-api.open-meteo.com`;
- `geocoding-api.open-meteo.com`.

The scoped policy is in
[`network_security_config.xml`](../app/src/main/res/xml/network_security_config.xml).
It does not trust user-installed certificates, does not disable hostname or
certificate validation, and rejects cleartext traffic. The checked-in X1 and X2
certificate fingerprints are enforced by `scripts/check_repository.py`; their
official source is [Let's Encrypt's certificate registry](https://letsencrypt.org/certificates/).
Review the live provider chain on every release and remove or replace these
anchors if the provider, Android floor, or ISRG chain changes. The bundled roots
expire in 2035 and 2040 respectively, so their presence is not an unattended
long-term endpoint strategy.

## Attribution

Open-Meteo states that API data are available under CC BY 4.0 and requires a link next to displayed Open-Meteo data. Its geocoding documentation identifies GeoNames as the location-data source. Nimbo includes an in-app linked Open-Meteo attribution and names GeoNames as the place-data basis.

See Open-Meteo’s current [licence](https://open-meteo.com/en/license) and [geocoding documentation](https://open-meteo.com/en/docs/geocoding-api). A release review must confirm that in-app and store attribution still matches the current requirements.

## Free-endpoint constraint

Open-Meteo’s current free/open-access terms limit the service to non-commercial use and published request limits. A subscription or advertising-supported application is listed as commercial use. A commercial, monetized, or higher-volume deployment of Nimbo must switch to an appropriate customer or self-hosted endpoint before release and must not embed a customer API key in a public client.

The August 2026 growth plan treats public organic promotion as a provider gate,
not as an assumed extension of the free tier. Campaign outreach and coordinated
promotion must remain paused until Open-Meteo gives written confirmation that the
planned non-monetized organic promotion is permitted, or Nimbo moves to an
approved customer/self-hosted endpoint. The existing client endpoint does not
change merely to start growth work, and any future commercial credential belongs
behind separately reviewed server-side infrastructure rather than in a mobile
binary.

See the current [terms and privacy notice](https://open-meteo.com/en/terms) and [pricing](https://open-meteo.com/en/pricing). Provider terms can change; this document is a release checklist, not legal advice.

## Privacy and retention

Open-Meteo states that free-service webserver logs may include IP addresses and sensitive request information such as coordinates for troubleshooting, are not shared with third parties, and are deleted after 90 days. That external processing is why Nimbo’s store declarations treat approximate location and city search as collected for app functionality even though Nimbo has no account or analytics SDK.

Nimbo reduces device coordinates to two decimal places before provider transmission. Manual city-search text is transmitted as typed. See [PRIVACY.md](PRIVACY.md) and [store declarations](../store/privacy-declarations.md).

## Changing a provider

A provider or endpoint change must update, in the same reviewable change:

- ADR 0001 or a superseding ADR;
- request/response mapping and deterministic tests;
- in-app attribution and licences;
- privacy policy and store privacy declarations;
- store metadata when provider naming changes;
- endpoint/key configuration without committing secrets;
- Android domain-scoped trust anchors and their pinned public-root fingerprints;
- cache, error, rate-limit, and release assumptions.

Forecast accuracy and service availability are external dependencies. Nimbo does not claim a provider SLA or “most accurate” forecast.
