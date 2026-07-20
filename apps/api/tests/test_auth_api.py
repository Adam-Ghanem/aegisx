from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from aegisx.api import create_app
from aegisx.config import Settings
from aegisx.database import Base
from aegisx.models import (
    Membership,
    MembershipRole,
    Organization,
    Permission,
    Role,
    RolePermission,
    User,
)
from aegisx.security.passwords import PasswordHasher


def test_login_refresh_rotation_replay_and_logout(tmp_path: Path) -> None:
    database_path = tmp_path / "auth.db"
    app = create_app(
        Settings(
            database_url=f"sqlite+pysqlite:///{database_path}", redis_url="redis://127.0.0.1:1/0"
        )
    )
    database = app.state.database
    Base.metadata.create_all(database.engine)
    organization_id, user_id, membership_id, role_id, permission_id = (uuid4() for _ in range(5))
    with database.sessions.begin() as session:
        session.add(
            Organization(
                id=organization_id,
                name="Synthetic SOC",
                slug="synthetic-soc",
                status="active",
                created_at=datetime.now(UTC),
            )
        )
        session.add(
            User(
                id=user_id,
                email="analyst@example.test",
                password_hash=PasswordHasher().hash("correct synthetic password"),
                status="active",
                created_at=datetime.now(UTC),
            )
        )
        session.add(
            Membership(
                id=membership_id, organization_id=organization_id, user_id=user_id, status="active"
            )
        )
        session.add(Role(id=role_id, organization_id=organization_id, name="Analyst"))
        session.add(Permission(id=permission_id, name="organization:read"))
        session.flush()
        session.add(
            RolePermission(
                organization_id=organization_id, role_id=role_id, permission_id=permission_id
            )
        )
        session.add(
            MembershipRole(
                organization_id=organization_id, membership_id=membership_id, role_id=role_id
            )
        )
    client = TestClient(app)
    bad = client.post(
        "/v1/auth/login",
        json={
            "email": "analyst@example.test",
            "password": "wrong",
            "organization_id": str(organization_id),
        },
    )
    assert bad.status_code == 401
    login = client.post(
        "/v1/auth/login",
        json={
            "email": "analyst@example.test",
            "password": "correct synthetic password",
            "organization_id": str(organization_id),
        },
    )
    assert login.status_code == 200
    original = login.json()["refresh_token"]
    rotated = client.post("/v1/auth/refresh", json={"refresh_token": original})
    assert rotated.status_code == 200
    assert rotated.json()["refresh_token"] != original
    assert client.post("/v1/auth/refresh", json={"refresh_token": original}).status_code == 401
    assert (
        client.post(
            "/v1/auth/logout", json={"refresh_token": rotated.json()["refresh_token"]}
        ).status_code
        == 204
    )
