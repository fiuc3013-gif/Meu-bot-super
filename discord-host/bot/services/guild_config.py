from dataclasses import dataclass


@dataclass(frozen=True)
class GuildConfig:
    guild_id: int
    locale: str = "pt-BR"


class GuildConfigService:
    """Prévia em memória para identificação; dados persistentes serão adicionados por módulos futuros."""

    def __init__(self) -> None:
        self._configs: dict[int, GuildConfig] = {}

    def get(self, guild_id: int | None) -> GuildConfig:
        if guild_id is None:
            return GuildConfig(guild_id=0)
        return self._configs.setdefault(guild_id, GuildConfig(guild_id=guild_id))

    def set_locale(self, guild_id: int, locale: str) -> GuildConfig:
        config = GuildConfig(guild_id=guild_id, locale=locale)
        self._configs[guild_id] = config
        return config
