from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy import select

from shared.database.models import XpProfile
from shared.database.session import SessionLocal


class XpCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="nivel", description="Consulta seu nível no servidor")
    async def nivel(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("Use este comando dentro de um servidor.", ephemeral=True)
            return
        if SessionLocal is None:
            await interaction.response.send_message("Banco de dados indisponível.", ephemeral=True)
            return
        with SessionLocal() as session:
            profile = session.execute(select(XpProfile).where(XpProfile.guild_id == str(interaction.guild.id), XpProfile.user_id == str(interaction.user.id))).scalar_one_or_none()
        xp = profile.xp if profile else 0
        level = profile.level if profile else 0
        await interaction.response.send_message(f"**{interaction.user.display_name}**: nível {level} • {xp} XP", ephemeral=True)

    @app_commands.command(name="ranking", description="Mostra o ranking de XP do servidor")
    async def ranking(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("Use este comando dentro de um servidor.", ephemeral=True)
            return
        if SessionLocal is None:
            await interaction.response.send_message("Banco de dados indisponível.", ephemeral=True)
            return
        with SessionLocal() as session:
            profiles = session.execute(select(XpProfile).where(XpProfile.guild_id == str(interaction.guild.id)).order_by(XpProfile.xp.desc()).limit(10)).scalars().all()
        if not profiles:
            await interaction.response.send_message("Ainda não há XP registrado neste servidor.", ephemeral=True)
            return
        lines = [f"{index}. <@{profile.user_id}> — {profile.xp} XP (nível {profile.level})" for index, profile in enumerate(profiles, 1)]
        await interaction.response.send_message("\n".join(lines), ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(XpCommands(bot))
