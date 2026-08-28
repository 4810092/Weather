# `nimbo.uz` launch state — 2026-08-28

Status: **origin deployed; public domain not yet reachable**.

## Completed

- GitHub Pages deployment run
  [`33195423653`](https://github.com/4810092/Weather/actions/runs/33195423653)
  completed successfully.
- The repository Pages configuration uses the workflow build type and accepts
  `nimbo.uz` as its custom domain.
- The generated site uses `https://nimbo.uz` as the canonical origin for the
  Uzbek, Russian, and English landing, privacy, support, and press routes.
- The registrar control panel contains the Cloudflare-assigned nameservers
  `jose.ns.cloudflare.com` and `sharon.ns.cloudflare.com`.
- The existing `nimbo-uz-rank-monitor` heartbeat temporarily runs hourly and
  performs read-only registry delegation, public DNS, Pages health, HTTP/TLS,
  and canonical checks alongside rank evaluation.

## Current external blocker

At `2026-08-28 23:35 +05:00`, public `NS`, `A`, and `AAAA` lookups returned no
records. An authoritative `dig +trace NS nimbo.uz` reached the `.uz` registry
and returned authenticated NSEC3 negative proof: the registry had not yet
published delegation for `nimbo.uz`. The registrar UI reported the domain as
`Activating`; Cloudflare therefore remained pending.

GitHub's Pages API also still returned HTTP `202` for domain health and
`https_enforced=false`. Those states are expected until DNS is visible and a
certificate can be issued. Public reachability and HTTPS are not claimed.

## DNS records required after activation

All records must remain DNS-only while GitHub verifies the domain and issues
TLS:

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

After propagation, the release check must enable Pages HTTPS, verify apex and
`www` redirects over HTTPS, verify every localized route, and then return the
heartbeat from hourly monitoring to its normal daily schedule.
