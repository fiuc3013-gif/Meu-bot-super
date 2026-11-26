"""add pending Miyora features

Revision ID: 20261125_003
Revises: 20261125_002
Create Date: 2026-11-25
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20261125_003"
down_revision: Union[str, Sequence[str], None] = "20261125_002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("loan_payments", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("loan_id", sa.Integer(), nullable=False), sa.Column("installment_number", sa.Integer(), nullable=False), sa.Column("amount", sa.Numeric(20, 2), nullable=False), sa.Column("due_at", sa.DateTime(timezone=True), nullable=False), sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True), sa.UniqueConstraint("loan_id", "installment_number", name="uq_loan_installment"))
    op.create_table("ticket_logs", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("ticket_id", sa.Integer(), nullable=False), sa.Column("actor_id", sa.String(32), nullable=False), sa.Column("action", sa.String(32), nullable=False), sa.Column("detail", sa.String(500), nullable=False, server_default=""), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("auto_messages", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("guild_id", sa.String(32), nullable=False), sa.Column("event", sa.String(24), nullable=False), sa.Column("channel_id", sa.String(32), nullable=False), sa.Column("template", sa.Text(), nullable=False), sa.UniqueConstraint("guild_id", "event", name="uq_auto_message_guild_event"))
    op.create_table("moderation_rules", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("guild_id", sa.String(32), nullable=False), sa.Column("rule_type", sa.String(24), nullable=False), sa.Column("config", sa.JSON(), nullable=False, server_default=sa.text("'{}'")), sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")), sa.UniqueConstraint("guild_id", "rule_type", name="uq_moderation_rule_guild_type"))
    op.create_table("trap_events", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("guild_id", sa.String(32), nullable=False), sa.Column("channel_id", sa.String(32), nullable=False), sa.Column("user_id", sa.String(32), nullable=False), sa.Column("detector", sa.String(32), nullable=False), sa.Column("action", sa.String(32), nullable=False), sa.Column("detail", sa.String(500), nullable=False, server_default=""), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))


def downgrade() -> None:
    for table in ("trap_events", "moderation_rules", "auto_messages", "ticket_logs", "loan_payments"):
        op.drop_table(table)
