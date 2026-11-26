import discord
from discord import app_commands
from discord.ext import commands

from bot.utils.embeds import miyora_embed


class HelpCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ajuda", description="Mostra os comandos disponíveis")
    async def ajuda(self, interaction: discord.Interaction) -> None:
        embed = miyora_embed("Ajuda do Miyora", "Comandos básicos disponíveis:")
        embed.add_field(name="/ping", value="Verifica a latência do bot", inline=False)
        embed.add_field(name="/botinfo", value="Exibe informações do Miyora", inline=False)
        embed.add_field(name="/ajuda", value="Mostra esta lista", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(HelpCommands(bot))
