import logging

import discord
from discord.ext import commands


log = logging.getLogger("miyora.interactions")


class InteractionEvents(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        if message.guild:
            log.debug("Mensagem recebida no servidor %s", message.guild.id)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction) -> None:
        guild_id = interaction.guild_id or 0
        log.debug("Interação recebida no contexto %s", guild_id)

    @commands.Cog.listener()
    async def on_app_command_completion(
        self,
        interaction: discord.Interaction,
        command: discord.app_commands.Command,
    ) -> None:
        log.debug("Comando Slash concluído: %s", command.qualified_name)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(InteractionEvents(bot))
