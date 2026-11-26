import platform

import discord
from discord import app_commands
from discord.ext import commands

from bot.utils.embeds import miyora_embed


class BotInfoCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="botinfo", description="Exibe informações sobre o Miyora")
    async def botinfo(self, interaction: discord.Interaction) -> None:
        embed = miyora_embed("Miyora", "Assistente kawaii do seu servidor")
        embed.add_field(name="Python", value=platform.python_version(), inline=True)
        embed.add_field(name="discord.py", value=discord.__version__, inline=True)
        embed.add_field(name="Servidores", value=str(len(self.bot.guilds)), inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BotInfoCommands(bot))
