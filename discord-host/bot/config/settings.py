from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    discord_bot_token: str = ""
    discord_application_id: str = ""
    discord_sync_commands: bool = False
    discord_test_guild_id: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


bot_settings = BotSettings()
