# Risk Register

Likelihood (L) and impact (I) use 1–5; score is `L × I`. Owners are roles until named.

| ID | Risk | L | I | Score | Mitigation / trigger | Owner |
|---|---|---:|---:|---:|---|---|
| R-01 | Cross-tenant access through query/cache/job/worker context | 3 | 5 | 15 | Composite scoping, policy library, RLS, two-tenant tests, canaries; any leak triggers incident | Security + Platform |
| R-02 | Detection noise prevents analyst trust | 4 | 4 | 16 | Staging, fixtures, suppression, dispositions; poor useful-alert ratio triggers review | Detection |
| R-03 | Event volume makes storage/search uneconomic | 4 | 4 | 16 | Tiering, quotas, benchmarks, cost telemetry | Data Platform |
| R-04 | Ambiguous product scope delays delivery | 3 | 4 | 12 | Approve personas/MVP/out-of-scope before Phase 1 | Product |
| R-05 | Accepted data is lost or wrongly duplicated | 2 | 5 | 10 | Durable-before-ack, idempotency, reconciliation, failure tests | Data Platform |
| R-06 | Rule language enables resource exhaustion or escape | 3 | 5 | 15 | Bounded AST, cost limits, isolation, no arbitrary code | Detection + Security |
| R-07 | Sensitive data leaks through logs, exports, integrations | 3 | 5 | 15 | Minimization, redaction, canaries, scoped exports, egress controls | Security + SRE |
| R-08 | Deletion/retention differs across stores/backups | 3 | 4 | 12 | Inventory, purge manifest, tombstones, restore tests | Data + Privacy |
| R-09 | Vendor choice causes lock-in or misses regions | 3 | 3 | 9 | Logical contracts, ADRs, exit costs, region matrix | Architecture |
| R-10 | Compromised source floods or poisons pipeline | 3 | 4 | 12 | Scoped credentials, rotation, bounds, quotas, quarantine | Ingestion |
| R-11 | Supply-chain/CI compromise reaches production | 2 | 5 | 10 | Pinning, provenance, reviews, isolated CI, signed artifacts | Security + DevEx |
| R-12 | SLOs fail under realistic workload | 3 | 3 | 9 | Workload model and benchmarks before commitments | SRE + Product |
| R-13 | IdP outage or stale revocation grants/blocks access | 3 | 4 | 12 | Short sessions, revocation design, safe degraded mode | Identity |
| R-14 | Small team cannot operate polyglot storage | 3 | 4 | 12 | Managed services, fewer products, readiness gate | Architecture + SRE |

Review at phase gates and monthly during delivery. Scores 15–25 need a treatment plan before exposure. Accepted risks require sponsor/security sign-off, expiry, and rationale.

