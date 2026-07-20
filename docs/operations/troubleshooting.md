# Development troubleshooting

## A service is unhealthy

Run `docker compose ps` and `docker compose logs --no-color <service>`. PostgreSQL and Redis must become healthy before the API starts; the web shell waits for API readiness. Health checks use bounded retries and do not guarantee functional correctness.

If port 8000 or 8080 is already in use, set `AEGISX_API_PORT` or `AEGISX_WEB_PORT` before starting Compose. Ports bind to loopback by default and should not be exposed to an untrusted network.

## PostgreSQL authentication fails

Changing `POSTGRES_PASSWORD` does not update credentials inside an existing initialized volume. For disposable synthetic development data, inspect the Compose project and explicitly remove its volumes, then restart. Never do this where the volume contains needed data.

## API startup fails after a schema change

Phase 1 currently creates tables at startup and has no migration framework. Preserve the failing logs and database volume for diagnosis. Do not delete state merely to make a test pass. Alembic migrations and compatibility checks are a production blocker.

## Python import or tool failures

Confirm the active interpreter is Python 3.12 and reinstall with `python -m pip install -e ".[dev]"`. Invoke tools through `python -m` so they use the active environment.

## Security audit cannot reach its advisory service

`pip-audit` may require network access and can fail in restricted environments. Record that check as not executed, retain the failure output, and run it in CI or an approved network environment. Never interpret a network failure as a clean audit.
