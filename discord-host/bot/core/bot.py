import importlib
import logging
from pathlib import Path

import discord
from discord.ext import commands

from bot.config.settings import bot_settings
from bot.services.guild_config import GuildConfigService


log = logging.getLogger("miyora.bot")


class MiyoraBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True

        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
            help_command=None,
        )

        self.guild_config = GuildConfigService()
        self.tree.on_error = self.on_app_command_error

    async def setup_hook(self) -> None:
        await self.load_extensions()

        if bot_settings.discord_sync_commands:
            await self.sync_commands()

    async def load_extensions(self) -> None:
        bot_root = Path(__file__).resolve().parents[1]
        for package_name in ("events", "commands"):
            package_dir = bot_root / package_name
            for module in sorted(package_dir.glob("*.py")):
                if module.name.startswith("_"):
                    continue
                name = f"bot.{package_name}.{module.stem}"
                try:
                    importlib.import_module(name)
                    await self.load_extension(name)
                    log.info("Extensão carregada: %s", name)
                except Exception:
                    log.exception("Falha ao carregar a extensão: %s", name)

    async def sync_commands(self) -> None:
        guild_id = bot_settings.discord_test_guild_id
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            await self.tree.sync(guild=guild)
            log.info("Comandos Slash sincronizados no servidor configurado")
        else:
            await self.tree.sync()
            log.info("Comandos Slash sincronizados globalmente")

    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: discord.app_commands.AppCommandError,
    ) -> None:
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            message = f"Espere {error.retry_after:.1f}s antes de usar este comando novamente."
        elif isinstance(error, discord.app_commands.MissingPermissions):
            message = "Você não possui permissão para usar este comando."
        else:
            log.exception("Erro em interação Slash", exc_info=error)
            message = "O Miyora encontrou um erro interno. Tente novamente em instantes."

        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)

    async def close(self) -> None:
        log.info("Encerramento organizado do Miyora iniciado")
        await super().close()
