# Roadmap

## Phase 0 — Foundation

Approve product requirements, architecture, domain language, security boundaries, quality plans, risks, and responsibilities. No runtime-control claim is made by Phase 0 documents.

## Phase 1 — Secure control-plane foundation

- Establish the modular-monolith monorepo, CI, environments, configuration, dependency policy, PostgreSQL, and bounded Redis use.
- Implement first-party authentication, refresh rotation and revocation, Organization and Workspace tenancy, memberships, deny-by-default authorization, and audit.
- Demonstrate two-organization and cross-workspace isolation, authentication replay resistance, policy coverage, migrations, and basic telemetry.
- Define extension ports without implementing ingestion or SOC domain workflows.

Exit: the control-plane trust boundary is deployable and verified. Event ingestion, normalization, detections, alerts, and incidents remain explicitly deferred. See `docs/phase-1-plan.md`.

## Phase 2 — First security-operations vertical slice

Add one authenticated synthetic source through durable ingest, immutable raw retention, normalization, one deterministic detection, alert triage, and query. Then expand source management, schema registry, rule staging, signed webhooks, quotas, quarantine and dead letters, retention/deletion/export jobs, and the connected SOC UI.

Exit: a production-like end-to-end slice proves tenant isolation, idempotency, durability, explainable detection, audit, and operational telemetry at a measured baseline.

## Phase 3 — MVP capability and controlled pilot

Broaden supported sources and SOC workflows, then onboard selected tenants with synthetic-first validation. Run load, resilience, restore, privacy, and security exercises; tune limits, cost, SLOs, and detections.

Exit: agreed pilot reliability, no unresolved critical or high security findings, and established support ownership.

## Phase 4 — General availability

Add justified regionalization, billing and entitlements, self-service onboarding, support tooling, progressive delivery, disaster-recovery exercises, and evidence for public commitments.

## Decision gates

1. Approve Phase 1 terminology, authentication architecture, tenancy boundary, and persistence ADRs.
2. Verify Phase 1 authorization, isolation, refresh replay, audit, migration, and operations acceptance criteria.
3. Approve Phase 2 canonical schema, raw-retention policy, durable transport, event store, rule constraints, workload, and cost model.
4. Approve pilot threat review, privacy assessment, SLOs, restore evidence, and incident readiness.
