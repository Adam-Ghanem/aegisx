from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class ActorType(StrEnum):
    USER = "user"
    SERVICE_ACCOUNT = "service_account"
    API_KEY = "api_key"
    SYSTEM = "system"


@dataclass(frozen=True, slots=True)
class TenantContext:
    """Trusted identity scope. Construct only after authentication."""

    tenant_id: UUID
    actor_id: UUID
    actor_type: ActorType
    permissions: frozenset[str]
    request_id: str
    correlation_id: str

    def __post_init__(self) -> None:
        if not self.request_id or not self.correlation_id:
            raise ValueError("request and correlation identifiers are required")

    def owns(self, resource_tenant_id: UUID) -> bool:
        return hmac_uuid_equal(self.tenant_id, resource_tenant_id)


def hmac_uuid_equal(left: UUID, right: UUID) -> bool:
    """Avoid data-dependent comparison behavior at trust boundaries."""

    import hmac

    return hmac.compare_digest(left.bytes, right.bytes)
