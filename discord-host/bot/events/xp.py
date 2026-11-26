from datetime import datetime, timedelta

import discord
from discord.ext import commands
from sqlalchemy import select

from shared.database.models import XpProfile
from shared.database.session import SessionLocal


class XpListener(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or message.guild is None or SessionLocal is None:
            return
        now = datetime.utcnow()
        with SessionLocal() as session:
            profile = session.execute(select(XpProfile).where(XpProfile.guild_id == str(message.guild.id), XpProfile.user_id == str(message.author.id)).with_for_update()).scalar_one_or_none()
            if profile is None:
                profile = XpProfile(guild_id=str(message.guild.id), user_id=str(message.author.id), xp=0, level=0)
                session.add(profile)
            if profile.last_message_at and now - profile.last_message_at.replace(tzinfo=None) < timedelta(seconds=60):
                session.commit()
                return
            profile.xp += 15
            new_level = int((profile.xp ** 0.5) // 1)
            profile.level = new_level
            profile.last_message_at = now
            session.commit()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(XpListener(bot))
