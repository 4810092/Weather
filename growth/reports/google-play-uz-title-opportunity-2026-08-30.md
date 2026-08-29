# Google Play UZ Uzbek-fallback title opportunity — 2026-08-30

Status: **APPLIED TO REPOSITORY DRAFT; NOT SUBMITTED OR PUBLISHED**.

## Decision

Change the unpublished Uzbekistan country-listing title for the `en-US`
store-locale fallback serving the Uzbek audience:

- before: `Nimbo: Ob-havo va prognoz`
- after: `Nimbo Weather: Ob-havo`

The Russian `ru-RU` title remains `Nimbo: Погода и прогноз`. The new
Uzbek-fallback title is 22 characters, within Google Play's 30-character
limit. It retains the exact local `Ob-havo` phrase and adds no feature,
accuracy, safety, or ranking claim.

## Evidence

The canonical logged-out UZ capture at `2026-08-30T00:00:25+05:00` showed
Nimbo below the observed first 30 Weather-category apps on all three fixed
Google profiles and meeting Top-10 quorum for 0 of 5 generic queries.

The fallback title is relevant to the fixed `uz-UZ` and `en-UZ` profiles. In
their visible Top-10 result titles:

| Surface | `uz-UZ` titles containing `Weather` | `en-UZ` titles containing `Weather` | Titles containing literal `prognoz` |
| --- | ---: | ---: | ---: |
| Weather category | 9/10 | 9/10 | 0/20 combined |
| `weather` search | 9/10 | 10/10 | 0/20 combined |
| `prognoz` search | 10/10 | 9/10 | 0/20 combined |

Across the two `weather` query Top-10 sets, `Weather` therefore appeared in
19/20 titles. Across the two `prognoz` query Top-10 sets, `Weather` also
appeared in 19/20 titles while the literal `prognoz` appeared in 0/20. The
full Uzbek description continues to use `prognoz` naturally, so the concept
is not removed from the listing payload.

This is correlational public-store evidence. It supports one bounded metadata
choice; it does not prove that title metadata alone changes rank or guarantee
Top-10 placement.

## Source and operational boundary

- Canonical capture: `growth/data/public-rank/2026-08-30.json`
- Capture SHA-256:
  `aa9028a53caa546886517ec6ea93951e19473a17b70f9a1d63f2ce9d38f0f75d`
- Country parameter: `gl=UZ`
- Profiles: logged out `hl=uz` / `uz-UZ` and `hl=en` / `en-UZ`
- Counting rule: case-insensitive literal term presence in the first ten
  unique app titles returned by each captured public surface

The metadata stays `draft`. This change does not authorize a Console write,
review submission, publication, release, outreach message, paid campaign, or
provider-scope change. The current public-claims audit was revised and its
payload hash was repinned in the same repository change; any later payload
drift must fail the gate until another explicit audit.
