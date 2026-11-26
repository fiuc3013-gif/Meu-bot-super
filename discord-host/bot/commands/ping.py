import discord
from discord import app_commands
from discord.ext import commands

from bot.utils.embeds import miyora_embed


class PingCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ping", description="Verifica a latência do Miyora")
    @app_commands.checks.cooldown(1, 5.0)
    async def ping(self, interaction: discord.Interaction) -> None:
        latency = round(self.bot.latency * 1000)
        embed = miyora_embed("Pong!", f"Latência atual: **{latency} ms** ✨")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PingCommands(bot))
