# Testing Strategy

## Quality gates

Every change must pass formatting/static analysis, unit, contract/schema, authorization, tenant-isolation, integration, and appropriate dependency/security checks. Release candidates also pass end-to-end, migration, resilience, performance, restore, and security validation.

| Layer | Focus |
|---|---|
| Unit | Domain invariants, policies, parsers, rule evaluation |
| Property/fuzz | Normalization, schema bounds, tenant filters, idempotency, rule AST |
| Contract | API, event schema, queue envelope, webhooks, compatibility |
| Integration | Real stores/queues, transactions, isolation, migrations |
| End-to-end | Ingest-to-alert, query, promotion, export/deletion, audit |
| Resilience | Retries, duplicates, poison records, dependency loss, recovery |
| Performance | Throughput, tails, hot tenants, costly queries/rules |
| Security | Auth matrix, cross-tenant negatives, SSRF/injection, secrets, abuse |

## Fixtures and critical scenarios

Only deterministic synthetic data is permitted. Maintain golden events per schema/source, rule fixture packs, two-tenant ID-collision fixtures, adversarial corpora, and time controls.

Tests prove acknowledged-event durability; idempotency; wrong-tenant denial in endpoints and workers; revoked authority on queued jobs; late/out-of-order/replay behavior; stable notification identities; deletion through restore/replay; legal hold; and rolling schema/engine compatibility.

## Environments and evidence

Ephemeral environments use isolated accounts and keys. Staging mirrors production topology at reduced scale. Migrations remain compatible during rolling deploys and have rollback or roll-forward plans. Progressive delivery begins with internal synthetic tenants.

CI retains test, compatibility, migration, performance, and security reports. A flaky test may be quarantined only with an owner, issue, and deadline.
