import logging

import discord
from discord.ext import commands


log = logging.getLogger("miyora.events")


class LifecycleEvents(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        log.info("Miyora conectado como %s", self.bot.user)
        log.info("Servidores conectados: %d", len(self.bot.guilds))

    @commands.Cog.listener()
    async def on_resumed(self) -> None:
        log.info("Conexão do Miyora retomada")

    @commands.Cog.listener()
    async def on_disconnect(self) -> None:
        log.warning("Conexão do Miyora perdida; discord.py tentará reconectar")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        log.debug("Entrada preparada para servidor %s: membro %s", member.guild.id, member.id)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        log.debug("Saída preparada para servidor %s: membro %s", member.guild.id, member.id)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        if before.roles != after.roles:
            log.debug("Alteração de cargos preparada para servidor %s", after.guild.id)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel) -> None:
        log.debug("Criação de canal preparada para servidor %s", channel.guild.id)

    @commands.Cog.listener()
    async def on_guild_channel_update(
        self,
        before: discord.abc.GuildChannel,
        after: discord.abc.GuildChannel,
    ) -> None:
        log.debug("Alteração de canal preparada para servidor %s", after.guild.id)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel) -> None:
        log.debug("Exclusão de canal preparada para servidor %s", channel.guild.id)

    @commands.Cog.listener()
    async def on_error(self, event: str, *args: object, **kwargs: object) -> None:
        log.exception("Erro no evento Discord: %s", event)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LifecycleEvents(bot))
