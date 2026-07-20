# System Architecture

## Architectural style

AegisX begins as a modular service architecture with independently scalable data-plane workers. The control plane handles identity, tenants, configuration, rules, alerts, and audit queries. The data plane handles high-volume ingestion, normalization, enrichment, detection, and notification. A durable event log separates acceptance from processing.

Phase 1 is a modular monolith implementing only authentication, Organization/Workspace authorization, and the audit control-plane foundation. The data-plane components below are target architecture for Phase 2 and later, not implemented Phase 1 services.

## Logical components

| Component | Responsibility | Trust level |
|---|---|---|
| Edge/API gateway | TLS termination, request limits, routing, request identity | Internet-facing |
| Identity adapter | Validate IdP tokens; map subjects to memberships | Security-critical |
| Control API | Tenant config, rules, alerts, cases, audit, jobs | Tenant-authorized |
| Ingestion API | Authenticate source, validate envelope, assign receipt | Hostile-input boundary |
| Durable event log | Partitioned accepted-event transport and replay | Internal data plane |
| Normalizer/enricher | Produce canonical events and bounded enrichment | Hostile-data processor |
| Detection workers | Evaluate versioned rules; emit findings | Isolated compute |
| Alert service | Correlate/deduplicate findings and manage workflow | Control plane |
| Notification workers | Signed webhooks and integration delivery | Egress boundary |
| Query service | Authorized search over tenant event indexes | Read boundary |
| Metadata database | Transactional configuration and workflow state | System of record |
| Event store/index | Canonical event retention and search | High-volume data |
| Object store | Cold data, exports, replay artifacts | Bulk data |
| Audit ledger | Append-only security and administrative actions | Restricted |

## Core boundaries

```text
Users / Sources
      |
  Edge Gateway
      |
+-----+---------------- Control Plane ------------------+
| Identity -> Control API -> Metadata DB / Audit Ledger |
+-------------------------------------------------------+
      |
+--------------------- Data Plane ----------------------+
| Ingest -> Durable Log -> Normalize -> Detect -> Alert |
|                         |             |         |      |
|                      Event Store -----+      Notify --> external integrations
+-------------------------------------------------------+
```

## Design principles

- Deny by default; tenant context is validated, never inferred from user input alone.
- Acknowledgement occurs only after durable acceptance.
- At-least-once delivery is expected; consumers and writes are idempotent.
- Partitioning uses `tenant_id` plus a stable key to retain tenant locality without hot partitions.
- Control-plane failure MUST NOT corrupt accepted events; data-plane backlog applies backpressure.
- External calls occur only through allowlisted egress workers with timeouts, size limits, and SSRF defenses.
- Configuration is immutable by version and promoted through explicit states.

## Deployment and failure domains

Initial production should use at least three availability zones where supported. Stateless APIs scale horizontally. Queue, metadata, and object storage use managed replicated services. Detection workers are separated from internet-facing services and receive no general credentials. Per-tenant quotas and circuit breakers prevent a noisy tenant or destination from exhausting shared capacity.

## Deferred decisions

Phase 1 decisions for the modular monolith, tenancy, first-party authentication, PostgreSQL, Redis, and pipeline deferral are recorded under `docs/adr/`. Concrete cloud, queue, event/search store, object store, and federation provider decisions remain deferred. The logical contracts are intended to survive those choices.
