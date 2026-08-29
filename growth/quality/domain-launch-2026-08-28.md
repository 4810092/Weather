# `nimbo.uz` launch state — 2026-08-28, refreshed 2026-08-29

Status: **PASS — registrar activation, public delegation/DNS, matching TLS,
HTTPS enforcement, redirects, canonicals, and published routes are verified**.

## Completed

- GitHub Pages deployment `6147270106` for commit
  `584f47a83637ce3587ce980a69f392b84a57656b` completed successfully.
- GitHub Pages workflow run `33213699930` for earlier commit
  `53d4801d5d2012b300bb44959f08c32afe705045` also completed successfully.
- GitHub Pages workflow run `33235358445` for commit
  `738e008ecb0a74224f5ba4f283610f7c8629a4f9` completed successfully in 38
  seconds; its deployment step completed in 11 seconds.
- GitHub Pages workflow run `33236549322` deployed commit
  `6f036dff7cb4fc915faae3938a032335a697107c` while final TLS and redirect
  verification was performed.
- The repository Pages configuration uses the workflow build type and accepts
  `nimbo.uz` as its custom domain.
- The generated site uses `https://nimbo.uz` as the canonical origin for the
  Uzbek, Russian, and English landing, privacy, support, and press routes.
- The active registrar record and the `.uz` parent both contain the
  Cloudflare-assigned nameservers `jose.ns.cloudflare.com` and
  `sharon.ns.cloudflare.com`.
- The Cloudflare zone contains the complete DNS-only GitHub Pages record set:
  four `A`, four `AAAA`, and the `www` `CNAME`. The two authoritative
  nameservers and the Cloudflare and Google public resolvers now return this
  record set publicly.
- A direct HTTP request to the GitHub Pages edge with `Host: nimbo.uz` returned
  HTTP `200` with the expected site. This proves that the Pages origin can route
  the custom host, but it does not prove public DNS or HTTPS reachability.
- The existing `nimbo-uz-rank-monitor` heartbeat temporarily runs hourly and
  performs read-only registry delegation, public DNS, Pages health, HTTP/TLS,
  and canonical checks alongside rank evaluation.

## Activation chronology

At `2026-08-29 01:34 +05:00`, the public Webname status page reported
`Активацияни кутиш` (waiting for activation). The `.uz` WHOIS response reported
status `EXPIRED`, with both creation and expiration dates set to `28-Aug-2026`.
It also listed registrar `Arsenal-D` and the intended Cloudflare nameservers.

A read-only recheck at `2026-08-29 02:26 +05:00` returned the same WHOIS
status, DNSSEC-authenticated registry `NXDOMAIN`, no public `A`/`AAAA` answer,
and no resolvable HTTPS endpoint.

At `2026-08-29 03:07 +05:00`, the authenticated registrar list still showed
`nimbo.uz` as `Активируется`, WHOIS still reported `EXPIRED`, and the registry
still returned DNSSEC-authenticated `NXDOMAIN`. The Cloudflare dashboard showed
the zone as `pending` and its authoritative DNS table contained no records.

At `2026-08-29 05:22 +05:00`, the registry authority plus Cloudflare and Google
public resolvers still returned DNSSEC-authenticated `NXDOMAIN`, HTTPS could not
resolve the host, WHOIS still reported the domain record as `EXPIRED`, and the
Cloudflare zone still displayed "Waiting for your registrar to propagate your
new nameservers". No DNS record was created while delegation remained absent.

At `2026-08-29 05:53 +05:00`, all nine GitHub Pages records listed below had
been created in Cloudflare with proxying disabled, and an immediate Cloudflare
nameserver recheck had been requested. The authenticated registrar still showed
the correct assigned Cloudflare nameservers and status `Активируется`. The
authoritative `.uz` query and the Cloudflare and Google public resolvers still
returned `NXDOMAIN`, so public DNS and TLS remain blocked on registrar/registry
activation rather than on missing zone content.

At `2026-08-29 05:56 +05:00`, one authenticated registrar support ticket
(`#1665`) was created with status `Новый`, asking Arsenal-D to complete the
registration/delegation or identify any remaining owner action. The ticket list
was checked first and contained no existing duplicate for this activation issue.

At `2026-08-29 07:12–07:14 +05:00`, the registrar still showed
`Активируется`, ticket `#1665` still had status `Новый`, and no human reply had
arrived. The apparent top-level `ACTIVE` line in the combined WHOIS response
belongs to the IANA object for the `.UZ` ccTLD; both domain-specific
`NIMBO.UZ` sections still report `EXPIRED`. The Cloudflare child zone is ready:
both assigned nameservers authoritatively return all four `A`, four `AAAA`, and
the `www` `CNAME` records. However, both `.uz` registry authorities and the
Cloudflare and Google public resolvers still return DNSSEC-validated `NXDOMAIN`,
so the parent delegation and public TLS endpoint remain absent.

At `2026-08-29 07:43 +05:00`, domain-specific WHOIS still reported
`NIMBO.UZ` as `EXPIRED`. A fresh trace ended at the DNSSEC-signed `.uz` denial
of delegation, while direct queries to the assigned Cloudflare nameservers
continued to return the prepared child zone. A direct GitHub Pages edge probe
for `https://nimbo.uz/` failed certificate-name validation, so certificate
issuance is not claimed. Because the registrar's documented average activation
window had elapsed, one concise support follow-up referencing ticket `#1665`
was sent at approximately `07:45` to the registrar's official support routes.
It requested activation/delegation or an exact remaining owner action. No DNS
record was changed, no duplicate ticket was created, and no human reply is yet
recorded.

At `2026-08-29 08:12 +05:00`, a new read-only recheck again found
domain-specific WHOIS status `EXPIRED`, DNSSEC-authenticated parent
non-delegation, no public `A` or `AAAA` answer, and no resolvable HTTPS host.
The registrar follow-up remains the latest owner action; no further message or
DNS change was made.

At `2026-08-29 09:52 +05:00`, domain-specific `.uz` WHOIS changed to
`NIMBO.UZ` status `ACTIVE`, updated `29-Aug-2026`, with expiration
`29-Aug-2027` and the intended Cloudflare nameservers. This closes the expired
registrar-record part of the blocker. It does not yet prove delegation: the
authoritative `.uz` nameserver, Cloudflare resolver, and Google resolver still
returned DNSSEC-authenticated `NXDOMAIN`, while direct queries to
`jose.ns.cloudflare.com` continued to return the staged apex `A` records and
`www` CNAME. The authenticated Cloudflare Zone API still reported the zone as
`pending`. `https://nimbo.uz/` still could not resolve.

At `2026-08-29 10:14:37–10:16:25 +05:00`, both `.uz` authorities returned
`NOERROR` with the intended `jose.ns.cloudflare.com` and
`sharon.ns.cloudflare.com` delegation, and a DNSSEC trace completed through
the signed `.uz` zone to the Cloudflare child. Both child nameservers agreed on
the four apex `A` records, four apex `AAAA` records, `www` CNAME, NS, and SOA.
The Cloudflare and Google public resolvers also returned the same public record
set. The signed parent proves that the child has no `DS`; `nimbo.uz` is
therefore currently an unsigned/insecure delegation, not a DNSSEC-bogus zone.

HTTP origin routing now passes when resolved directly: the apex returns `200`
and `www` returns `301` to the apex. HTTPS remains invalid. The GitHub Pages
edge still presents a certificate with `CN=*.github.io` and no `nimbo.uz` or
`www.nimbo.uz` SAN; hostname verification fails and `curl --resolve` exits
`60`. The macOS system resolver API also retained an earlier negative cache at
the capture time even though direct local queries and both independent public
resolvers were already correct.

The registrar, parent delegation, authoritative DNS, and independent public
resolution parts of the gate now pass. Certificate issuance and end-to-end
HTTPS verification remain the only domain launch blocker.

At `2026-08-29 10:29–10:30 +05:00`, the authenticated GitHub Pages settings
page identified the latest deployment as live at `http://nimbo.uz/`, showed the
custom-domain status `DNS Check in Progress`, and kept `Enforce HTTPS` disabled
with the explicit reason that no certificate had yet been issued for
`nimbo.uz`. No Pages setting was changed during this read-only check.

At `2026-08-29 10:36–10:41 +05:00`, GitHub issued a Let's Encrypt certificate
with `CN=nimbo.uz`, SANs for `nimbo.uz` and `www.nimbo.uz`, validity from
`2026-08-29 04:32:08Z` through `2026-11-27 04:32:07Z`, and successful hostname
verification for both hosts. The authenticated Pages control became available,
`Enforce HTTPS` was enabled, and the checked state was verified. One UI capture
showed `DNS check successful`; a near-simultaneous reload retained the earlier
`DNS Check in Progress` label, which is treated as non-blocking control-plane
lag because the public data-plane checks below all pass.

After propagation, all four GitHub Pages IPv4 edges returned `301` from the
HTTP apex to `https://nimbo.uz/`. HTTP `www` reached the same HTTPS apex in two
redirects, and HTTPS `www` reached it in one. The final response was `200` with
certificate verification result `0` in every case.

All 12 intended localized HTML routes returned HTTPS `200` with the expected
self-canonical and `lang`: Uzbek at `/`, `/press/`, `/privacy/`, `/support/`;
Russian at `/ru/` plus its three localized routes; and English at `/en/` plus
its three localized routes. Uzbek intentionally uses the canonical root rather
than a separate `/uz/` route. `/growth/`, `/robots.txt`, `/sitemap.xml`, and
`/schemas/store-metadata-v2.json` also returned HTTPS `200`; the schema parsed
as JSON with the expected canonical `$id`.

The macOS resolver API still retained an earlier negative cache during this
window, but both authoritative nameservers, Cloudflare and Google recursive DNS
checks from the activation capture, and a fresh Cloudflare DoH query returned
the public record set. The stale local cache does not invalidate the independent
public checks.

## Fail-closed activation gate — complete

The domain gate passed only after all of the following were independently
verified:

1. Active registrar record and `.uz` parent delegation.
2. Matching Cloudflare authoritative records and independent recursive DNS.
3. Matching apex/`www` certificate plus enabled HTTPS enforcement.
4. Redirect convergence, published route responses, canonical URLs, language
   declarations, and the public schema.

## DNS records serving after activation

All records are present and must remain DNS-only to preserve the verified
GitHub Pages host routing and certificate configuration:

| Type | Name | Target |
|---|---|---|
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| AAAA | `@` | `2606:50c0:8000::153` |
| AAAA | `@` | `2606:50c0:8001::153` |
| AAAA | `@` | `2606:50c0:8002::153` |
| AAAA | `@` | `2606:50c0:8003::153` |
| CNAME | `www` | `4810092.github.io` |

After all gates pass, return the heartbeat from hourly monitoring to its normal
daily schedule.
