# Contributing to Nimbo

Thank you for helping improve Nimbo as an application and as a Kotlin Multiplatform reference project. Focused fixes, tests, accessibility work, localization corrections, provider hardening, platform-parity improvements, and documentation are welcome.

## Before you start

- Read the [architecture overview](docs/ARCHITECTURE.md) and the relevant ADR before changing a boundary.
- Check [existing issues](https://github.com/4810092/Weather/issues) and [discussions](https://github.com/4810092/Weather/discussions). A prior issue is not required for a small, self-contained fix.
- Discuss changes that alter providers, privacy behavior, persistence schema, product scope, app identifiers, or platform support before implementing them.
- Keep one pull request focused on one coherent outcome.

## Development workflow

1. Fork or branch from the current default branch.
2. Follow [Development](docs/DEVELOPMENT.md) to build the affected platform.
3. Add or update deterministic tests where behavior changes.
4. Run the proportionate checks in [Testing](docs/TESTING.md).
5. Update docs when architecture, privacy, provider terms, localization behavior, or release requirements change.
6. Open a pull request that explains the reason, affected platforms, test evidence, and screenshots for visible UI changes.

CI builds Android/shared code on Linux and the unsigned iOS/watchOS targets on macOS. Maintainer signing keys are never required for a contributor PR.

## Design and architecture expectations

- Keep provider DTOs and database rows out of UI state.
- Keep normalized domain values in SI units; convert and format at presentation boundaries.
- Preserve the database-backed UI source-of-truth model unless an accepted ADR changes it.
- Keep insight outputs deterministic and semantic; localization belongs in presentation code.
- Explain intentional Android/iOS differences instead of forcing parity where platform conventions differ.
- Do not change production application or bundle identifiers.

These are current project constraints, not claims that every KMP application should use the same design.

## Tests and fixtures

Use fixed clocks/data where practical. Network tests use Ktor’s mock engine; do not make live provider calls in unit tests. Database fixtures must be generated or deliberately sanitized and must contain no user identity or precise location history.

When changing the SQLDelight schema:

1. add a numbered migration;
2. update the versioned schema snapshot;
3. extend migration coverage for the previously released schema;
4. run `:shared:verifySqlDelightMigration` and `:shared:testAndroidHostTest`.

## Localization and accessibility

English Compose resources are canonical, and every shipped locale is required. Preserve resource types and positional placeholders, avoid concatenating translated sentence fragments, and run `python3 scripts/check_localizations.py`. See [Localization](docs/LOCALIZATION.md) for the complete locale and RTL contract.

For UI changes, check large text, light/dark appearance, narrow and expanded widths, and screen-reader semantics. Preserve the explicitly left-to-right chronological timeline inside RTL layouts unless the product decision and tests are intentionally revised.

## Privacy and security

Do not commit API keys, passwords, tokens, signing files, provisioning profiles, credentials, production databases, precise coordinates, or store-export artifacts. Use synthetic or sanitized fixtures. Review [Privacy](docs/PRIVACY.md), [Providers](docs/PROVIDERS.md), and [Security](SECURITY.md) when data flow or dependencies change.

Report vulnerabilities privately rather than in an issue or pull request.

## Commit and pull-request scope

Readable, imperative commit messages are preferred. A pull request may contain multiple commits when they help review; maintainers may squash at merge. PRs should state:

- what changed and why;
- affected platforms;
- tests and manual checks performed;
- before/after screenshots for visible UI work;
- privacy, security, provider, migration, or release implications.

By contributing, you agree that your contribution is licensed under Apache-2.0 and that you will follow the [Code of Conduct](CODE_OF_CONDUCT.md).
