"""add Miyora integrated systems

Revision ID: 20261125_002
Revises: 20261125_001
Create Date: 2026-11-25
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20261125_002"
down_revision: Union[str, Sequence[str], None] = "20261125_001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("guild_configs", sa.Column("welcome_config", sa.JSON(), nullable=False, server_default=sa.text("'{}'")))
    op.add_column("guild_configs", sa.Column("moderation_config", sa.JSON(), nullable=False, server_default=sa.text("'{}'")))
    op.add_column("guild_configs", sa.Column("xp_config", sa.JSON(), nullable=False, server_default=sa.text("'{}'")))
    op.add_column("guild_configs", sa.Column("economy_config", sa.JSON(), nullable=False, server_default=sa.text("'{}'")))
    op.add_column("guild_configs", sa.Column("ticket_config", sa.JSON(), nullable=False, server_default=sa.text("'{}'")))

    op.create_table("xp_profiles", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("guild_id", sa.String(32), nullable=False), sa.Column("user_id", sa.String(32), nullable=False), sa.Column("xp", sa.Integer(), nullable=False, server_default="0"), sa.Column("level", sa.Integer(), nullable=False, server_default="0"), sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=True), sa.UniqueConstraint("guild_id", "user_id", name="uq_xp_profile_guild_user"))
    op.create_index("ix_xp_guild_level", "xp_profiles", ["guild_id", "level"])

    op.create_table("punishments", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("guild_id", sa.String(32), nullable=False), sa.Column("user_id", sa.String(32), nullable=False), sa.Column("moderator_id", sa.String(32), nullable=False), sa.Column("kind", sa.String(24), nullable=False), sa.Column("reason", sa.String(500), nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_punishment_guild_user", "punishments", ["guild_id", "user_id"])

    op.create_table("economy_wallets", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("guild_id", sa.String(32), nullable=False), sa.Column("user_id", sa.String(32), nullable=False), sa.Column("balance", sa.Numeric(20, 2), nullable=False, server_default="0"), sa.UniqueConstraint("guild_id", "user_id", name="uq_wallet_guild_user"))
    op.create_table("global_balances", sa.Column("user_id", sa.String(32), primary_key=True), sa.Column("balance", sa.Numeric(20, 2), nullable=False, server_default="0"))
    op.create_table("economy_transactions", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("idempotency_key", sa.String(128), nullable=False), sa.Column("user_id", sa.String(32), nullable=False), sa.Column("guild_id", sa.String(32), nullable=True), sa.Column("kind", sa.String(32), nullable=False), sa.Column("amount", sa.Numeric(20, 2), nullable=False), sa.Column("balance_before", sa.Numeric(20, 2), nullable=False), sa.Column("balance_after", sa.Numeric(20, 2), nullable=False), sa.Column("reason", sa.String(500), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.UniqueConstraint("idempotency_key", name="uq_economy_transaction_idempotency"))
    op.create_index("ix_economy_user", "economy_transactions", ["user_id"])

    op.create_table("audit_logs", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("administrator_id", sa.String(32), nullable=False), sa.Column("action", sa.String(64), nullable=False), sa.Column("entity_type", sa.String(64), nullable=False), sa.Column("entity_id", sa.String(32), nullable=True), sa.Column("before_value", sa.JSON(), nullable=True), sa.Column("after_value", sa.JSON(), nullable=True), sa.Column("reason", sa.String(500), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))

    op.create_table("store_products", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("scope", sa.String(16), nullable=False), sa.Column("guild_id", sa.String(32), nullable=True), sa.Column("name", sa.String(100), nullable=False), sa.Column("description", sa.String(500), nullable=False, server_default=""), sa.Column("price", sa.Numeric(20, 2), nullable=False), sa.Column("stock", sa.Integer(), nullable=True), sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")))
    op.create_table("store_purchases", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("idempotency_key", sa.String(128), nullable=False), sa.Column("product_id", sa.Integer(), nullable=False), sa.Column("user_id", sa.String(32), nullable=False), sa.Column("guild_id", sa.String(32), nullable=True), sa.Column("amount", sa.Numeric(20, 2), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.UniqueConstraint("idempotency_key", name="uq_store_purchase_idempotency"))

    op.create_table("loans", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("idempotency_key", sa.String(128), nullable=False), sa.Column("user_id", sa.String(32), nullable=False), sa.Column("requested_amount", sa.Numeric(20, 2), nullable=False), sa.Column("approved_amount", sa.Numeric(20, 2), nullable=True), sa.Column("interest_rate", sa.Numeric(6, 4), nullable=False, server_default="0.25"), sa.Column("installments", sa.Integer(), nullable=False), sa.Column("status", sa.String(16), nullable=False, server_default="pending"), sa.Column("due_at", sa.DateTime(timezone=True), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.UniqueConstraint("idempotency_key", name="uq_loan_idempotency"))
    op.create_table("booster_requests", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("guild_id", sa.String(32), nullable=False), sa.Column("user_id", sa.String(32), nullable=False), sa.Column("benefit", sa.String(200), nullable=False), sa.Column("status", sa.String(16), nullable=False, server_default="pending"), sa.Column("reviewed_by", sa.String(32), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))

    op.create_table("tickets", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("guild_id", sa.String(32), nullable=False), sa.Column("channel_id", sa.String(32), nullable=False), sa.Column("user_id", sa.String(32), nullable=False), sa.Column("category", sa.String(64), nullable=False), sa.Column("status", sa.String(16), nullable=False, server_default="open"), sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False), sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True))
    op.create_table("giveaways", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("guild_id", sa.String(32), nullable=False), sa.Column("channel_id", sa.String(32), nullable=False), sa.Column("creator_id", sa.String(32), nullable=False), sa.Column("prize", sa.String(200), nullable=False), sa.Column("winners_count", sa.Integer(), nullable=False), sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False), sa.Column("message_id", sa.String(32), nullable=True), sa.Column("status", sa.String(16), nullable=False, server_default="open"))
    op.create_table("giveaway_participants", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("giveaway_id", sa.Integer(), nullable=False), sa.Column("user_id", sa.String(32), nullable=False))
    op.create_unique_constraint("uq_giveaway_user", "giveaway_participants", ["giveaway_id", "user_id"])

    op.create_table("server_reviews", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("guild_id", sa.String(32), nullable=False), sa.Column("user_id", sa.String(32), nullable=False), sa.Column("rating", sa.Integer(), nullable=False), sa.Column("comment", sa.String(1000), nullable=False, server_default=""), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.UniqueConstraint("guild_id", "user_id", name="uq_server_review_guild_user"))
    op.create_table("auto_roles", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("guild_id", sa.String(32), nullable=False), sa.Column("role_id", sa.String(32), nullable=False), sa.UniqueConstraint("guild_id", "role_id", name="uq_auto_role_guild_role"))


def downgrade() -> None:
    for table in ("auto_roles", "server_reviews", "giveaway_participants", "giveaways", "tickets", "booster_requests", "loans", "store_purchases", "store_products", "audit_logs", "economy_transactions", "global_balances", "economy_wallets", "punishments", "xp_profiles"):
        op.drop_table(table)
    for column in ("ticket_config", "economy_config", "xp_config", "moderation_config", "welcome_config"):
        op.drop_column("guild_configs", column)
