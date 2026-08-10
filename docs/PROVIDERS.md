# Provider attribution and deployment terms

Nimbo currently uses:

- [Open-Meteo](https://open-meteo.com/) for forecast and historical model/reanalysis weather data and its geocoding endpoint for manual city search. Open-Meteo data is attributed and linked in the app next to the weather UI. The app deliberately describes historical values as historical weather/context, not verified station observations.
- [GeoNames](https://www.geonames.org/) is the underlying location database used by Open-Meteo geocoding and is credited in the app. Nimbo does not call GeoNames directly.

The public Open-Meteo endpoint is suitable only while the deployed app has no subscription or advertising and satisfies the provider's non-commercial and usage conditions. A monetized/commercial release must use an appropriate paid Open-Meteo plan/customer endpoint and must not ship its API key in the client. This is a release-configuration requirement, not an optional documentation detail.

Open-Meteo currently licenses API data under CC BY 4.0 and requires a link next to displayed data. Its geocoding data is based on GeoNames under a CC BY licence. The in-app attribution is a link to Open-Meteo and identifies GeoNames as the underlying place source. See the provider's [licence](https://open-meteo.com/en/license), [terms/privacy](https://open-meteo.com/en/terms), and [geocoding documentation](https://open-meteo.com/en/docs/geocoding-api).

Provider terms, attribution requirements, endpoint selection, and privacy declarations must be reviewed before each store release. Changing providers requires updates to the privacy source of truth, app attribution, store disclosures, and ADR 0001.
