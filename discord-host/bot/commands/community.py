import secrets
import asyncio
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands, tasks

from shared.database.models import Giveaway, GiveawayParticipant, ServerReview, Ticket, TicketLog, GuildConfig
from shared.database.session import SessionLocal


class CommunityCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    ticket = app_commands.Group(name="ticket", description="Gerencia tickets")

    @ticket.command(name="criar", description="Cria um ticket privado")
    async def ticket_criar(self, interaction: discord.Interaction, categoria: str = "Geral"):
        if interaction.guild is None or interaction.channel is None:
            await interaction.response.send_message("Use dentro de um servidor.", ephemeral=True)
            return
        if not interaction.guild.me.guild_permissions.manage_channels:
            await interaction.response.send_message("O Miyora não possui permissão para criar canais.", ephemeral=True)
            return
        if SessionLocal is None:
            await interaction.response.send_message("Banco de dados indisponível.", ephemeral=True)
            return
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
        }
        with SessionLocal() as session:
            guild_config = session.get(GuildConfig, str(interaction.guild.id))
            staff_role_id = (guild_config.ticket_config or {}).get("staff_role_id") if guild_config else None
        if staff_role_id:
            staff_role = interaction.guild.get_role(int(staff_role_id))
            if staff_role is not None:
                overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True)
        channel = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}"[:100], overwrites=overwrites)
        with SessionLocal() as session:
            ticket = Ticket(guild_id=str(interaction.guild.id), channel_id=str(channel.id), user_id=str(interaction.user.id), category=categoria[:64])
            session.add(ticket)
            session.flush()
            session.add(TicketLog(ticket_id=ticket.id, actor_id=str(interaction.user.id), action="opened", detail=f"Categoria: {categoria[:64]}"))
            session.commit()
        await interaction.response.send_message(f"Ticket criado: {channel.mention}", ephemeral=True)

    @ticket.command(name="encerrar", description="Encerra o ticket atual")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def ticket_encerrar(self, interaction: discord.Interaction):
        if interaction.guild is None or interaction.channel is None:
            await interaction.response.send_message("Use dentro de um servidor.", ephemeral=True)
            return
        if SessionLocal is not None:
            with SessionLocal() as session:
                record = session.query(Ticket).filter_by(guild_id=str(interaction.guild.id), channel_id=str(interaction.channel.id), status="open").first()
                if record:
                    record.status = "closed"
                    record.closed_at = datetime.utcnow()
                    session.add(TicketLog(ticket_id=record.id, actor_id=str(interaction.user.id), action="closed", detail="Ticket encerrado pelo usuário autorizado"))
                    session.commit()
        await interaction.response.send_message("Ticket encerrado.", ephemeral=True)
        await interaction.channel.delete(reason="Ticket encerrado pelo Miyora")

    sorteio = app_commands.Group(name="sorteio", description="Gerencia sorteios")

    @sorteio.command(name="criar", description="Cria um sorteio")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def sorteio_criar(self, interaction: discord.Interaction, premio: str, duracao_minutos: app_commands.Range[int, 1, 43200], vencedores: app_commands.Range[int, 1, 50], canal: discord.TextChannel):
        if interaction.guild is None:
            await interaction.response.send_message("Use dentro de um servidor.", ephemeral=True)
            return
        if SessionLocal is None:
            await interaction.response.send_message("Banco de dados indisponível.", ephemeral=True)
            return
        end_at = datetime.utcnow() + timedelta(minutes=duracao_minutos)
        message = await canal.send(f"🎉 **Sorteio: {premio}**\nReaja com 🎉 para participar.\nEncerramento: <t:{int(end_at.timestamp())}:R>")
        await message.add_reaction("🎉")
        with SessionLocal() as session:
            giveaway = Giveaway(guild_id=str(interaction.guild.id), channel_id=str(canal.id), creator_id=str(interaction.user.id), prize=premio[:200], winners_count=vencedores, ends_at=end_at, message_id=str(message.id), status="open")
            session.add(giveaway)
            session.commit()
        await interaction.response.send_message("Sorteio criado.", ephemeral=True)

    @sorteio.command(name="historico", description="Consulta sorteios registrados")
    async def sorteio_historico(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("Use dentro de um servidor.", ephemeral=True)
            return
        if SessionLocal is None:
            await interaction.response.send_message("Banco de dados indisponível.", ephemeral=True)
            return
        with SessionLocal() as session:
            items = session.query(Giveaway).filter_by(guild_id=str(interaction.guild.id)).order_by(Giveaway.id.desc()).limit(10).all()
        if not items:
            await interaction.response.send_message("Nenhum sorteio registrado.", ephemeral=True)
            return
        await interaction.response.send_message("\n".join(f"#{item.id}: {item.prize} — {item.status}" for item in items), ephemeral=True)

    @sorteio.command(name="encerramento", description="Prepara encerramento manual de um sorteio")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def sorteio_encerramento(self, interaction: discord.Interaction, sorteio_id: int):
        if interaction.guild is None:
            await interaction.response.send_message("Use dentro de um servidor.", ephemeral=True)
            return
        if SessionLocal is None:
            await interaction.response.send_message("Banco de dados indisponível.", ephemeral=True)
            return
        with SessionLocal() as session:
            giveaway = session.get(Giveaway, sorteio_id)
            if not giveaway or giveaway.guild_id != str(interaction.guild.id):
                await interaction.response.send_message("Sorteio não encontrado neste servidor.", ephemeral=True)
                return
            if giveaway.status != "open":
                await interaction.response.send_message("Este sorteio já foi encerrado.", ephemeral=True)
                return
            participants = session.query(GiveawayParticipant).filter_by(giveaway_id=sorteio_id).all()
            if not participants:
                giveaway.status = "closed"
                session.commit()
                await interaction.response.send_message("Sorteio encerrado sem participantes.", ephemeral=True)
                return
            winners = secrets.SystemRandom().sample([item.user_id for item in participants], k=min(giveaway.winners_count, len(participants)))
            giveaway.status = "closed"
            giveaway.winners = winners
            session.commit()
        await interaction.response.send_message("Vencedores: " + ", ".join(f"<@{winner}>" for winner in winners), ephemeral=True)

    @app_commands.command(name="avaliar", description="Avalia este servidor")
    async def avaliar(self, interaction: discord.Interaction, nota: app_commands.Range[int, 1, 5], comentario: str = ""):
        if interaction.guild is None:
            await interaction.response.send_message("Use dentro de um servidor.", ephemeral=True)
            return
        if SessionLocal is None:
            await interaction.response.send_message("Banco de dados indisponível.", ephemeral=True)
            return
        with SessionLocal() as session:
            existing = session.query(ServerReview).filter_by(guild_id=str(interaction.guild.id), user_id=str(interaction.user.id)).first()
            if existing:
                existing.rating = nota
                existing.comment = comentario[:1000]
            else:
                session.add(ServerReview(guild_id=str(interaction.guild.id), user_id=str(interaction.user.id), rating=nota, comment=comentario[:1000]))
            session.commit()
        await interaction.response.send_message("Sua avaliação foi registrada.", ephemeral=True)

    @app_commands.command(name="avaliacao", description="Consulta avaliações do servidor")
    async def avaliacao(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("Use dentro de um servidor.", ephemeral=True)
            return
        if SessionLocal is None:
            await interaction.response.send_message("Banco de dados indisponível.", ephemeral=True)
            return
        with SessionLocal() as session:
            reviews = session.query(ServerReview).filter_by(guild_id=str(interaction.guild.id)).all()
        if not reviews:
            await interaction.response.send_message("Nenhuma avaliação registrada.", ephemeral=True)
            return
        average = sum(review.rating for review in reviews) / len(reviews)
        await interaction.response.send_message(f"Média: **{average:.2f}/5** • {len(reviews)} avaliação(es)", ephemeral=True)

    @tasks.loop(seconds=30)
    async def close_due_giveaways(self) -> None:
        if SessionLocal is None:
            return
        now = datetime.utcnow()
        with SessionLocal() as session:
            giveaways = session.query(Giveaway).filter(Giveaway.status == "open", Giveaway.ends_at <= now).all()
            due_ids = [giveaway.id for giveaway in giveaways]
            for giveaway in giveaways:
                giveaway.status = "closed"
            session.commit()
        for giveaway_id in due_ids:
            await self.finish_giveaway(giveaway_id)

    @close_due_giveaways.before_loop
    async def before_close_due_giveaways(self) -> None:
        await self.bot.wait_until_ready()

    async def cog_load(self) -> None:
        self.close_due_giveaways.start()

    async def cog_unload(self) -> None:
        self.close_due_giveaways.cancel()

    async def finish_giveaway(self, giveaway_id: int) -> None:
        if SessionLocal is None:
            return
        with SessionLocal() as session:
            giveaway = session.get(Giveaway, giveaway_id)
            if giveaway is None:
                return
            participants = session.query(GiveawayParticipant).filter_by(giveaway_id=giveaway_id).all()
            if giveaway.winners:
                winners = giveaway.winners
            elif participants:
                winners = secrets.SystemRandom().sample([item.user_id for item in participants], k=min(giveaway.winners_count, len(participants)))
                giveaway.winners = winners
                session.commit()
            else:
                giveaway.winners = []
                session.commit()
                return
        channel = self.bot.get_channel(int(giveaway.channel_id))
        if isinstance(channel, discord.TextChannel):
            await channel.send("Sorteio encerrado automaticamente. Vencedores: " + ", ".join(f"<@{winner}>" for winner in winners))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CommunityCommands(bot))
