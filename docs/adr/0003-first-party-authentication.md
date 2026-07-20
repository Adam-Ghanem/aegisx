# ADR 0003: First-Party Authentication Architecture

- Status: Accepted
- Date: 2026-07-20

## Context

Phase 1 requires a self-contained, testable authentication foundation. The earlier external-IdP-only assumption does not satisfy login, refresh rotation, revocation, and password requirements.

## Decision

Implement email/password authentication behind application interfaces. Store memory-hard password hashes. Issue short-lived signed access tokens and single-use opaque refresh tokens; persist only refresh-token hashes and rotate transactionally. Model sessions and token families for logout, revocation, replay detection, and metadata. Keep email delivery, verification, password reset, MFA, and future OIDC/SAML behind ports.

Tokens identify user, session, issuer, audience, issuance/expiry, and token version. They do not embed permission snapshots or secrets. Authorization revalidates current user, organization, membership, and resource state.

## Consequences

AegisX owns credential security, reset safety, rate limits, and key rotation. Generic errors and safe audit events are mandatory. Production readiness must assess whether password authentication is acceptable for the target deployment.

