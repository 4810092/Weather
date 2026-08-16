# Codex for Open Source application notes

Internal maintainer document. This is a dated, evidence-backed application worksheet—not public adoption marketing. Refresh all GitHub counts and store status immediately before submitting the [OpenAI Codex for Open Source form](https://openai.com/form/codex-for-oss/).

Snapshot date: 2026-08-16 (Asia/Tashkent). Repository metrics below were collected through GitHub CLI/API after merging OSS-readiness pull request #8 and three independently verified Dependabot updates. Dependabot opened those updates immediately after the OSS-readiness merge; all three passed the required Android/shared and iOS gates before merge.

## Repository

- URL: <https://github.com/4810092/Weather>
- Name: Nimbo (repository slug remains `Weather`)
- Visibility/default branch: public / `master`
- Created: 2026-08-09 17:04:15 UTC (seven calendar days old at this snapshot)
- License: Apache-2.0, detected by GitHub and present in `LICENSE`
- Description: “Production Kotlin Multiplatform weather app for Android and iOS — Compose Multiplatform, SQLDelight, offline-first data, and deterministic insights.”

## Maintainer

- Khasan Ganikhodjaev
- GitHub: [4810092](https://github.com/4810092)
- Role: creator and primary maintainer

That role is supported by the repository owner, the first commit, Git shortlog, and GitHub contributor data: the repository is owned by `4810092`; Khasan authored the initial commit and all 42 commits on the default branch at this snapshot; GitHub reports one contributor. “Creator and primary maintainer” is accurate. “Maintainer team” or external contributor claims would not be accurate.

## Verified repository signals

| Signal | Verified value at snapshot | Evidence/source |
| --- | --- | --- |
| Repository age | Created 2026-08-09 | GitHub repository API `createdAt` |
| Stars | 0 | GitHub repository API |
| Forks | 0 | GitHub repository API |
| Watchers | 0 | GitHub repository API |
| Contributors | 1 (`4810092`) | GitHub contributors API |
| Pull requests | 11 total and merged: 8 maintainer-authored PRs and 3 Dependabot PRs (#9-#11); 0 open | GitHub PR list, all states |
| Issues | 0 issues (PRs excluded) | GitHub issue list, all states |
| Tags | 3: one legacy checkpoint and two RC tags | GitHub tags API / Git refs |
| GitHub Releases | 2; both existing RC tags; both marked prerelease | GitHub releases API |
| Discussions | Enabled; 0 discussions at snapshot | GitHub repository/GraphQL API |
| CI | One active `CI` workflow; post-merge `master` run 31928556967 successful | GitHub Actions API |
| Recent activity | Default branch pushed 2026-08-16 | GitHub repository API |
| License | Apache-2.0 | GitHub license detection and repository file |
| Security features | Dependabot alerts/security updates, secret scanning, push protection, and private vulnerability reporting enabled | GitHub repository/security APIs |
| Dependency updates | Weekly Gradle and GitHub Actions Dependabot configuration in this readiness change | `.github/dependabot.yml` |

No download total, active-user count, testimonials, external adoption, or production performance aggregate was collected. Do not infer one. A stale public search result for the legacy Play listing is not adequate evidence for current adoption.

## Product and platform facts

- Real Kotlin Multiplatform application, not a library/framework.
- Shared Compose Multiplatform UI, state, resources, data, and domain code for Android and iOS.
- Android phone/tablet 1.0.2 (version code 6) is recorded as a completed Google Play production rollout on 2026-08-13.
- iOS/iPadOS 1.0 build 3 is recorded as an external TestFlight build, not a public App Store production release.
- Source includes Android home widget, WidgetKit, Wear OS, and watchOS companion surfaces.
- Offline-first SQLDelight source of truth, forecast snapshots, migrations, and a released-schema fixture test.
- Ktor/Open-Meteo provider integration with no client weather API secret.
- Deterministic insight engines; no LLM or remote inference in the product.
- 13 shipped languages, Arabic RTL, location-local time, adaptive layouts, and accessibility semantics.
- Pull-request CI builds Android/shared and unsigned iOS/watchOS targets.

The current release state is supported by [RELEASE_CANDIDATE.md](RELEASE_CANDIDATE.md), [RELEASE.md](RELEASE.md), Git history, build configuration, and CI. Store consoles remain the live authority; re-check them before describing current availability in an application.

## Ecosystem value

Nimbo’s strongest OSS case is not broad adoption; the repository is too young and the metrics do not support that claim. Its case is that it exposes a compact but unusually complete KMP application under real deployment constraints:

- shared Compose UI alongside thin native shells and companion surfaces;
- database-first offline behavior rather than direct network-to-UI sample code;
- explicit SQL and released-schema migration verification;
- explainable fixed-input insight logic and timezone/DST tests;
- a privacy boundary applied before persistence/network use;
- localization, RTL chronology, large-text, and accessibility decisions;
- store metadata, privacy declarations, upgrade evidence, CI, and release journals.

This can help KMP developers inspect trade-offs that minimal samples commonly omit. The project should be described as a production application/reference implementation, never as a widely adopted library or standard.

## Active maintenance evidence

- Eight merged maintainer-authored pull requests and three merged Dependabot updates between August 10 and the snapshot, with required CI on every PR and `master`.
- Two immutable RC tags now have accurately marked GitHub prerelease objects.
- Dated Android production, TestFlight, migration, QA, performance, provider, privacy, and store evidence.
- Real release-response history: RC2 fixed Play device exclusion caused by an implicit hardware requirement, then documented the upgrade gate.
- Reproducible repository, localization, store metadata, store asset, formatting, shared-test, migration, Android bundle, iOS, and watchOS gates.
- Contributor issue/PR forms, support/security routing, dependency updates, and explicit release/checkpoint documentation.

Limitations: all human maintenance and PR authorship is currently by one person; the only other PR author is Dependabot. There is no public issue-triage history because no issues have been opened, and the repository is only days old. These facts make the active-maintenance signal real but short-lived and internally concentrated.

## Readiness assessment

| Dimension | Rating | Reason |
| --- | --- | --- |
| Maintainer eligibility | **STRONG** | Repository owner, creator, sole contributor, release/operator responsibility. |
| Active-maintenance signal | **MODERATE** | Real PR, CI, store, QA, release, and security work, but only a short history and one maintainer. |
| Ecosystem-value signal | **MODERATE** | Substantive inspectable KMP application patterns; no evidence yet that the ecosystem is using them. |
| Adoption signal | **WEAK** | 0 stars, 0 forks, 0 watchers, one contributor, and no verified usage/download metric. |
| Overall application readiness | **MODERATE** | Technically credible and honestly documented, but adoption and project age are material weaknesses that repository polish cannot fix. |

## Current form mechanics

The current official form is <https://openai.com/form/codex-for-oss/>. It has one role radio selection rather than a free-text role description. API credits from the $1 million Codex Open Source Fund and conditional Codex Security access are requested in this same form; OpenAI does not publish a separate Fund form, an amount field, or a per-project maximum on the current official program page.

Select **Primary maintainer**, **Codex Security**, and **API credits for my project**. The Organization ID is account-specific and must not be committed here.

## Suggested form answers

Character counts include spaces and punctuation in the answer paragraph only. All answers are within the form’s 500-character limits where stated.

### Role selection

Primary maintainer

The current form does not accept a role paragraph. Keep the following counted text for a verification follow-up.

### Describe your role (supporting text) — 305 characters

I created Nimbo and am its primary maintainer. I own its Kotlin Multiplatform architecture, Android and iOS releases, CI, testing, security, localization, documentation, issue triage, and contributor workflow. I maintain the project end to end, from product architecture through store release engineering.

### Why does this repository qualify? — 450 characters

Nimbo is an inspectable Kotlin Multiplatform reference app built under real store constraints: Android 1.0.2 is in production, and the repository records iOS build 3 in external TestFlight. Its public source demonstrates shared Compose UI, offline-first SQLDelight persistence, deterministic logic, 13 locales and RTL, accessibility, schema migrations, privacy boundaries, CI, and cross-platform release engineering—trade-offs toy samples often omit.

### How will you use API credits? — 408 characters

I would use API credits for OSS maintenance: issue triage, PR review, regression-test generation, Android/iOS parity checks, localization validation, dependency and security analysis, documentation maintenance, and evidence-based release notes. Codex-assisted changes would remain reviewable through pull requests and the existing CI gates; OpenAI APIs would not be added to the Nimbo weather product itself.

### Anything else we should know? — 393 characters

Nimbo is a young open-source project and does not yet have broad adoption or external contributors. I am not claiming otherwise. Its value is as a reproducible, store-constrained KMP reference: the repository exposes architecture decisions, trade-offs, migrations, privacy and accessibility boundaries, CI, and cross-platform release engineering that simplified sample applications often omit.

## Refresh procedure before submission

Re-run the following read-only checks and update only facts that changed:

```sh
gh repo view 4810092/Weather \
  --json createdAt,updatedAt,pushedAt,stargazerCount,forkCount,watchers,licenseInfo
gh api repos/4810092/Weather/contributors --paginate
gh pr list -R 4810092/Weather --state all --limit 200
gh issue list -R 4810092/Weather --state all --limit 200
gh api repos/4810092/Weather/tags --paginate
gh api repos/4810092/Weather/releases --paginate
gh run list -R 4810092/Weather --limit 20
```

Then recalculate answer character counts and verify live store status. Do not create issues, discussions, releases, contributors, or usage claims merely to improve an application signal.
