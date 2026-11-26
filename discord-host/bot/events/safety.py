import re
from datetime import datetime, timedelta

import discord
from discord.ext import commands

from shared.database.models import AutoMessage, TrapEvent, ModerationRule
from shared.database.session import SessionLocal


class SafetyEvents(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.recent: dict[tuple[str, str], list[datetime]] = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or message.guild is None or SessionLocal is None:
            return
        guild_id = str(message.guild.id)
        user_id = str(message.author.id)
        key = (guild_id, user_id)
        now = datetime.utcnow()
        timestamps = [item for item in self.recent.setdefault(key, []) if now - item < timedelta(seconds=5)]
        timestamps.append(now)
        self.recent[key] = timestamps

        flood = len(timestamps) >= 6
        invite_filter = re.search(r"discord(?:\.gg|app\.com/invite)/", message.content, re.I)

        detector = "flood" if flood else ("invite_filter" if invite_filter else None)
        if detector is None:
            with SessionLocal() as session:
                trap = session.query(ModerationRule).filter_by(guild_id=guild_id, rule_type="trap").first()
            if trap and trap.enabled:
                trap_config = trap.config
                if str(trap_config.get("channel_id", "")) == str(message.channel.id):
                    keywords = [str(item).lower() for item in trap_config.get("keywords", [])]
                    if keywords and any(keyword in message.content.lower() for keyword in keywords):
                        detector = "trap"

        if detector is None:
            return

        action = "record_only"
        with SessionLocal() as session:
            rule = session.query(ModerationRule).filter_by(guild_id=guild_id, rule_type=detector).first()
            if rule and rule.enabled:
                config = rule.config
                exempt_users = {str(item) for item in config.get("except_users", [])}
                exempt_roles = {str(role.id) for role in getattr(message.author, "roles", [])}
                configured_roles = {str(item) for item in config.get("except_roles", [])}
                if user_id in exempt_users or exempt_roles.intersection(configured_roles):
                    return
                action = str(config.get("action", "record_only"))
                if action == "timeout" and hasattr(message.author, "timeout"):
                    await message.author.timeout(timedelta(minutes=5), reason="Proteção Miyora contra flood/spam")
                elif action == "kick" and hasattr(message.author, "kick"):
                    await message.author.kick(reason="Proteção Miyora configurada pelo proprietário")
                elif action == "ban" and hasattr(message.author, "ban"):
                    await message.author.ban(reason="Proteção Miyora configurada pelo proprietário")
            session.add(TrapEvent(guild_id=guild_id, channel_id=str(message.channel.id), user_id=user_id, detector=detector, action=action, detail="Detecção automática registrada"))
            session.commit()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        await self.send_auto_message(member, "welcome")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        await self.send_auto_message(member, "leave")

    async def send_auto_message(self, member: discord.Member, event: str) -> None:
        if SessionLocal is None:
            return
        with SessionLocal() as session:
            record = session.query(AutoMessage).filter_by(guild_id=str(member.guild.id), event=event).first()
        if record is None:
            return
        channel = member.guild.get_channel(int(record.channel_id))
        if not isinstance(channel, discord.TextChannel):
            return
        text = record.template.replace("{member}", member.mention).replace("{guild}", member.guild.name).replace("{count}", str(member.guild.member_count or 0))
        await channel.send(text)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SafetyEvents(bot))
