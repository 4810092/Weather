# Nimbo weekly growth review — 2026-08-30

Report as of: `2026-08-30` (`Asia/Tashkent`)
KPI evidence period: `2026-08-24 through 2026-08-30`
Evaluation artifact: `evaluation_weekly_report.json`
Weekly evidence: `weekly-2026-08-30.json` — ACCEPTED
Current rank evidence: `public_rank_weekly_report.json` — ACCEPTED
Rank comparison observation dates: `2026-08-23, 2026-08-30`
Goal evidence completeness: `complete`

## Executive summary

**HOLD.** At least one critical scale gate is failed.

The simultaneous Top-10 goal is not achieved: the current verified streak is **0 / 7 complete days**. Paid spend is **not authorized**; external action is **not authorized**.

## KPI status

| Metric | Apple | Google | Target | Evidence / caveat |
| --- | --- | --- | --- | --- |
| Conversion / listing CTR | 14% — FAIL; denominator 600 / minimum 500 | 40% — PASS; 240 / 600; denominator 600 / minimum 500 | Apple >= 15%; Google >= 35% | Conversion status is valid only after its recorded minimum denominator. |
| First launch / install | 85% — PASS; 85 / 100 | 90% — PASS; 90 / 100 | >= 80% | Exact numerator / denominator is shown only from the referenced weekly import. |
| D7 retention | 25% — PASS; 25 / 100 | 25% — PASS; 25 / 100 | >= 20% | Exact numerator / denominator is shown only from the referenced weekly import. |
| DAU / MAU | 30% — PASS; 30 / 100 | 25% — PASS; 25 / 100 | >= 20% | Exact numerator / denominator is shown only from the referenced weekly import. |
| Ratings | 25 ratings — PASS; 4.7 / 5 — PASS | 30 ratings — PASS; 4.8 / 5 — PASS | count >= 25; average >= 4.6 / 5 | Point-in-time storefront values; not additive across breakdowns. |

## Rank and search

| Surface | Current | Comparison observation | Change | Complete? |
| --- | ---: | ---: | ---: | --- |
| Apple UZ Top Free Weather | #9 | #15 (2026-08-23) | 6 | PASS |
| Google UZ Weather, `uz-UZ` | #8 | #14 (2026-08-23) | 6 | PASS |
| Google UZ Weather, `ru-UZ` | #12 | #18 (2026-08-23) | 6 | FAIL |
| Google UZ Weather, `en-UZ` | >30 | Unknown | Unknown | FAIL |
| Generic-query diagnostic | 1 (weather) | Unknown | Unknown | Diagnostic: FAIL |

Current verified Top-10 streak: **0 / 7 complete days**.

Rank comparisons include only exact numeric observations under the current monitor configuration. Bounded absences are not converted into synthetic ranks.

## Scale gates

| Gate | Actual | Evaluation | Required | Evidence / required action |
| --- | --- | --- | --- | --- |
| iOS crash gate | pass | PASS | pass | Current crash evidence is reviewed. Required action: Maintain dated evidence and recheck at the next cutoff. |
| Open-Meteo promotion clearance | pending | FAIL | pass | Written provider clearance is not yet recorded. Required action: Obtain written Open-Meteo promotion clearance; keep promotion paused until the reply is recorded. |
| Release artifact / source sync | pass | PASS | pass | Source-current signed artifacts and hashes are recorded. Required action: Maintain dated evidence and recheck at the next cutoff. |
| Android runtime smoke (legacy ID) | pass | PASS | pass | The required Android physical matrix passed. Required action: Maintain dated evidence and recheck at the next cutoff. |
| Apple runtime smoke (legacy ID) | pass | PASS | pass | The required Apple physical matrix passed. Required action: Maintain dated evidence and recheck at the next cutoff. |
| nimbo.uz activation | blocked | FAIL | pass | Public delegation and HTTPS are not verified. Required action: Verify a matching nimbo.uz/www certificate, HTTPS redirects, canonicals, and localized routes before using the domain in store or outreach surfaces. |
| Store policy console clearance | pass | PASS | pass | Both store consoles report no open policy action. Required action: Maintain dated evidence and recheck at the next cutoff. |

## Quality guardrails

| Guardrail | Actual | Requirement | Status | Evidence policy |
| --- | ---: | ---: | --- | --- |
| iOS crash-free sessions | 99.9% | >= 99.8% | PASS | block_scale |
| Android user-perceived crash rate | 0.3% | < 1.09% | PASS | block_scale |
| Android user-perceived ANR rate | 0.1% | < 0.47% | PASS | block_scale |
| Android phone-model crash rate | 1% | < 8% | PASS | review_required |
| Android phone-model ANR rate | 1% | < 8% | PASS | review_required |
| Wear model crash rate | 1% | < 4% | PASS | review_required |
| Wear model ANR rate | 1% | < 5% | PASS | review_required |
| User loss rate | Unknown | < 5% | UNKNOWN | report_unknown |
| Open policy issues | 0, 0 | == 0 | PASS | block_scale |

## Unknown or missing evidence

- Unknown quality guardrails: User loss rate.
- Rank evidence is incomplete for the goal: Google UZ Weather category is not top 10 in all fixed profiles.

## Next actions

| Priority | Action | Suggested owner | Suggested due |
| ---: | --- | --- | --- |
| 1 | Obtain written Open-Meteo promotion clearance; keep promotion paused until the reply is recorded. | Product / legal | 2026-09-06 |
| 2 | Verify a matching nimbo.uz/www certificate, HTTPS redirects, canonicals, and localized routes before using the domain in store or outreach surfaces. | Web operations | 2026-09-06 |
| 3 | Capture the next complete public-rank snapshot and rerun the evaluation without changing the monitor configuration. | Growth operations | 2026-08-31 |

Suggested owners and due dates are operating recommendations calculated from the report date, not recorded commitments.

## Operating boundary

This review does not send outreach, publish store changes, authorize spend, switch provider infrastructure, or claim a release or rank outcome that is not present in the supplied evidence.
