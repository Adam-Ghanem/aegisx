# Domain Model

## Aggregate map

| Entity | Tenant-scoped | Key relationships and invariants |
|---|---:|---|
| Organization | No | Administrative tenant root; has status, region, plan, and policy defaults |
| Workspace | Yes | Mandatory security-data and authorization boundary within one organization |
| User | No | Human identity; service accounts are a distinct future principal type |
| Membership | Yes | Connects a user to an organization and scoped roles; may be time-bounded |
| Role / Permission | Role yes | Role grants fixed permissions; no implicit wildcard in MVP |
| DataSource | Yes | Owns credentials, schema profile, status, and rate limits |
| IngestionReceipt | Yes | Records batch/idempotency outcome and durable offset |
| CanonicalEvent | Yes | Immutable normalized observation; schema-versioned |
| Rule | Yes or managed | Stable identity with immutable RuleVersions |
| RuleVersion | Yes or managed | Expression, window, status, fixtures, and author |
| Finding | Yes | Rule evaluation result tied to event evidence |
| Alert | Yes | Workflow aggregate formed from one or more findings |
| Case | Yes | Optional investigation grouping alerts and notes |
| Integration | Yes | Destination with secret reference, never a raw secret |
| Delivery | Yes | Attempt history for a notification payload |
| AuditEvent | Yes/system | Append-only actor/action/resource/outcome record |
| Job | Yes | Export, deletion, replay, or bulk operation with frozen scope |

Phase 1 implements only Organization, Workspace, User, Membership, authorization entities, Session, RefreshToken, and AuditEntry. All security-data aggregates in this table are Phase 2 or later.

## Identity and lifecycle

Identifiers are opaque UUIDv7 or equivalent sortable, non-semantic values. `organization_id` and `workspace_id` are immutable. External identifiers live in typed namespaces and never replace internal IDs. Human display names are non-unique. Timestamps are UTC instants; durations use explicit units.

- Organization: `provisioning -> active -> suspended -> deleting -> deleted`.
- Workspace: `active -> suspended -> deleting -> deleted`.
- Data source: `pending -> active -> paused -> revoked`.
- Rule version: `draft -> validated -> staged -> active -> retired`; rollback activates a prior immutable version.
- Alert: `open -> acknowledged -> investigating -> resolved`; `closed_as_duplicate` is terminal.
- Job: `queued -> running -> succeeded|failed|cancelled`; execution revalidates authority.

## Invariants

1. A workspace-scoped relationship MUST join on resource ID, `organization_id`, and `workspace_id`.
2. Cross-tenant foreign keys are forbidden; managed global content is explicitly read-only.
3. Canonical events, rule versions, findings, and audit events are immutable.
4. Alert state changes use optimistic concurrency and preserve full history.
5. Deletion uses tombstones and a tracked purge workflow across every store.
6. Secrets are represented only by secret-manager references.
