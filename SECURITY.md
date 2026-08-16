# Security policy

## Reporting a vulnerability

Report suspected vulnerabilities through [GitHub private vulnerability reporting](https://github.com/4810092/Weather/security/advisories/new). Do not open a public issue or discussion containing credentials, exploit details, precise user location, signing material, or unpublished store configuration.

Include the affected commit/version, platform, impact, and a minimal reproduction when possible. Do not send production secrets or personal location databases as evidence; use redacted logs and synthetic data.

The maintainer will acknowledge a complete report, assess impact, coordinate remediation, and agree on disclosure timing with the reporter. This is a response process, not a guaranteed response-time SLA.

## Supported versions

Security fixes target the current default branch and the latest publicly distributed application version when a fix can be released. Older Git tags are historical checkpoints and are not maintained release lines.

## Scope notes

Nimbo is a client application that uses Open-Meteo and platform geocoding services. Provider availability or forecast accuracy alone is not a security vulnerability. Valid security and privacy reports include unintended disclosure of stored location/weather data, unsafe exported components, dependency vulnerabilities with a demonstrated impact, or a way to bypass the documented coarse-location boundary.

See [Privacy](docs/PRIVACY.md) for the data flow and [Providers](docs/PROVIDERS.md) for external-service constraints.
