# Open-Meteo capacity contingency — 2026-08-29

Status: **implemented request-throttling; written clearance confirmed for the
exact unpaid, non-monetized organic-promotion scope**. OpenMeteo GmbH confirmed
that scope in ticket `234272` on 2026-08-29; the authenticated record and its
limits are preserved in
[`open-meteo-clarification-email.md`](open-meteo-clarification-email.md).
No endpoint, API key, subscription, proxy, or budget was changed.

## Official constraints

- The [Open-Meteo terms](https://open-meteo.com/en/terms) limit the free API to
  non-commercial use and fewer than 10,000 calls per day, 5,000 per hour, and
  600 per minute. They separately list promotional activities as commercial.
- The [pricing page](https://open-meteo.com/en/pricing) says a commercial
  subscription supplies an API key for `customer-api.open-meteo.com` and lists
  monthly capacities of 1M calls for Standard, 5M for Professional, and 50M+
  for Enterprise. The public server-rendered page does not expose a monetary
  amount, so this repository records no guessed price.
- Open-Meteo states that one HTTP request is usually one call, but requests with
  more than 10 variables or more than two weeks of data may count as multiple
  calls. Nimbo therefore does not equate HTTP attempts with billed call units.

## Source-derived request model

One foreground refresh currently performs:

1. one 10-day forecast request with one past day;
2. one seven-day history request; and
3. one air-quality request.

Each request can make up to two additional attempts for transient failures.
City search adds one geocoding request and may add one English fallback request.
Background refresh performs the primary forecast and optional air-quality
request, but not the seven-day history request.

Before the 2026-08-29 throttling change, an uninterrupted foreground session
could start that three-request refresh cycle every 15 minutes, while Android
and iOS background scheduling requested another cycle from a 30-minute
interval. That was nominally 12 foreground HTTP requests per active hour before
background work, manual actions, geocoding, or retries.

The current policy keeps the 15-minute foreground freshness check but permits
an automatic provider refresh only when the cached primary forecast is at least
one hour old. Android periodic work and the earliest iOS background request are
also moved to one hour, and background execution publishes a fresh cached
snapshot without calling the provider. Failed automatic attempts are also
limited to once per hour per location. A durable `InFlight` / `Cooldown` /
`RetryPending` record survives a cold start: transient background work keeps
returning retry during the remaining cooldown without spending another
provider call, then permits one new attempt when the hour is due. Cache-read or
durable-state failures fail closed without a provider call. Manual refresh and
first-location load remain immediate. Foreground and platform background paths
share a process-wide, per-location single-flight lock and re-read the cache
after acquiring it, so an hour boundary cannot start duplicate automatic
refreshes in the same process.
Future cache/attempt timestamps caused by a wall-clock correction are treated
as due instead of suppressing refresh indefinitely.

For capacity planning, use this nominal HTTP-request formula before retry
expansion:

`3 × eligible activation cycles + 3 × eligible foreground cycles + 2 × eligible background cycles + geocoding requests`

The retry ceiling is three attempts per request. Provider-billed call units may
be higher than HTTP requests because the forecast payload uses more than ten
variables; a commercial decision therefore needs an observed customer usage
definition or an explicit Open-Meteo answer, not only this formula.

## Verification

- Shared tests cover fresh-cache activation/background skips, the exact
  one-hour boundary, durable transient retry deferral and the later real retry,
  stale completion tokens, manual retry, deletion cleanup, different-location
  independence, cache/state failure, future timestamps, and concurrent
  automatic-path coalescing.
- `ktlintCheck`, all shared Android-host/iOS Simulator tests, Android unit
  tests, SQLDelight migration verification, and phone/Wear release bundle builds
  pass locally.
- Unsigned Release simulator builds pass for the iOS app/widget and watchOS app.
  This is source/build evidence only; no signed artifact, physical-device pass,
  endpoint change, API key, subscription, upload, or publication is claimed.

## Decision boundary

- Provider clearance no longer blocks the described unpaid organic activity.
  Acquisition and outreach remain paused only while the independent crash,
  exact signed-artifact, physical-device, and release gates remain blocked.
- Re-open the provider decision before monetization, paid promotion,
  sponsorships, referral or affiliate revenue, attribution changes, Free API
  limit changes, or any other material change to the confirmed facts.
- If commercial access is required, do not embed the customer API key in the
  app. Design a server-side proxy/customer endpoint with secrets outside the
  clients, request coalescing, cache controls, rate limits, and fail-closed
  observability.
- Do not buy a plan or switch endpoints until the monetary price, billing
  owner, proxy operating cost, and explicit budget authorization are recorded.
