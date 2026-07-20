# ADR 0002: Organization and Workspace Tenancy

- Status: Accepted
- Date: 2026-07-20

## Context

Earlier Phase 0 documents used `Tenant` as both isolation root and product concept. Enterprise customers need an administrative organization containing operational workspaces.

## Decision

Organization is the administrative tenant root. Workspace is the mandatory security-data and authorization boundary. Future security resources carry immutable `organization_id` and `workspace_id`. Trusted request context selects exactly one workspace after membership and policy validation. “Tenant” remains only a generic isolation term.

## Consequences

Repositories, foreign keys, cache keys, jobs, storage prefixes, and tests scope both identifiers. Cross-workspace access is denied unless an explicit organization-level administrative policy permits it. A later decision will finalize non-owner workspace access representation.

