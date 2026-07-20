# Authorization Model

## Model

AegisX uses RBAC for understandable tenant administration, augmented by relationship and resource-state checks. Authentication establishes a principal; membership selects a tenant; policy decides an action on a resource. Authentication alone never grants access.

In Phase 1 terms, authentication establishes a `User`, organization membership establishes the administrative boundary, and a validated workspace selection establishes the operational boundary. `Principal` remains a future umbrella term for users and service accounts.

## Initial roles

| Role | Representative permissions |
|---|---|
| Organization Owner | Settings, membership, integrations, all analyst/admin functions |
| Organization Admin | Members except ownership transfer, sources, retention, integrations, rules |
| Detection Engineer | Read events/alerts; create, validate, and promote rules per approval policy |
| Analyst | Read events, triage alerts, manage cases, add notes |
| Auditor | Read configuration, workflow, and audit history; no export by default |
| Ingest Source | Submit events only for its bound source and tenant |
| Service Worker | Narrow machine capability for a named queue/store operation |

Permissions use `resource:action`, such as `event:read`, `event:export`, `rule:activate`, `member:manage`, and `audit:read`. Viewing does not imply exporting, editing does not imply activating, and managing integrations does not expose stored secrets.

## Policy evaluation

Allow only when identity/session is valid; tenant and membership are active; request tenant matches trusted context; the role grants explicit permission; resource ownership and state checks pass; required step-up/two-person approval passes; and no platform suspension or legal hold policy denies the action. Deny overrides allow. Policies and decisions are versioned. Background jobs and signed links recheck authorization when used.

## Platform operations and audit

Operators have no standing access to tenant event content. Time-bound support access requires tenant approval where feasible, reason/ticket, step-up authentication, narrow scope, and full audit. Emergency break-glass is separately controlled and alerted.

Audit records include principal, effective tenant, action, resource type/ID, policy version, decision/outcome, reason, request/trace ID, source network, and time. They exclude credentials and full sensitive payloads.
