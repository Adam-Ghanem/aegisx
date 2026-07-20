from sqlalchemy import inspect

from aegisx import models  # noqa: F401
from aegisx.database import Base, Database


def test_foundation_schema_can_be_created_from_empty_database() -> None:
    database = Database("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(database.engine)
    assert set(inspect(database.engine).get_table_names()) == {
        "audit_entries",
        "memberships",
        "membership_roles",
        "organizations",
        "permissions",
        "refresh_tokens",
        "role_permissions",
        "roles",
        "users",
        "workspaces",
    }


def test_tenant_owned_tables_have_organization_id() -> None:
    for name in (
        "workspaces",
        "memberships",
        "roles",
        "role_permissions",
        "membership_roles",
        "audit_entries",
    ):
        assert "organization_id" in Base.metadata.tables[name].columns
