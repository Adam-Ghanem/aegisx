# Contributing to AegisX

Work on a dedicated branch and keep changes scoped to one reviewable milestone. Never commit secrets, `.env`, local databases, caches, generated telemetry, or build output.

Before opening a pull request:

1. Rebase or merge the latest target branch without rewriting published history.
2. Run `make validate` on Linux/macOS or `.\scripts\dev.ps1 validate` on Windows.
3. Review `git status` and the full diff.
4. Confirm documentation describes actual behavior and that no test result is claimed without execution.
5. Use a conventional commit such as `feat(ingest): enforce idempotent receipts`.

Security and tenant isolation regressions are release blockers. Authorization is deny-by-default, and every tenant-owned query must be tested with two tenants and colliding identifiers. Use deterministic synthetic data only.

Dependencies require a clear purpose, an exact version, an appropriate license, and successful audit checks. Do not add a package when the standard library or an existing dependency is sufficient.

Pull requests should state the threat boundary affected, tests executed, operational impact, migration or rollback considerations, and known risks. Do not merge directly to `main` or bypass required CI checks.
