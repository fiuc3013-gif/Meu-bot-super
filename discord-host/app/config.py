from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    discord_bot_token: str = ""
    discord_application_id: str = ""
    discord_sync_commands: bool = False
    discord_test_guild_id: str = ""
    database_url: str = ""
    bot_api_host: str = "0.0.0.0"
    bot_api_port: int = 8000
    bot_api_token: str = ""
    owner_api_token: str = ""
    owner_discord_user_id: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
