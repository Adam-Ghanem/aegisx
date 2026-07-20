from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from typing import Protocol, cast
from uuid import UUID, uuid4


class TokenError(ValueError):
    """Generic token failure which intentionally hides validation detail."""


@dataclass(frozen=True, slots=True)
class AccessTokenClaims:
    subject: UUID
    tenant_id: UUID
    session_id: UUID
    permissions: frozenset[str]
    issued_at: datetime
    expires_at: datetime
    token_id: UUID


class AccessTokenCodec:
    """Fixed-algorithm signed access-token codec with strict claim validation."""

    def __init__(self, signing_key: bytes, issuer: str, audience: str) -> None:
        if len(signing_key) < 32 or not issuer or not audience:
            raise ValueError("strong signing key, issuer, and audience are required")
        self._key, self._issuer, self._audience = signing_key, issuer, audience

    def encode(self, claims: AccessTokenClaims) -> str:
        header = _json_encode({"alg": "HS256", "typ": "JWT"})
        payload = _json_encode(
            {
                "aud": self._audience,
                "exp": int(claims.expires_at.timestamp()),
                "iat": int(claims.issued_at.timestamp()),
                "iss": self._issuer,
                "jti": str(claims.token_id),
                "permissions": sorted(claims.permissions),
                "sid": str(claims.session_id),
                "sub": str(claims.subject),
                "tid": str(claims.tenant_id),
            }
        )
        signed = f"{header}.{payload}".encode("ascii")
        return f"{header}.{payload}.{_encode(hmac.new(self._key, signed, hashlib.sha256).digest())}"

    def decode(self, token: str, now: datetime | None = None) -> AccessTokenClaims:
        try:
            header, payload, signature = token.split(".")
            signed = f"{header}.{payload}".encode("ascii")
            expected = hmac.new(self._key, signed, hashlib.sha256).digest()
            if not hmac.compare_digest(expected, _decode(signature)):
                raise TokenError("invalid token")
            if _json_decode(header) != {"alg": "HS256", "typ": "JWT"}:
                raise TokenError("invalid token")
            data = _json_decode(payload)
            if data.get("iss") != self._issuer or data.get("aud") != self._audience:
                raise TokenError("invalid token")
            current = now or datetime.now(UTC)
            issued = datetime.fromtimestamp(_integer(data, "iat"), UTC)
            expires = datetime.fromtimestamp(_integer(data, "exp"), UTC)
            if issued > current + timedelta(seconds=30) or expires <= current or expires <= issued:
                raise TokenError("invalid token")
            raw_permissions = data.get("permissions")
            if not isinstance(raw_permissions, list) or not all(
                isinstance(p, str) for p in raw_permissions
            ):
                raise TokenError("invalid token")
            return AccessTokenClaims(
                UUID(_string(data, "sub")),
                UUID(_string(data, "tid")),
                UUID(_string(data, "sid")),
                frozenset(raw_permissions),
                issued,
                expires,
                UUID(_string(data, "jti")),
            )
        except (KeyError, TypeError, ValueError, UnicodeError) as error:
            raise TokenError("invalid token") from error


@dataclass(frozen=True, slots=True)
class RefreshTokenRecord:
    token_hash: bytes
    family_id: UUID
    session_id: UUID
    subject: UUID
    tenant_id: UUID
    expires_at: datetime
    used_at: datetime | None = None
    revoked_at: datetime | None = None


class RefreshTokenStore(Protocol):
    def get(self, token_hash: bytes) -> RefreshTokenRecord | None: ...
    def put(self, record: RefreshTokenRecord) -> None: ...
    def mark_used(self, token_hash: bytes, when: datetime) -> bool: ...
    def revoke_family(self, family_id: UUID, when: datetime) -> None: ...


class InMemoryRefreshTokenStore:
    """Test/local store; production implementation must use transactional CAS."""

    def __init__(self) -> None:
        self._records: dict[bytes, RefreshTokenRecord] = {}

    def get(self, token_hash: bytes) -> RefreshTokenRecord | None:
        return self._records.get(token_hash)

    def put(self, record: RefreshTokenRecord) -> None:
        self._records[record.token_hash] = record

    def mark_used(self, token_hash: bytes, when: datetime) -> bool:
        record = self._records.get(token_hash)
        if record is None or record.used_at is not None or record.revoked_at is not None:
            return False
        self._records[token_hash] = replace(record, used_at=when)
        return True

    def revoke_family(self, family_id: UUID, when: datetime) -> None:
        for key, record in tuple(self._records.items()):
            if record.family_id == family_id and record.revoked_at is None:
                self._records[key] = replace(record, revoked_at=when)


@dataclass(frozen=True, slots=True)
class TokenPair:
    access_token: str
    refresh_token: str
    access_expires_at: datetime
    refresh_expires_at: datetime


class RefreshTokenService:
    def __init__(
        self,
        codec: AccessTokenCodec,
        store: RefreshTokenStore,
        hash_key: bytes,
        access_ttl: timedelta = timedelta(minutes=10),
        refresh_ttl: timedelta = timedelta(days=7),
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        if len(hash_key) < 32 or access_ttl <= timedelta(0) or refresh_ttl <= access_ttl:
            raise ValueError("secure token configuration is required")
        self._codec, self._store, self._hash_key = codec, store, hash_key
        self._access_ttl, self._refresh_ttl, self._clock = access_ttl, refresh_ttl, clock

    def issue(self, subject: UUID, tenant_id: UUID, permissions: frozenset[str]) -> TokenPair:
        return self._new_pair(subject, tenant_id, permissions, uuid4(), uuid4())

    def rotate(self, refresh_token: str, permissions: frozenset[str]) -> TokenPair:
        now, digest = self._clock(), self._hash(refresh_token)
        record = self._store.get(digest)
        if record is None or record.expires_at <= now or record.revoked_at is not None:
            raise TokenError("invalid refresh token")
        if record.used_at is not None or not self._store.mark_used(digest, now):
            self._store.revoke_family(record.family_id, now)
            raise TokenError("invalid refresh token")
        return self._new_pair(
            record.subject, record.tenant_id, permissions, record.session_id, record.family_id
        )

    def identity(self, refresh_token: str) -> tuple[UUID, UUID]:
        """Return server-stored identity for authorization revalidation before rotation."""
        record = self._store.get(self._hash(refresh_token))
        if record is None or record.expires_at <= self._clock() or record.revoked_at is not None:
            raise TokenError("invalid refresh token")
        return record.subject, record.tenant_id

    def revoke(self, refresh_token: str) -> None:
        record = self._store.get(self._hash(refresh_token))
        if record is not None:
            self._store.revoke_family(record.family_id, self._clock())

    def _new_pair(
        self,
        subject: UUID,
        tenant_id: UUID,
        permissions: frozenset[str],
        session_id: UUID,
        family_id: UUID,
    ) -> TokenPair:
        now, refresh = self._clock(), secrets.token_urlsafe(48)
        access_exp, refresh_exp = now + self._access_ttl, now + self._refresh_ttl
        claims = AccessTokenClaims(
            subject, tenant_id, session_id, permissions, now, access_exp, uuid4()
        )
        self._store.put(
            RefreshTokenRecord(
                self._hash(refresh), family_id, session_id, subject, tenant_id, refresh_exp
            )
        )
        return TokenPair(self._codec.encode(claims), refresh, access_exp, refresh_exp)

    def _hash(self, token: str) -> bytes:
        return hmac.new(self._hash_key, token.encode(), hashlib.sha256).digest()


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _json_encode(value: dict[str, object]) -> str:
    return _encode(json.dumps(value, separators=(",", ":"), sort_keys=True).encode())


def _json_decode(value: str) -> dict[str, object]:
    result = json.loads(_decode(value))
    if not isinstance(result, dict):
        raise TokenError("invalid token")
    return cast(dict[str, object], result)


def _string(data: dict[str, object], key: str) -> str:
    value = data[key]
    if not isinstance(value, str):
        raise TokenError("invalid token")
    return value


def _integer(data: dict[str, object], key: str) -> int:
    value = data[key]
    if not isinstance(value, int) or isinstance(value, bool):
        raise TokenError("invalid token")
    return value
