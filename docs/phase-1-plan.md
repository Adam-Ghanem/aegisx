# Phase 1 Plan: Secure Control-Plane Foundation

## Outcome

Phase 1 delivers a deployable modular-monolith foundation for first-party authentication, organization and workspace tenancy, deny-by-default authorization, and append-oriented audit. It does **not** implement telemetry ingestion, normalization, detections, alerts, incidents, search, automation, or analyst dashboards. Those capabilities begin in Phase 2 only after the security boundary is verified.

## Bounded scope

### Included

- Python/FastAPI API and worker entry points in a monorepo.
- PostgreSQL as the transactional system of record and migration target.
- Redis for bounded, non-authoritative rate-limit and short-lived revocation state.
- Organization, Workspace, User, Membership, Role, Permission, RolePermission, MembershipRole, Session, RefreshToken, and AuditEntry models.
- First-party email/password authentication: login, refresh rotation, logout/revocation, generic failures, password hashing, and authentication rate limiting.
- Password-reset and email-verification interfaces with a local non-delivery adapter. Public completion flows and real email delivery are deferred unless separately accepted.
- Backend authorization policies, workspace selection, resource ownership checks, request/correlation IDs, structured logging, and health endpoints.
- Deterministic bootstrap data for tests and local development only.

### Explicitly deferred to Phase 2

- DataSource and API-key ingestion authentication.
- Raw or canonical events, adapters, queues, outbox processing, quarantine, and event search.
- Detection rules, findings, alerts, alert transitions, incidents, correlation, and risk scoring.
- Threat intelligence, assets, security-observable identities, vulnerabilities, playbooks, reports, exports, and AI assistance.
- Redis-backed job queues, ClickHouse, object storage, brokers, Kubernetes, and production email providers.
- The full web SOC application. Any minimal authentication shell must not imply deferred capabilities exist.

## Ubiquitous language

- **Organization** is the commercial and administrative tenant root.
- **Workspace** is the mandatory data and authorization boundary beneath an organization. Every future security-domain resource belongs to exactly one workspace and therefore one organization.
- **User** is a human identity. A future **ServiceAccount** is a non-human identity and is not modeled as a user.
- **Membership** grants a user access to one organization. Workspace access is explicit or derives from a documented organization-wide administrative role.
- `organization_id` and `workspace_id` are immutable ownership fields. Client-supplied ownership never overrides authenticated context.
- “Tenant” is an architectural adjective for isolation, not a persisted entity name.

## Milestones

### M1.1 — Repository and runtime foundation

Deliver project layout, locked dependencies, settings validation, API lifecycle, safe structured logging, request/correlation IDs, health endpoints, PostgreSQL migrations, and local Redis/PostgreSQL configuration.

Exit: clean setup from documentation; migration upgrade succeeds on PostgreSQL; invalid or secret-bearing configuration fails safely; quality and security checks are runnable.

### M1.2 — Organization/workspace domain and isolation

Deliver Organization, Workspace, User, Membership, roles, and granular permissions with tenant-aware repository methods and deny-by-default policy evaluation.

Exit: two-organization tests with colliding identifiers prove no cross-organization or cross-workspace read/write; every protected endpoint checks backend policy; critical policy branches have complete coverage.

### M1.3 — First-party authentication

Deliver password hashing, login, short-lived access tokens, opaque rotating refresh tokens stored only as hashes, session metadata, logout/revocation, generic authentication errors, and rate limits. Define reset and verification interfaces without claiming external delivery.

Exit: refresh replay revokes the token family; logout prevents refresh reuse; suspended users, organizations, and memberships are denied; tokens contain identifiers but no secrets or permission snapshots; credentials and raw tokens never enter logs or audit metadata.

### M1.4 — Audit and operational hardening

Deliver append-oriented audit recording for authentication and privileged state changes, safe audit querying, metrics, graceful shutdown, CI checks, threat-model updates, runbooks, and a production-readiness review.

Exit: required actions create audit entries atomically where possible; denied privileged actions and authentication outcomes are represented without credential leakage; dependency, secret, static, test, migration, and configuration checks pass or blockers are recorded.

## API boundary

Initial public contracts are limited to `/v1/auth/login`, `/v1/auth/refresh`, `/v1/auth/logout`, `/v1/auth/me`, authorized organization/workspace reads needed for context selection, and health endpoints. Administrative mutation APIs are added only with complete policy and audit coverage. There are no `/events`, `/detections`, `/alerts`, or `/incidents` endpoints in Phase 1.

## Cross-cutting invariants

1. Authorization denies unless an explicit policy permits the action.
2. Organization and workspace context derives from authenticated state and validated membership, never an arbitrary request field.
3. Workspace-owned relations and queries constrain both `organization_id` and `workspace_id`; identifiers alone are insufficient.
4. PostgreSQL is authoritative. Redis loss may reduce availability or invalidate sessions conservatively, but must never grant access or lose durable business state.
5. Refresh rotation is transactional and single-use; replay is detectable and revokes the family.
6. Passwords use a memory-hard password hash. Tokens, passwords, reset secrets, and signing keys are never persisted or logged in plaintext.
7. Audit metadata uses an allowlist and excludes credentials, tokens, and sensitive bodies.
8. All timestamps are UTC and identifiers are opaque and non-semantic.

## Acceptance suite

- Domain and repository tests cover active, suspended, revoked, expired, and wrong-boundary cases.
- An authorization matrix covers every Phase 1 endpoint and role; no route relies on frontend visibility.
- Isolation tests use two organizations, multiple workspaces, and colliding human-readable identifiers.
- Authentication tests cover enumeration resistance, rate limits, refresh races, replay, revocation, expiry, malformed tokens, and key/version rejection.
- Audit tests prove required event creation and prohibited-field redaction.
- Migration tests execute against PostgreSQL, including upgrade from an empty database.
- API contracts and generated OpenAPI match implemented routes.
- Logs and traces include request/correlation IDs without raw credentials or customer content.
- Documentation names deferred capabilities honestly and includes reproducible commands.

## Assumptions and risks

- Phase 1 uses shared infrastructure with logical isolation; dedicated deployments and per-organization keys are later tiers.
- A user may belong to multiple organizations. A request operates in exactly one selected workspace.
- First-party authentication increases credential-handling and recovery risk; federation and MFA remain required extension points.
- Redis rate limiting is defense in depth; edge limits are still required in production.
- PostgreSQL row-level security is defense in depth, not a substitute for scoped repositories and policy checks.
- Deferring the event pipeline delays validation of throughput and durable-before-ack claims; Phase 2 must benchmark before SLO commitments.

## Unresolved questions

- Whether ordinary organization membership grants all workspaces or needs WorkspaceMembership. Default: explicit workspace access, with organization owners as the only documented inheritance.
- Exact access-token signing and key-rotation mechanism for the first deployment environment.
- Whether public password-reset and email-verification completion belong in Phase 1 or the first Phase 2 increment.
- Required two-person approval boundaries for organization ownership and role changes.

