# Data Flow

## Ingestion and detection

1. A data source sends a TLS request with source credential, idempotency key, and bounded batch.
2. The gateway applies size/rate limits; ingestion derives tenant context from the authenticated credential.
3. The service validates the envelope, stamps receipt metadata, and appends accepted records to the durable log before acknowledging.
4. Normalizers validate the source profile, map fields to the canonical schema, and quarantine malformed records without blocking valid siblings.
5. Enrichment uses bounded internal datasets; external lookups are asynchronous, allowlisted, cached, and treated as untrusted.
6. Canonical events are written idempotently to hot search storage and durable object storage as policy requires.
7. Detection workers load a signed rule-version snapshot for the same tenant, evaluate events, and emit deterministic findings.
8. The alert service groups findings using a documented fingerprint, stores evidence references, and emits notification intents.
9. Notification workers resolve destination secrets, apply egress policy, sign payloads, retry with jitter, and dead-letter exhausted deliveries.

## Query and configuration

The API authenticates the principal, resolves active tenant membership, authorizes the action/resource, and issues a query with a server-injected tenant predicate. Results are redacted according to field permissions. Evidence access and exports are separately audited.

Rule/configuration changes are validated, versioned, and committed transactionally with an audit event. Workers receive immutable snapshots through a configuration stream and reject invalid tenant, signature, or version metadata.

## Deletion and export

Requests freeze an authorized scope and create a job. Workers re-authorize system capability, enumerate objects using tenant-prefixed manifests, and record completion per store. Exports use short-lived, single-tenant encrypted objects and expiring grants. Deletion emits tombstones first, prevents rehydration during replay, and verifies eventual purge.

## Delivery semantics

- Accepted input: at least once, with deterministic `event_id` and deduplication.
- Internal processing: at least once; every consumer is idempotent.
- Alert creation: effectively once per `(tenant_id, rule_version_id, fingerprint, window)`.
- Notification: at least once; payload carries a stable delivery ID.
- Ordering: guaranteed only within a documented partition; event time and ingest time are distinct.

