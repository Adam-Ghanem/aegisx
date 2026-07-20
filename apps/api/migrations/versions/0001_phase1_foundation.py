"""Phase 1 control-plane foundation."""

from alembic import op

from aegisx import models  # noqa: F401
from aegisx.database import Base

revision = "0001_phase1_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind(), checkfirst=False)


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind(), checkfirst=False)
