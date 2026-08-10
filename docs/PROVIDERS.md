# Provider attribution and deployment terms

Nimbo currently uses:

- [Open-Meteo](https://open-meteo.com/) for forecast and historical model/reanalysis weather data. Open-Meteo data is attributed in the app next to the weather UI. The app deliberately describes historical values as historical weather/context, not verified station observations.
- [GeoNames](https://www.geonames.org/) for manual city search, with attribution in the app.

The public Open-Meteo endpoint is suitable only while the deployed app satisfies its non-commercial and usage conditions. A monetized/commercial release must use an appropriate paid Open-Meteo plan/customer endpoint and must not ship its API key in the client. This is a release-configuration requirement, not an optional documentation detail.

Provider terms, attribution requirements, endpoint selection, and privacy declarations must be reviewed before each store release. Changing providers requires updates to the privacy source of truth, app attribution, store disclosures, and ADR 0001.
