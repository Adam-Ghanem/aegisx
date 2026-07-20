# AegisX development

## Prerequisites

- Python 3.12 (CI uses 3.12.11)
- Git
- Docker Engine with Docker Compose v2 for the production-like local stack
- GNU Make on Linux/macOS, or PowerShell 7 on Windows

Do not place credentials in the repository. Copy `.env.example` to `.env` only for local overrides; `.env` is ignored. The Compose password default is intentionally local-only and must never be used outside a developer workstation.

## Local Python workflow

Create and activate an isolated environment, then install the project.

Linux/macOS:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
make setup
make validate
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
.\scripts\dev.ps1 setup
.\scripts\dev.ps1 validate
```

Unit tests use SQLite for speed. The Compose smoke path exercises PostgreSQL migrations and Redis readiness. Redis is non-authoritative and currently participates only in readiness; rate limiting and short-lived session state remain follow-up work.

## Container workflow

Start PostgreSQL, Redis, the API, and the explicit web shell:

```sh
make start
```

```powershell
.\scripts\dev.ps1 start
```

The API listens only on `127.0.0.1:8000`; readiness is at `http://127.0.0.1:8000/health/ready`. The web shell listens on `127.0.0.1:8080`. Override ports with `AEGISX_API_PORT` and `AEGISX_WEB_PORT`.

View logs with `make logs` or `.\scripts\dev.ps1 logs`. Stop without deleting data with `make stop` or `.\scripts\dev.ps1 stop`.

Removing volumes deletes the local development database and Redis state. This is intentionally not wrapped in a task; inspect the target project first, then run `docker compose down --volumes` only when that deletion is intended.

## Quality commands

| Purpose | Linux/macOS | Windows PowerShell |
|---|---|---|
| Tests | `make test` | `.\scripts\dev.ps1 test` |
| Lint | `make lint` | `.\scripts\dev.ps1 lint` |
| Format | `make format` | `.\scripts\dev.ps1 format` |
| Type check | `make typecheck` | `.\scripts\dev.ps1 typecheck` |
| Security checks | `make security` | `.\scripts\dev.ps1 security` |
| Package/container build | `make build` | `.\scripts\dev.ps1 build` |

CI is configured with least-privilege repository access, runs tests and static checks, validates Compose, builds all images, and waits for health checks. CI action tags are version-pinned but not yet immutable commit-SHA pinned; this supply-chain gap must be closed before a production release.

## Current Phase 1 boundaries

- The web service is an accessible React application shell; operational SOC pages remain disabled until their APIs exist in later phases.
- Redis is health-checked but is not yet used for rate limiting or session state.
- The API container applies the versioned Alembic migration before starting. Production deployments require a separately controlled migration job rather than every replica migrating.
- Local Compose uses tag-pinned images, not digest-pinned images. Validate and pin digests in the release environment.
- Frontend dependencies have a lockfile. Python versions are exactly constrained but a transitive Python lockfile remains to be added.
