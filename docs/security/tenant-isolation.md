# Tenant Isolation

## Isolation contract

Tenant isolation is a system invariant, not a UI convention. Every tenant-scoped request, message, row, index document, object key, cache entry, job, and audit record carries a validated `tenant_id`. Tenant context originates from authenticated identity or source credentials and MUST NOT be accepted from a conflicting client field.

## Controls by layer

| Layer | Required control |
|---|---|
| Edge | Bind credentials to tenant; reject ambiguous tenant selection |
| API | Typed tenant context; object lookup by `(tenant_id, id)` |
| Authorization | Membership and permission evaluated for active tenant |
| Relational store | Composite keys; row-level security as defense in depth |
| Search | Per-tenant alias or mandatory server filter; no raw client DSL |
| Event log | Tenant in signed envelope; ACL-separated producers/consumers |
| Object storage | Tenant-prefixed keys, scoped identities, encryption context |
| Cache | Tenant in key/invalidation channel; no globally cached auth decisions |
| Workers/jobs | Frozen tenant scope, least-privilege capability, runtime revalidation |
| Observability | Avoid payloads; use bounded internal tenant identifiers |

## Isolation tiers and noisy neighbors

The MVP uses shared infrastructure with logical isolation. Higher tiers may offer tenant-specific encryption keys, indexes, worker pools, or deployments. Moving tiers requires a documented migration and purge procedure.

Quotas cover ingest rate, bytes, query cost, concurrent exports, rules, detection CPU, notification attempts, and retained volume. Fair scheduling and reserved operator capacity stop one tenant exhausting the platform. Limits return explicit errors and never silently drop acknowledged data.

## Verification

- Generated tests exercise every repository/query method with mismatched tenants.
- Integration tests use at least two tenants and intentionally colliding IDs/names.
- Property tests verify no result contains a foreign `tenant_id`.
- Logs/traces verify tenant-context propagation without customer content.
- Production canaries execute synthetic cross-tenant denials.

Any confirmed cross-tenant disclosure or action is a security incident and release blocker.

