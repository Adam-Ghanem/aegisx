from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session, sessionmaker

from .models import Membership, MembershipRole, Permission, RefreshToken, RolePermission, User
from .security.passwords import PasswordHasher
from .security.tokens import RefreshTokenRecord, RefreshTokenStore, TokenError


class SqlRefreshTokenStore(RefreshTokenStore):
    """Transactional persistent refresh-token store with compare-and-set rotation."""

    def __init__(self, sessions: sessionmaker[Session]) -> None:
        self.sessions = sessions

    def get(self, token_hash: bytes) -> RefreshTokenRecord | None:
        with self.sessions() as session:
            row = session.get(RefreshToken, token_hash)
            if row is None:
                return None
            return RefreshTokenRecord(
                row.token_hash,
                row.family_id,
                row.session_id,
                row.subject,
                row.organization_id,
                _required_utc(row.expires_at),
                _utc(row.used_at),
                _utc(row.revoked_at),
            )

    def put(self, record: RefreshTokenRecord) -> None:
        with self.sessions.begin() as session:
            session.add(
                RefreshToken(
                    token_hash=record.token_hash,
                    family_id=record.family_id,
                    session_id=record.session_id,
                    subject=record.subject,
                    organization_id=record.tenant_id,
                    expires_at=record.expires_at,
                    used_at=record.used_at,
                    revoked_at=record.revoked_at,
                )
            )

    def mark_used(self, token_hash: bytes, when: datetime) -> bool:
        with self.sessions.begin() as session:
            result = session.execute(
                update(RefreshToken)
                .where(
                    RefreshToken.token_hash == token_hash,
                    RefreshToken.used_at.is_(None),
                    RefreshToken.revoked_at.is_(None),
                )
                .values(used_at=when)
            )
            return result.rowcount == 1

    def revoke_family(self, family_id: UUID, when: datetime) -> None:
        with self.sessions.begin() as session:
            session.execute(
                update(RefreshToken)
                .where(RefreshToken.family_id == family_id, RefreshToken.revoked_at.is_(None))
                .values(revoked_at=when)
            )


def authenticate_user(
    sessions: sessionmaker[Session],
    hasher: PasswordHasher,
    email: str,
    password: str,
    organization_id: UUID,
) -> tuple[UUID, frozenset[str]]:
    """Authenticate generically and resolve current active tenant permissions."""
    with sessions() as session:
        user = session.scalar(
            select(User).where(User.email == email.casefold(), User.status == "active")
        )
        valid_hash = user.password_hash if user else hasher.hash("generic-timing-equalizer")
        if not hasher.verify(password, valid_hash) or user is None:
            raise TokenError("invalid credentials")
        membership = session.scalar(
            select(Membership).where(
                Membership.organization_id == organization_id,
                Membership.user_id == user.id,
                Membership.status == "active",
            )
        )
        if membership is None:
            raise TokenError("invalid credentials")
        names = session.scalars(
            select(Permission.name)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(
                MembershipRole,
                (MembershipRole.role_id == RolePermission.role_id)
                & (MembershipRole.organization_id == RolePermission.organization_id),
            )
            .where(
                MembershipRole.organization_id == organization_id,
                MembershipRole.membership_id == membership.id,
            )
        )
        return user.id, frozenset(names)


def _utc(value: datetime | None) -> datetime | None:
    if value is None or value.tzinfo is not None:
        return value
    return value.replace(tzinfo=UTC)


def _required_utc(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)
