import discord
from discord.ext import commands
from sqlalchemy import select

from shared.database.models import AutoRole
from shared.database.session import SessionLocal


class AutoRoleEvents(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        if SessionLocal is None:
            return
        with SessionLocal() as session:
            role_ids = session.execute(select(AutoRole.role_id).where(AutoRole.guild_id == str(member.guild.id))).scalars().all()
        for role_id in role_ids:
            role = member.guild.get_role(int(role_id))
            if role is not None and member.guild.me.guild_permissions.manage_roles and role.position < member.guild.me.top_role.position:
                await member.add_roles(role, reason="Cargo automático Miyora")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AutoRoleEvents(bot))
