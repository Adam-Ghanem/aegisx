# Roadmap

## Phase 0 — Foundation (current)

Approve product requirements, architecture, models, security boundaries, event/storage/detection designs, quality/operations plans, risks, and responsibilities. Exit requires cross-document consistency and sponsor approval. No application code is included.

## Phase 1 — Walking skeleton

- Record ADRs for language/framework, cloud, identity, queue, metadata DB, event store, and object store.
- Establish repository standards, CI, environments, secrets, and dependency policy.
- Implement tenant/membership authorization and audit foundation.
- Prove one source through durable ingest, normalization, one rule, alert, and query.
- Demonstrate two-tenant isolation, idempotency, and basic telemetry.

Exit: production-like end-to-end slice, threat controls tested, operating cost measured.

## Phase 2 — MVP capability

Add source management, schema registry, rule staging, alert triage, search, signed webhooks, quotas, quarantine/dead letters, retention/deletion/export jobs, admin UI, and runbooks.

Exit: pilot readiness, load/resilience/security tests, restore exercise, privacy review.

## Phase 3 — Controlled pilot

Onboard selected tenants with synthetic-first validation, measure quality/cost, tune limits/SLOs, exercise incident response, close high risks, and produce SOC 2 readiness evidence.

Exit: agreed reliability, no unresolved critical/high security findings, support ownership established.

## Phase 4 — General availability

Add justified regionalization, billing/entitlements, self-service onboarding, support tooling, progressive delivery, disaster recovery exercises, and public commitments.

## Decision gates

1. Confirm product definition, personas, and MVP.
2. Choose isolation tier and regulated-data commitments.
3. Approve canonical schema v1 and rule-language constraints.
4. Approve storage benchmarks/cost model and vendor ADRs.
5. Approve pilot threat review, privacy assessment, SLOs, and incident readiness.

