from __future__ import annotations

# ruff: noqa: S101
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from aegisx.security import (
    AccessTokenCodec,
    ActorType,
    AuditMetadata,
    AuthorizationDecision,
    InMemoryRefreshTokenStore,
    PasswordHasher,
    PermissionPolicy,
    PolicyRequest,
    RefreshTokenService,
    TenantContext,
    TokenError,
)


def context(tenant_id: object, permissions: frozenset[str]) -> TenantContext:
    return TenantContext(tenant_id, uuid4(), ActorType.USER, permissions, "req-1", "corr-1")  # type: ignore[arg-type]


def test_password_hash_is_salted_and_malformed_hash_fails_closed() -> None:
    hasher = PasswordHasher()
    first = hasher.hash("correct horse battery staple")
    second = hasher.hash("correct horse battery staple")
    assert first != second
    assert hasher.verify("correct horse battery staple", first)
    assert not hasher.verify("wrong", first)
    assert not hasher.verify("password", "not-a-hash")
    assert not hasher.verify("password", "scrypt$1073741824$8$1$c2FsdA$ZGVyaXZlZA")
    assert "correct horse" not in first


def test_policy_denies_missing_permission_wrong_tenant_and_invalid_state() -> None:
    tenant, foreign = uuid4(), uuid4()
    actor = context(tenant, frozenset({"alert:triage"}))
    assert (
        PermissionPolicy.evaluate(actor, PolicyRequest("alert:read", tenant))
        is AuthorizationDecision.DENY_PERMISSION
    )
    assert (
        PermissionPolicy.evaluate(actor, PolicyRequest("alert:triage", foreign))
        is AuthorizationDecision.DENY_TENANT
    )
    request = PolicyRequest("alert:triage", tenant, "resolved", frozenset({"new"}))
    assert PermissionPolicy.evaluate(actor, request) is AuthorizationDecision.DENY_STATE
    with pytest.raises(PermissionError, match="access denied"):
        PermissionPolicy.require(actor, PolicyRequest("alert:triage", foreign))


def test_policy_allows_only_explicit_permission_for_owned_resource() -> None:
    tenant = uuid4()
    request = PolicyRequest("alert:read", tenant, "new", frozenset({"new"}))
    assert (
        PermissionPolicy.evaluate(context(tenant, frozenset({"alert:read"})), request)
        is AuthorizationDecision.ALLOW
    )


def test_access_token_rejects_tampering_expiry_and_wrong_audience() -> None:
    now = datetime(2026, 7, 20, tzinfo=UTC)
    codec = AccessTokenCodec(b"s" * 32, "aegisx", "api")
    service = RefreshTokenService(codec, InMemoryRefreshTokenStore(), b"h" * 32, clock=lambda: now)
    pair = service.issue(uuid4(), uuid4(), frozenset({"alert:read"}))
    assert codec.decode(pair.access_token, now).permissions == frozenset({"alert:read"})
    header, payload, signature = pair.access_token.split(".")
    changed = ("A" if payload[0] != "A" else "B") + payload[1:]
    with pytest.raises(TokenError, match="invalid token"):
        codec.decode(f"{header}.{changed}.{signature}", now)
    with pytest.raises(TokenError, match="invalid token"):
        AccessTokenCodec(b"s" * 32, "aegisx", "other").decode(pair.access_token, now)
    with pytest.raises(TokenError, match="invalid token"):
        codec.decode(pair.access_token, pair.access_expires_at)


def test_refresh_rotation_detects_replay_and_revokes_family() -> None:
    now = datetime(2026, 7, 20, tzinfo=UTC)
    service = RefreshTokenService(
        AccessTokenCodec(b"s" * 32, "aegisx", "api"),
        InMemoryRefreshTokenStore(),
        b"h" * 32,
        clock=lambda: now,
    )
    original = service.issue(uuid4(), uuid4(), frozenset({"alert:read"}))
    rotated = service.rotate(original.refresh_token, frozenset({"alert:read"}))
    assert rotated.refresh_token != original.refresh_token
    with pytest.raises(TokenError, match="invalid refresh token"):
        service.rotate(original.refresh_token, frozenset())
    with pytest.raises(TokenError, match="invalid refresh token"):
        service.rotate(rotated.refresh_token, frozenset())


@pytest.mark.parametrize(
    "key", ["password", "access_token", "Authorization", "raw-event", "client_secret"]
)
def test_audit_metadata_rejects_sensitive_keys(key: str) -> None:
    with pytest.raises(ValueError, match="sensitive"):
        AuditMetadata({key: "must-not-appear"})


def test_audit_metadata_copies_input_and_rejects_nested_content() -> None:
    source = {"count": 2}
    metadata = AuditMetadata(source)
    source["count"] = 3
    assert metadata.as_dict() == {"count": 2}
    with pytest.raises(TypeError):
        AuditMetadata({"details": {"unsafe": "unbounded"}})  # type: ignore[dict-item]
