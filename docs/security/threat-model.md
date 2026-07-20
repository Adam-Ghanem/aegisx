# AegisX Repository Threat Model

## Overview

AegisX is designed as a multi-tenant security event ingestion, detection, investigation, and response SaaS. The repository is currently documentation-only; this model describes required future runtime surfaces and controls, not implemented controls. Primary assets are tenant telemetry, identities/memberships, source and integration credentials, detection rules, alert/case state, audit history, encryption keys, service credentials, and platform availability/integrity.

Highest-order invariants are: no cross-tenant read or action; no acknowledged event loss; only authorized principals change sensitive state; detections cannot escape bounded execution; audit history accurately records privileged actions; and content/secrets do not leak through telemetry, exports, or integrations.

## Threat Model, Trust Boundaries, and Assumptions

### Actors and controlled inputs

- **External attackers** control unauthenticated traffic, malformed requests, identifiers, timing, volume, and public-endpoint content.
- **Tenant users** control queries, configuration, safe-language rules, exports, workflow content, and integration endpoints; malicious tenants may target peers or shared capacity.
- **Data sources** control event payloads, timestamps, structures, identifiers, and volume after authentication. Source compromise is realistic.
- **Integration destinations** control DNS, redirects, TLS behavior, response bytes, and latency.
- **Operators** control deployment/configuration through privileged workflows but have no routine content access. Insider misuse and credential compromise remain in scope.
- **Developers/CI** control source/build inputs. Supply-chain compromise is in scope; local-only tooling is lower severity absent a path to secrets or releases.

### Trust boundaries

1. Internet to edge and public APIs.
2. Authenticated identity/source to tenant authorization context.
3. Control plane to metadata, audit, and configuration distribution.
4. Ingestion to durable log and hostile-data workers.
5. Tenant data/rules to shared detection compute/state.
6. Query service to tenant event stores.
7. Platform to webhook/enrichment destinations.
8. Runtime to secret/KMS systems.
9. CI/build to artifact registry and production deployment.
10. Backups, exports, and telemetry crossing normal access paths.

### Assumptions

The initial model assumes managed cloud primitives, TLS, an external standards-based IdP, no arbitrary user code, and shared infrastructure with logical isolation. Provider control-plane and physical compromise are handled through provider assurance and are not application findings unless AegisX configuration enables them. Endpoint collection, malware execution, autonomous containment, and on-premises deployment are outside MVP scope.

## Attack Surface, Mitigations, and Attacker Stories

### Public API and identity

Relevant classes include broken object authorization, tenant-context confusion, token/session/revocation flaws, injection, mass assignment, request smuggling, and exhaustion. Required controls are trusted tenant derivation, `(tenant_id, id)` lookup, deny-first policy, strict token issuer/audience/algorithm validation, short sessions, bounded parsing, parameterized access, quotas, and audit. A realistic story is a tenant analyst changing an alert ID to retrieve another tenant's evidence; UI hiding is no mitigation.

### Ingestion and normalization

Sources can send deeply nested, oversized, duplicate, late, malformed, secret-bearing, or adversarial payloads. Risks include parser/regex denial of service, schema confusion, downstream injection, spoofed tenant fields, poison-message blocking, and acknowledged loss. Controls are source-bound tenant identity, structural limits, durable-before-ack, quarantine, per-record outcomes, safe parsing, redaction, checksums, idempotency, and fair quotas.

### Detection engine

Tenant rules can aim for exhaustion, cross-tenant state collision, compiler escape, nondeterminism, or alert floods. Accept only a bounded declarative AST; validate cost/schema; namespace rules/state; distribute signed snapshots; isolate resources; apply output quotas; and retain deterministic evidence. User code, network/filesystem access, and unrestricted regex are prohibited.

### Storage, query, cache, and jobs

Broken filters, raw search DSL, cache key omissions, cross-tenant joins, path manipulation, broad service identities, replay after deletion, and stale job authority are key risks. Controls include server tenant predicates, composite keys, row-level security, tenant manifests, scoped identities/cache keys, tombstones, cost limits, and execution-time authorization.

### Webhooks, enrichment, and exports

Tenant destinations create SSRF, DNS rebinding, redirect, credential-leak, response-exhaustion, and replay risks. Controls include egress mediation; scheme/port/host policy; IP checks per connection; redirect restrictions; metadata/private-range blocks; time/byte caps; secret references; signed payloads; stable delivery IDs; and expiring scoped exports.

### Operations and supply chain

Risks include secrets in telemetry, excessive operator access, break-glass misuse, compromised dependencies/builds, unsigned artifacts, and untested recovery. Controls include managed secret rotation, content-free logs, time-bound support access, dual control, pinning/scanning, provenance/signing, isolated CI, least-privilege deployment, restore drills, and audit monitoring.

### Out-of-scope or reduced-likelihood stories

Arbitrary tenant code is not a capability; introducing plugins reopens this model. Cross-tenant aggregate analytics is out of scope. Local test/example weaknesses are low unless they reach CI credentials, artifacts, or runtime. Provider physical compromise is outside the application boundary, while insecure AegisX provider configuration is in scope.

## Severity Calibration (Critical, High, Medium, Low)

### Critical

- Broad/systemic cross-tenant event or credential disclosure/modification.
- Remote code execution in shared production or detection workers with data/secret access.
- Authentication bypass granting platform or many-tenant administration.
- Signing/KMS/deployment authority compromise enabling undetected takeover.

### High

- Single-tenant cross-tenant evidence access or meaningful unauthorized export.
- SSRF reaching cloud metadata or privileged internal services.
- Durable loss/silent corruption of acknowledged events at material scale.
- Rule escape or resource attack causing sustained multi-tenant outage.
- Unauthorized rule activation, retention reduction, or consequential audit tampering.

### Medium

- Tenant-scoped denial of service with bounded recovery and no loss.
- Limited sensitive metadata exposure without content or credentials.
- Stored content injection requiring an authorized user with constrained impact.
- Notification replay/duplication causing confusion without privilege gain.
- Missing audit detail for a non-critical but authorized action.

### Low

- Non-sensitive service/version information disclosure.
- Rate-limit bypass with negligible capacity/cost effect.
- Developer/test weakness without a path to CI secrets, artifacts, or runtime.
- Minor log spoofing where structured boundaries and decisions remain intact.

Severity decreases when required attacker control does not exist or impact is effectively isolated; it increases with breadth, sensitivity, persistence, stealth, and compromise of security-decision integrity.

Repository: C:\Users\adamg\Desktop\aegisx
Version: phase0-design-baseline-2026-07-20

## Phase 1 implementation impact

Phase 1 introduces first-party password authentication, signed access tokens, rotating opaque refresh tokens, shared PostgreSQL tenant data, bounded Redis use, and a browser shell. New material threats are credential stuffing, refresh-token replay, signing-key compromise, cross-organization role joins, pooled database context leakage, browser token theft, and dependency compromise.

Implemented controls include memory-hard salted password hashing, generic authentication failures, fixed-algorithm token validation, hashed refresh-token storage with family revocation on replay, tenant-first deny-by-default policy evaluation, composite tenant relationships, safe audit metadata, explicit CORS/security headers, fail-closed production keys, structured content-free request logs, pinned dependencies, and security/dependency tests. Authentication rate limiting, MFA enrollment, password reset/email verification completion, PostgreSQL RLS deployment roles, asymmetric signing-key rotation, and browser session storage policy remain release-blocking production-hardening work and are documented limitations rather than claimed controls.
