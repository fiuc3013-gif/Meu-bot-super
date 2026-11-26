from pydantic import BaseModel, Field


class GuildConfigUpdate(BaseModel):
    locale: str = Field(default="pt-BR", min_length=2, max_length=10)
    enabled_modules: list[str] = Field(default_factory=list, max_length=50)
    welcome_config: dict = Field(default_factory=dict)
    moderation_config: dict = Field(default_factory=dict)
    xp_config: dict = Field(default_factory=dict)
    economy_config: dict = Field(default_factory=dict)
    ticket_config: dict = Field(default_factory=dict)


class GuildConfigResponse(BaseModel):
    guild_id: str
    locale: str
    enabled_modules: list[str]
    welcome_config: dict = Field(default_factory=dict)
    moderation_config: dict = Field(default_factory=dict)
    xp_config: dict = Field(default_factory=dict)
    economy_config: dict = Field(default_factory=dict)
    ticket_config: dict = Field(default_factory=dict)
