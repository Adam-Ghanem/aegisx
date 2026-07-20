# Product Requirements

## Product statement

AegisX enables organizations to ingest security telemetry, normalize it into a stable event contract, evaluate tenant-owned and managed detection rules, investigate alerts, and coordinate auditable response. It is designed for B2B SaaS operation with strong logical tenant isolation; dedicated deployments are a future option, not a Phase 1 requirement.

## Users and jobs

- **Tenant security analyst:** triage prioritized alerts, inspect evidence, record disposition, and suppress known noise.
- **Tenant administrator:** manage members, roles, data sources, retention, integrations, and tenant rules.
- **Detection engineer:** author, validate, stage, and promote versioned detection content.
- **Platform operator:** operate ingestion and detection safely without routine access to tenant event content.
- **Auditor:** verify who changed access, rules, configuration, or alert state.

## Phase 1 minimum viable product

1. Create a tenant and invite users through an external identity provider.
2. Accept authenticated batch and streaming JSON events from tenant-scoped sources.
3. Validate, normalize, deduplicate, enrich, and retain canonical events.
4. Evaluate deterministic rules and create deduplicated alerts with evidence.
5. Provide tenant-scoped search, alert triage, rule lifecycle, and audit history.
6. Deliver signed outbound webhook notifications with retry and dead-letter handling.
7. Enforce authorization and tenant isolation at every synchronous and asynchronous boundary.

## Functional requirements

- Every resource MUST have an immutable identifier and tenant ownership where applicable.
- Event ingestion MUST be idempotent within a documented window and expose per-record outcomes.
- Raw source payload retention MUST be configurable and disabled by default after normalization unless required for replay.
- Schema and rule versions MUST be immutable after activation.
- Rules MUST support draft, validate, stage, activate, disable, and rollback states.
- Alerts MUST retain the rule version, evidence event references, severity, status, assignee, and history.
- Search MUST apply tenant and authorization filters before execution.
- All privileged and state-changing actions MUST create tamper-evident audit records.
- Export and deletion jobs MUST be asynchronous, authorized at execution time, and auditable.

## Non-functional requirements and initial SLOs

| Objective | Initial target |
|---|---|
| Ingestion API availability | 99.9% monthly |
| Accepted event durability | No acknowledged loss; replicated durable queue |
| Detection latency | p95 under 60 seconds for streaming rules |
| Interactive API latency | p95 under 500 ms excluding exports |
| Tenant isolation | No cross-tenant disclosure or action |
| Audit coverage | 100% of privileged/state-changing operations |
| Recovery | RPO <= 5 minutes, RTO <= 4 hours for control plane |
| Scale baseline | 10k events/sec aggregate, burstable; validate before commitment |

## Privacy and compliance posture

AegisX MUST minimize collected personal data, support configurable regional retention, encrypt data in transit and at rest, and support tenant export/deletion workflows. Phase 0 does not claim certification. SOC 2 readiness is a planning target; data residency, HIPAA, PCI DSS, and government requirements require explicit product decisions.

## Out of scope for the MVP

- Endpoint agents, packet capture, autonomous containment, malware execution, and general-purpose SOAR.
- Cross-tenant analytics using customer content.
- Arbitrary user-supplied code in detections or enrichment.
- A public rule marketplace and unmanaged plugins.
- On-premises or air-gapped deployment.

## Acceptance gate

Phase 1 starts only after approval of the product assumption, tenant model, canonical schema, authorization semantics, and storage/detection technology decision records.

