from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands

from shared.database.models import Punishment
from shared.database.session import SessionLocal


class ModerationCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def record(self, guild_id: str, user_id: str, moderator_id: str, kind: str, reason: str, expires_at: datetime | None = None) -> None:
        if SessionLocal is None:
            raise RuntimeError("DATABASE_URL is not configured")
        with SessionLocal() as session:
            session.add(Punishment(guild_id=guild_id, user_id=user_id, moderator_id=moderator_id, kind=kind, reason=reason, expires_at=expires_at))
            session.commit()

    @app_commands.command(name="advertir", description="Adverte um membro")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def advertir(self, interaction: discord.Interaction, membro: discord.Member, motivo: str) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("Use dentro de um servidor.", ephemeral=True)
            return
        await self.record(str(interaction.guild.id), str(membro.id), str(interaction.user.id), "warn", motivo)
        await interaction.response.send_message(f"{membro.mention} advertido. Motivo: {motivo}", ephemeral=True)

    @app_commands.command(name="expulsar", description="Expulsa um membro")
    @app_commands.checks.has_permissions(kick_members=True)
    async def expulsar(self, interaction: discord.Interaction, membro: discord.Member, motivo: str) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("Use dentro de um servidor.", ephemeral=True)
            return
        if interaction.guild.me.top_role <= membro.top_role:
            await interaction.response.send_message("Não posso expulsar este membro por hierarquia de cargos.", ephemeral=True)
            return
        await membro.kick(reason=motivo)
        await self.record(str(interaction.guild.id), str(membro.id), str(interaction.user.id), "kick", motivo)
        await interaction.response.send_message(f"{membro.mention} foi expulso.", ephemeral=True)

    @app_commands.command(name="banir", description="Bane um membro")
    @app_commands.checks.has_permissions(ban_members=True)
    async def banir(self, interaction: discord.Interaction, membro: discord.Member, motivo: str) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("Use dentro de um servidor.", ephemeral=True)
            return
        if interaction.guild.me.top_role <= membro.top_role:
            await interaction.response.send_message("Não posso banir este membro por hierarquia de cargos.", ephemeral=True)
            return
        await membro.ban(reason=motivo)
        await self.record(str(interaction.guild.id), str(membro.id), str(interaction.user.id), "ban", motivo)
        await interaction.response.send_message(f"{membro.mention} foi banido.", ephemeral=True)

    @app_commands.command(name="silenciar", description="Silencia temporariamente um membro")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def silenciar(self, interaction: discord.Interaction, membro: discord.Member, minutos: app_commands.Range[int, 1, 10080], motivo: str) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("Use dentro de um servidor.", ephemeral=True)
            return
        expires = datetime.utcnow() + timedelta(minutes=minutos)
        await membro.timeout(timedelta(minutes=minutos), reason=motivo)
        await self.record(str(interaction.guild.id), str(membro.id), str(interaction.user.id), "timeout", motivo, expires)
        await interaction.response.send_message(f"{membro.mention} silenciado por {minutos} minuto(s).", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ModerationCommands(bot))
