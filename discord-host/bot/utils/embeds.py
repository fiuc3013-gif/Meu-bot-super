import discord


MIYORA_COLOR = discord.Color.from_rgb(242, 137, 181)


def miyora_embed(title: str, description: str | None = None) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=MIYORA_COLOR)
    embed.set_footer(text="Miyora")
    return embed
