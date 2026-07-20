from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from .context import TenantContext


class AuthorizationDecision(StrEnum):
    ALLOW = "allow"
    DENY_TENANT = "deny_tenant"
    DENY_PERMISSION = "deny_permission"
    DENY_STATE = "deny_state"


@dataclass(frozen=True, slots=True)
class PolicyRequest:
    permission: str
    resource_tenant_id: UUID
    resource_state: str | None = None
    allowed_states: frozenset[str] | None = None


class PermissionPolicy:
    """Small, deny-first policy core; callers must explicitly enforce ALLOW."""

    @staticmethod
    def evaluate(context: TenantContext, request: PolicyRequest) -> AuthorizationDecision:
        if not context.owns(request.resource_tenant_id):
            return AuthorizationDecision.DENY_TENANT
        if not request.permission or request.permission not in context.permissions:
            return AuthorizationDecision.DENY_PERMISSION
        if (
            request.allowed_states is not None
            and request.resource_state not in request.allowed_states
        ):
            return AuthorizationDecision.DENY_STATE
        return AuthorizationDecision.ALLOW

    @classmethod
    def require(cls, context: TenantContext, request: PolicyRequest) -> None:
        if cls.evaluate(context, request) is not AuthorizationDecision.ALLOW:
            raise PermissionError("access denied")
