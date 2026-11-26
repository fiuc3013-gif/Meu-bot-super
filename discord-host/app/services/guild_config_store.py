from datetime import datetime

from sqlalchemy.orm import Session

from shared.database.models import GuildConfig
from shared.database.session import SessionLocal


class GuildConfigStore:
    def get(self, guild_id: str) -> GuildConfig | None:
        if SessionLocal is None:
            raise RuntimeError("DATABASE_URL is not configured")
        with SessionLocal() as session:
            return session.get(GuildConfig, guild_id)

    def upsert(self, guild_id: str, locale: str, enabled_modules: list[str], welcome_config: dict | None = None, moderation_config: dict | None = None, xp_config: dict | None = None, economy_config: dict | None = None, ticket_config: dict | None = None) -> GuildConfig:
        if SessionLocal is None:
            raise RuntimeError("DATABASE_URL is not configured")
        with SessionLocal() as session:
            record = session.get(GuildConfig, guild_id)
            if record is None:
                record = GuildConfig(guild_id=guild_id)
                session.add(record)
            record.locale = locale
            record.enabled_modules = enabled_modules
            record.welcome_config = welcome_config or {}
            record.moderation_config = moderation_config or {}
            record.xp_config = xp_config or {}
            record.economy_config = economy_config or {}
            record.ticket_config = ticket_config or {}
            record.updated_at = datetime.utcnow()
            session.commit()
            session.refresh(record)
            return record
