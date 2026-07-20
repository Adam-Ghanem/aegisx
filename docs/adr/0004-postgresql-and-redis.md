# ADR 0004: PostgreSQL System of Record and Redis Ephemeral State

- Status: Accepted
- Date: 2026-07-20

## Context

Phase 1 needs transactional identity, tenancy, policy, session, and audit state plus bounded shared rate-limit and revocation coordination. It does not need an analytics store.

## Decision

Use PostgreSQL as the authoritative Phase 1 database through SQLAlchemy and Alembic. Use composite ownership constraints and optionally row-level security as defense in depth. Use Redis only for non-authoritative, expiring state such as distributed rate-limit counters and short-lived revocation/cache acceleration.

Security decisions fail closed when Redis state is unavailable or uncertain. Durable sessions, refresh-token families, memberships, roles, and audit entries remain in PostgreSQL.

## Consequences

Integration and migration tests run against PostgreSQL; SQLite is not an isolation substitute. Redis flushes cannot grant authorization. Operations require pooling, timeouts, health semantics, PostgreSQL backups, and bounded Redis keys and TTLs.

