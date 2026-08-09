# ADR 0001: Weather and geocoding provider

Status: accepted for v1  
Date: 2026-08-09

## Context

Nimbo needs global current/hourly data, recent observations, historical forecast access, location timezones, city search, forecast snapshots, and an open-source-friendly integration without shipping a secret.

## Options

- Open-Meteo: keyless non-commercial/open-source tier, global multi-model forecast, archive and historical forecast APIs, current/hourly fields, and GeoNames-based multilingual geocoding. It requires attribution and commercial deployments require the customer endpoint/terms.
- MET Norway Locationforecast: strong public service and global forecast, but richer Nordic behavior and no convenient historical observation/forecast API for this product.
- WeatherAPI.com: broad integrated feature set and commercial use, but free history is only one day, a client API key is required, attribution is required on free use, and cache retention is constrained.
- Tomorrow.io: capable current/forecast/history products, but API-key management and plan limits add release and open-source friction.

## Decision

Use Open-Meteo as the single v1 weather provider and its geocoding API for city search. Show required Open-Meteo and GeoNames attribution. Keep provider DTOs behind repository interfaces and make base URLs configurable so commercial customer infrastructure or a fallback can be introduced without changing domain/UI.

## Consequences

The app ships without a weather secret and can support observations, issued-forecast history, and stored local snapshots. The public endpoint is appropriate only while Nimbo remains within Open-Meteo's non-commercial/fair-use terms; a commercial launch must switch to an appropriate plan or self-hosted endpoint before release.

