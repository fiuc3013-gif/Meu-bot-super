import discord
from discord.ext import commands

from shared.database.models import Giveaway, GiveawayParticipant
from shared.database.session import SessionLocal


class GiveawayParticipantEvents(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        if payload.user_id == getattr(self.bot.user, "id", None) or str(payload.emoji) != "🎉" or SessionLocal is None:
            return
        with SessionLocal() as session:
            giveaway = session.query(Giveaway).filter_by(guild_id=str(payload.guild_id), channel_id=str(payload.channel_id), message_id=str(payload.message_id), status="open").first()
            if giveaway is None:
                return
            existing = session.query(GiveawayParticipant).filter_by(giveaway_id=giveaway.id, user_id=str(payload.user_id)).first()
            if existing is None:
                session.add(GiveawayParticipant(giveaway_id=giveaway.id, user_id=str(payload.user_id)))
                session.commit()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GiveawayParticipantEvents(bot))
