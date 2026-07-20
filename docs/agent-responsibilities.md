# Agent Responsibilities

## Purpose and shared rules

These responsibilities apply to human or AI delivery agents. They define ownership and review; they do not authorize autonomous production actions.

- Work only within an approved phase and issue scope.
- Read requirements, architecture, security, and applicable ADRs before changing a contract.
- Never use customer data, credentials, network access, dependency installation, deployment, GitHub publishing, or destructive actions without explicit authorization.
- Preserve tenant isolation, authorization, auditability, compatibility, and idempotency.
- Make reviewable changes with tests/docs; report assumptions and risks.
- Stop on ambiguous destructive migrations, security-boundary changes, or product decisions.

## Responsibility matrix

| Agent | Accountable deliverables | Mandatory reviewers |
|---|---|---|
| Product | Requirements, personas, acceptance, scope, outcomes | Architecture, Security |
| Architecture | ADRs, boundaries, interfaces, dependencies, evolution | Security, SRE, owner |
| Identity/Security | Auth, threats, tenant controls, secrets, security gates | Architecture, domain owner |
| Ingestion/Data | Contracts, canonicalization, queues, persistence, deletion | Security, Detection, SRE |
| Detection | Rule runtime, fixtures, quality, correlation | Security, Data, Product |
| API/UI | Authorized workflows, safe queries, accessibility, client contracts | Security, Product |
| SRE/Platform | Environments, CI/CD, telemetry, SLOs, DR, runbooks | Security, owners |
| Quality | Test architecture, contract suites, release evidence | Relevant owner |
| Privacy/Compliance | Data inventory, retention, subject requests, evidence | Legal sponsor, Security |
| Documentation | Terminology, links, decisions, operator/user guidance | Document owner |

Contract changes to tenant identity, permissions, events, delivery/rule semantics, retention, or audit require an ADR, compatibility/migration plan, security review, and tests. Implementers do not self-approve security-boundary changes. Production release authority remains human-controlled.

Hand-offs state what and why, affected interfaces, evidence, migration/rollback, security/privacy and observability impacts, remaining risks, and applicable requirement/ADR. Guesses are explicit.
