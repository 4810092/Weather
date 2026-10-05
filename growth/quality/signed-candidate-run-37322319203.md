# Signed candidate 13 — October 5, 2026

Status: **PASS for protected signing and independent local full-byte verification**.

Product source: `44d3f7862b61ef95bf2b686820cfba3fc05a7b25`. Workflow head: `9dcc498e641923fc03d4631b516c5141720dc5a9`.
[Protected signing run 37322319203](https://github.com/4810092/Weather/actions/runs/37322319203), attempt 1, succeeded for phone13, Wear1000013 and Apple app/widget/watch13, version1.1.0.

| Artifact | SHA-256 |
| --- | --- |
| android_phone | `a7f4f6b9d749be34a7e27a6f0040ddc1261c5114ad08ed1790283e53b6df54eb` |
| apple | `9538a70063988eed24aa4a739e3cff01ad8c0387d3383c5f88d5daaaf12be99e` |
| wear_os | `c9b79accdb4dcca8968e5e2a94759a0de67a8fc3882750cc25896512c2c662e4` |

Authenticated Actions artifact11351568516 matched ZIP SHA-256 `c74a1ce3095c7c2e34352353b3515b599ed90e5954413acd776dd70882a8fbfd`. The exact two-file ZIP inventory, run/head/repository identity, receipt provenance and safe package extraction were checked locally. Package SHA-256 `cd9ca82d66dd5c59ab10504ac1f620636289c319a64cdbfd3b53dfea613b99e8` and canonical tree `84404972b8116b259cda684d9dc4936eb961a1aa3d47d556a7bbf352edeaf15e` matched.

The [signer receipt](receipts/signed-candidate-37322319203.json) records original hosted provenance. An independent local execution of `scripts/verify_signed_candidate.py` exited0; the [local verification record](receipts/release13-local-reverification-2026-10-05.json) explicitly identifies local execution. All three digests matched the signer receipt. Checks include Android package/version/source/upload certificate/mapping; Apple distribution signature, profiles, entitlements/App Groups, version/source, archive/export parity, dSYMs and watch topology. The reviewed workflow/verifier digests also matched.

This evidence proves signing and source/byte verification only. Runtime gaps from the [current acceptance record](release13-runtime-acceptance-2026-10-05.md) remain open; no delivery, review, rollout or public availability is claimed here. One-off build12 materialization/verification workflows were not reused.
