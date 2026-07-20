# Storage Strategy

## Persistence by workload

| Data | Primary need | Proposed class | Default retention |
|---|---|---|---|
| Tenants, memberships, config, alerts, jobs | Transactions/invariants | Relational database | Policy + audit needs |
| Accepted transport | Durable ordered replay | Replicated event log | Days, sized for recovery |
| Canonical events hot tier | Time/field search | Search/columnar store | 30 days |
| Canonical/raw cold tier | Low-cost replay/export | Encrypted object storage | 90 days; configurable |
| Audit events | Integrity and query | Dedicated ledger + archive | 1 year |
| Cache/rate limits | Ephemeral low latency | Distributed cache | Minutes/hours |
| Secrets | Rotation/access control | Managed secret service | Until revoked + metadata history |

These are technology classes, not vendor commitments.

## Partitioning, encryption, and keys

Tenant data uses `tenant_id` as the leading logical partition. High-volume events additionally partition by time and stable hash. Object keys use generated tenant prefixes and manifests; callers never construct arbitrary paths. Relational uniqueness and foreign keys include `tenant_id`.

TLS is mandatory. Managed encryption applies at rest with environment-separated keys. Higher tiers may use per-tenant data-encryption keys wrapped by managed KMS. Encryption context includes tenant and data class. Plaintext secrets and keys are never logged.

## Retention, deletion, and legal hold

Retention is policy-driven by data class and tenant within platform bounds. A deletion manifest tracks tombstone, hot-store purge, cold-object purge, index compaction, backup expiry, and verification. Legal hold is narrowly authorized and audited. Backups expire rather than being selectively mutated; restores reapply tombstones before service.

## Recovery and integrity

- Point-in-time recovery for metadata and versioned/immutable cold objects.
- Restore tests prove RPO/RTO.
- Checksums cover transport and stored objects; immutable versions protect rules/config.
- Reconciliation compares log offsets, event-store counts, and quarantine outcomes.
- Capacity alerts cover partitions, lag, indexes, objects, and quotas.

Phase 1 must benchmark representative writes/queries, isolation guarantees, cost, backup/restore, regional support, deletion behavior, and operational burden before vendor selection.

