"""Add user_id ownership column to journeys table.

Revision ID: 003
Revises: 002
Create Date: 2026-11-20 14:50:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("journeys", sa.Column("user_id", sa.Integer(), nullable=True))
    with op.batch_alter_table("journeys") as batch_op:
        batch_op.create_foreign_key(
            "fk_journeys_user_id_users",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )
        batch_op.create_index("ix_journeys_user_id", ["user_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("journeys") as batch_op:
        batch_op.drop_index("ix_journeys_user_id")
        batch_op.drop_constraint("fk_journeys_user_id_users", type_="foreignkey")
        batch_op.drop_column("user_id")
