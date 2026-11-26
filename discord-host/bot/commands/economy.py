import random
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy import select

from shared.database.models import EconomyTransaction
from shared.database.session import SessionLocal
from app.services.loans import LoanService
from app.services.boosters import BoosterService


class WorkView(discord.ui.View):
    def __init__(self, guild_id: str, user_id: str) -> None:
        super().__init__(timeout=30)
        self.guild_id = guild_id
        self.user_id = user_id
        self.answer = 6

    @discord.ui.button(label="5", style=discord.ButtonStyle.secondary)
    async def answer_five(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.finish(interaction, 5)

    @discord.ui.button(label="6", style=discord.ButtonStyle.primary)
    async def answer_six(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.finish(interaction, 6)

    @discord.ui.button(label="7", style=discord.ButtonStyle.secondary)
    async def answer_seven(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.finish(interaction, 7)

    async def finish(self, interaction: discord.Interaction, answer: int) -> None:
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("Este desafio pertence a outro usuário.", ephemeral=True)
            return
        if answer == self.answer:
            await EconomyCommands.credit_local(self.guild_id, self.user_id, 1000, f"work:{datetime.utcnow().date().isoformat()}:{self.user_id}", "Work challenge reward", "work")
            await interaction.response.edit_message(content="Desafio concluído! Você recebeu 1.000 moedas locais.", view=None)
        else:
            await interaction.response.edit_message(content="Resposta incorreta. O Miyora não concedeu moedas.", view=None)


class EconomyCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @staticmethod
    def latest_transaction(guild_id: str, user_id: str, kind: str) -> EconomyTransaction | None:
        if SessionLocal is None:
            return None
        with SessionLocal() as session:
            return session.execute(select(EconomyTransaction).where(EconomyTransaction.guild_id == guild_id, EconomyTransaction.user_id == user_id, EconomyTransaction.kind == kind).order_by(EconomyTransaction.created_at.desc()).limit(1)).scalar_one_or_none()

    @staticmethod
    async def credit_local(guild_id: str, user_id: str, amount: int, idempotency_key: str, reason: str, kind: str = "reward") -> None:
        if SessionLocal is None:
            raise RuntimeError("DATABASE_URL is not configured")
        from shared.database.models import EconomyWallet
        with SessionLocal() as session:
            existing = session.execute(select(EconomyTransaction).where(EconomyTransaction.idempotency_key == idempotency_key)).scalar_one_or_none()
            if existing:
                return
            wallet = session.execute(select(EconomyWallet).where(EconomyWallet.guild_id == guild_id, EconomyWallet.user_id == user_id).with_for_update()).scalar_one_or_none()
            if wallet is None:
                wallet = EconomyWallet(guild_id=guild_id, user_id=user_id, balance=amount)
                before = 0
            else:
                before = int(wallet.balance)
                wallet.balance = before + amount
            session.add(EconomyTransaction(idempotency_key=idempotency_key, user_id=user_id, guild_id=guild_id, kind=kind, amount=amount, balance_before=before, balance_after=before + amount, reason=reason))
            session.commit()

    @app_commands.command(name="diario", description="Recebe a recompensa diária")
    @app_commands.checks.cooldown(1, 1.0)
    async def diario(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("Use dentro de um servidor.", ephemeral=True)
            return
        today = datetime.utcnow().date().isoformat()
        key = f"daily:{interaction.guild.id}:{interaction.user.id}:{today}"
        latest = self.latest_transaction(str(interaction.guild.id), str(interaction.user.id), "daily")
        if latest and datetime.utcnow() - latest.created_at.replace(tzinfo=None) < timedelta(hours=24):
            await interaction.response.send_message("Você já recebeu a recompensa diária nas últimas 24 horas.", ephemeral=True)
            return
        amount = random.randint(1000, 5000)
        await self.credit_local(str(interaction.guild.id), str(interaction.user.id), amount, key, "Daily reward", "daily")
        await interaction.response.send_message(f"Você recebeu **{amount:,}** moedas locais.", ephemeral=True)

    @app_commands.command(name="booster", description="Solicita aprovação manual de benefício de booster")
    async def booster(self, interaction: discord.Interaction, beneficio: str) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("Use dentro de um servidor.", ephemeral=True)
            return
        try:
            request = BoosterService().request(str(interaction.guild.id), str(interaction.user.id), beneficio)
        except (RuntimeError, ValueError) as exc:
            await interaction.response.send_message(str(exc), ephemeral=True)
            return
        await interaction.response.send_message(f"Solicitação #{request.id} registrada. Benefícios só serão aplicados após aprovação.", ephemeral=True)

    @app_commands.command(name="emprestimo", description="Solicita um empréstimo ao banco Miyora")
    async def emprestimo(self, interaction: discord.Interaction, valor: app_commands.Range[float, 0.01, 50000], parcelas: app_commands.Range[int, 1, 12]) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("Use dentro de um servidor.", ephemeral=True)
            return
        try:
            loan = LoanService().request(str(interaction.user.id), __import__("decimal").Decimal(str(valor)), parcelas, f"loan:{interaction.guild.id}:{interaction.user.id}:{datetime.utcnow().date().isoformat()}")
        except (RuntimeError, ValueError) as exc:
            await interaction.response.send_message(str(exc), ephemeral=True)
            return
        await interaction.response.send_message(f"Solicitação #{loan.id} registrada. Aguarde a análise manual do proprietário.", ephemeral=True)

    @app_commands.command(name="trabalhar", description="Resolve um desafio recreativo para ganhar moedas")
    async def trabalhar(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("Use dentro de um servidor.", ephemeral=True)
            return
        latest = self.latest_transaction(str(interaction.guild.id), str(interaction.user.id), "work")
        if latest and datetime.utcnow() - latest.created_at.replace(tzinfo=None) < timedelta(hours=15):
            await interaction.response.send_message("Você precisa aguardar 15 horas entre trabalhos.", ephemeral=True)
            return
        await interaction.response.send_message("Desafio rápido: quanto é 2 + 2 + 2?", view=WorkView(str(interaction.guild.id), str(interaction.user.id)), ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(EconomyCommands(bot))
