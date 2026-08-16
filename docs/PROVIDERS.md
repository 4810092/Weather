# Provider attribution and deployment terms

Last reviewed against Open-Meteo’s published terms, licence, and geocoding documentation on August 16, 2026.

## Current integrations

- [Open-Meteo](https://open-meteo.com/) provides forecast/recent historical model data, air-quality data, and the geocoding endpoint used by manual city search.
- [GeoNames](https://www.geonames.org/) is the location database underlying Open-Meteo geocoding. Nimbo does not call GeoNames directly.
- Android and iOS platform geocoders may resolve a coarsened device coordinate to a display city/country under the platform provider’s terms.

The endpoints and requested fields are visible in [OpenMeteoService](../shared/src/commonMain/kotlin/uz/ganikhodjaev/weather/shared/data/OpenMeteoService.kt). Provider DTOs are mapped to Nimbo models before persistence or UI use.

## Attribution

Open-Meteo states that API data are available under CC BY 4.0 and requires a link next to displayed Open-Meteo data. Its geocoding documentation identifies GeoNames as the location-data source. Nimbo includes an in-app linked Open-Meteo attribution and names GeoNames as the place-data basis.

See Open-Meteo’s current [licence](https://open-meteo.com/en/license) and [geocoding documentation](https://open-meteo.com/en/docs/geocoding-api). A release review must confirm that in-app and store attribution still matches the current requirements.

## Free-endpoint constraint

Open-Meteo’s current free/open-access terms limit the service to non-commercial use and published request limits. A subscription or advertising-supported application is listed as commercial use. A commercial, monetized, or higher-volume deployment of Nimbo must switch to an appropriate customer or self-hosted endpoint before release and must not embed a customer API key in a public client.

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
- cache, error, rate-limit, and release assumptions.

Forecast accuracy and service availability are external dependencies. Nimbo does not claim a provider SLA or “most accurate” forecast.
