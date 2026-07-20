from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Workspace(Base):
    __tablename__ = "workspaces"
    __table_args__ = (UniqueConstraint("organization_id", "slug"),)
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)


class User(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id"),
        UniqueConstraint("organization_id", "id"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="active")


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("organization_id", "name"),
        UniqueConstraint("organization_id", "id"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)


class Permission(Base):
    __tablename__ = "permissions"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)


class RolePermission(Base):
    __tablename__ = "role_permissions"
    __table_args__ = (
        ForeignKeyConstraint(["organization_id", "role_id"], ["roles.organization_id", "roles.id"]),
    )
    organization_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    role_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    permission_id: Mapped[UUID] = mapped_column(ForeignKey("permissions.id"), primary_key=True)


class MembershipRole(Base):
    __tablename__ = "membership_roles"
    __table_args__ = (
        ForeignKeyConstraint(
            ["organization_id", "membership_id"], ["memberships.organization_id", "memberships.id"]
        ),
        ForeignKeyConstraint(["organization_id", "role_id"], ["roles.organization_id", "roles.id"]),
    )
    organization_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    membership_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    role_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)


class AuditEntry(Base):
    __tablename__ = "audit_entries"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    actor_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    actor_type: Mapped[str] = mapped_column(String(32), nullable=False)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    target_type: Mapped[str] = mapped_column(String(80), nullable=False)
    target_id: Mapped[str] = mapped_column(String(128), nullable=False)
    outcome: Mapped[str] = mapped_column(String(24), nullable=False)
    failure_reason: Mapped[str | None] = mapped_column(String(160))
    request_id: Mapped[str] = mapped_column(String(128), nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(128), nullable=False)
    source_ip: Mapped[str | None] = mapped_column(String(45))
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    token_hash: Mapped[bytes] = mapped_column(LargeBinary(32), primary_key=True)
    family_id: Mapped[UUID] = mapped_column(Uuid, nullable=False, index=True)
    session_id: Mapped[UUID] = mapped_column(Uuid, nullable=False, index=True)
    subject: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
