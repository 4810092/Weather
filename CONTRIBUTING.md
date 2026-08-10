# Contributing

Thank you for helping improve Nimbo. Keep changes focused, explain user-visible behavior, and include tests for domain, persistence, or localization changes.

## Development workflow

1. Create a branch from the current default branch.
2. Make the smallest coherent change.
3. Run the commands in the README production-gates section.
4. Update documentation when behavior, architecture, privacy, providers, or release requirements change.
5. Open a pull request with the affected platforms and QA evidence.

Do not commit API keys, signing files, provisioning profiles, credentials, production databases, or store-export artifacts. Use synthetic or deliberately sanitized fixtures. The checked-in v1 migration database contains only generated weather/location test data and no user identity.

## Localization

English is canonical, but every production locale is required. A pull request that adds or changes a canonical resource must update all locale overlays and preserve placeholder/resource types. Do not construct sentences by concatenating translated fragments. Run `python3 scripts/check_localizations.py` before submitting and see `docs/LOCALIZATION.md` for RTL and chronological-axis rules.

By contributing, you agree that your contribution is licensed under Apache-2.0 and that you will follow the Code of Conduct.
