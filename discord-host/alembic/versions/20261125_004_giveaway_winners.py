"""persist giveaway winners

Revision ID: 20261125_004
Revises: 20261125_003
Create Date: 2026-11-25
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20261125_004"
down_revision: Union[str, Sequence[str], None] = "20261125_003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("giveaways", sa.Column("winners", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("giveaways", "winners")
