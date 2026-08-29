# `nimbo.uz` launch state — 2026-08-28, refreshed 2026-08-29

Status: **BLOCKED — registrar activation is incomplete; public domain and TLS
are not available**.

## Completed

- GitHub Pages deployment `6147270106` for commit
  `584f47a83637ce3587ce980a69f392b84a57656b` completed successfully.
- GitHub Pages workflow run `33213699930` for the current commit
  `53d4801d5d2012b300bb44959f08c32afe705045` also completed successfully.
- The repository Pages configuration uses the workflow build type and accepts
  `nimbo.uz` as its custom domain.
- The generated site uses `https://nimbo.uz` as the canonical origin for the
  Uzbek, Russian, and English landing, privacy, support, and press routes.
- The registrar-facing record contains the Cloudflare-assigned nameservers
  `jose.ns.cloudflare.com` and `sharon.ns.cloudflare.com`; this is not proof of
  registry delegation.
- The Cloudflare zone now contains the complete DNS-only GitHub Pages record
  set: four `A`, four `AAAA`, and the `www` `CNAME`. These records are staged
  but cannot answer publicly until the `.uz` registry publishes delegation.
- A direct HTTP request to the GitHub Pages edge with `Host: nimbo.uz` returned
  HTTP `200` with the expected site. This proves that the Pages origin can route
  the custom host, but it does not prove public DNS or HTTPS reachability.
- The existing `nimbo-uz-rank-monitor` heartbeat temporarily runs hourly and
  performs read-only registry delegation, public DNS, Pages health, HTTP/TLS,
  and canonical checks alongside rank evaluation.

## Current external blocker

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

Registry lookup, direct queries to authoritative `.uz` nameservers, and public
recursive resolver checks all returned DNSSEC-authenticated `NXDOMAIN` for
`nimbo.uz`. The registry has therefore not published a delegation. The
nameservers shown in the registrar-facing record are not publicly effective,
and this is not an ordinary Cloudflare propagation delay.

TLS for `nimbo.uz` is not provisioned. The successful GitHub Pages deployment
and direct edge-host HTTP `200` are origin-only evidence; public reachability
and HTTPS remain unclaimed.

## Fail-closed activation gate

Do not announce or promote `nimbo.uz` as live until all of the following are
complete and independently verified:

1. Complete the registrar activation flow, including any outstanding payment
   or identity/contact verification required by Webname/Arsenal-D.
2. Confirm that WHOIS no longer reports `EXPIRED` or waiting for activation and
   that the `.uz` registry publishes delegation to the intended Cloudflare
   nameservers.
3. Verify the staged Cloudflare DNS records below after delegation, then confirm
   public `NS`, `A`, `AAAA`, and `www` resolution from independent recursive
   resolvers.
4. Wait for GitHub Pages certificate issuance, enable HTTPS, and verify the
   apex, `www`, redirects, canonical URLs, and every localized route over TLS.

## DNS records staged before activation

All records are present and must remain DNS-only while GitHub verifies the
domain and issues TLS:

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
