# App Store Connect API readiness — 2026-08-29

Status: **PASS for bounded inventory reads; BLOCKED for diagnostics and draft
writes**.

No build was uploaded, attached, submitted, released, or made public. The one
bounded create attempt described below was rejected before a version resource
was created; a final read confirmed that App Store Connect contains no Nimbo
`1.1.0` version or partial localization draft.

## Authenticated inventory

At `2026-08-29 22:56 +05:00`, an existing maintainer-owned Team/Individual API
key outside this repository authenticated successfully. Read-only requests
resolved:

- app id `6799886897`, name `Nimbo Weather`, bundle id
  `uz.ganikhodjaev.weather`;
- public iOS `1.0.1`, version id
  `147bee33-68c6-4490-ac07-4661b30b4af4`, ready for distribution/sale, release
  type `AFTER_APPROVAL`, with build `4` valid;
- public iOS `1.0`, ready for sale, with build `2` valid;
- builds `1`, `2`, `3`, and `4`, all valid, with no build `5` or `6` present;
- twelve localizations on the current `1.0.1` version: `ar-SA`, `de-DE`,
  `en-US`, `es-ES`, `fr-FR`, `hi`, `ja`, `ko`, `pt-PT`, `ru`, `tr`, and
  `zh-Hans`;
- zero existing analytics report requests.

The build-detail and diagnostic-signature requests for build `4` both returned
HTTP 403 `FORBIDDEN_ERROR` for security reasons. This authenticated key therefore
cannot retrieve the suppressed historical crash signature or log.

## Bounded 1.1.0 draft attempt

Preflight reads proved that an iOS `1.1.0` version did not exist. A single
request then attempted to create only an App Store version with:

- platform `IOS`;
- version string `1.1.0`;
- release type `MANUAL`;
- `usesIdfa=false`.

App Store Connect rejected the request with HTTP 403 `FORBIDDEN_ERROR` because
the key is not allowed to perform that operation. No localization, app-info,
screenshots, Custom Product Page, age rating, pricing, build association,
submission, or release request followed. A final authenticated GET returned
zero `1.1.0` versions, proving that no partial draft was left behind.

## Local credential hygiene

A bounded metadata scan located four maintainer-owned regular-file copies of
the same private key outside this repository. Before changing permissions, all
four were mode `0644`, 257 bytes, and byte-identical by SHA-256. Their filesystem
permissions were changed to `0600` on the exact verified paths only; owner,
size, and SHA-256 remained unchanged. No key contents were printed, moved,
deleted, committed, or replaced.

## Decision

The read path is usable for inventory verification, but App Store Connect write
access is unavailable to this key. Creating the `1.1.0` draft requires an
existing write-capable account/session or a separately authorized key/role.
Diagnostics remain blocked by the security 403. Neither limitation is treated
as proof that the historical crash is resolved, and neither permits attaching
a build or submitting a release before the signed-artifact and physical QA
gates pass.

This record is authenticated API evidence, not proof of upload, review,
publication, rollout, or end-user availability.
