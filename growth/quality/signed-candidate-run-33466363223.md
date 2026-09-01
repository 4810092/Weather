# Replacement signed-candidate run 33466363223

Status: **FAILED CLOSED — no signed candidate artifact retained**  
Observed: 2026-09-01 08:28–08:53 Asia/Tashkent  
Workflow head: `a3ed7d915b96526e96823dd610f3e2ee43b7dcf8`  
Product source authority: `ba824beae5e72653e42af2b8b78286f61415e3ab`

## What passed

- Exact `master` CI run `33465021222` passed all five jobs before signing was
  dispatched.
- The protected unsigned job sealed the exact product source and built phone
  `1.1.0 (9)`, Wear OS `1.1.0 (1000009)`, and the Apple archive for
  `1.1.0 (7)`.
- In the protected `release-signing` environment, Android upload signing,
  Apple identity/profile installation, and Apple App Store export all passed.
- Ephemeral signing material was destroyed before independent byte
  verification, and the final cleanup step also passed.

## Fail-closed result

The independent verifier rejected the retained Apple archive because its
top-level `ApplicationProperties.CFBundleVersion` was `6` while the candidate
manifest required `7`. The workflow upload step was skipped, so there is no
signed-candidate package or receipt from this run and nothing may be promoted
or uploaded from it.

The inert unsigned handoff remains available as Actions artifact `9785435177`
(`nimbo-unsigned-inputs-ba824beae5e72653e42af2b8b78286f61415e3ab`, API
digest `sha256:d1f44eaac6833bd89e2c98dbd297c7d3912ecb2138cc15cc052b359637d4607c`).
A read-only local download verified its inner tar SHA-256 as
`a41d450415f81bb252eab9ab9a82a3fa18a26a8550498bea65e69597d901b884`.
Safe extraction found build `7` and source revision `ba824be…` in the app,
widget, and watch Info plists and build `7` in the unsigned archive metadata.

## Root cause and correction

The export step had a historical literal that rewrote the retained archive
metadata to build `6` after a successful build-7 export. The correction copies
both version and build from the exported app Info plist into the retained
archive metadata. The signed-candidate workflow remains hash-pinned by
`scripts/signed_candidate_workflow_security.py`; no verifier, signing input,
profile, entitlement, or product source was weakened or changed.

This record proves a protected fail-closed rejection and its diagnosed cause.
It does not prove signed bytes, store delivery, submission, review, rollout,
public availability, physical QA, or rank.
