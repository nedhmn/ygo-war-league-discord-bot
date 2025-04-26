import discord

from app.core import exceptions
from app.core.config import settings


async def is_in_allowed_guilds(interaction: discord.Interaction) -> bool:
    if interaction.guild_id is None:
        raise exceptions.UnathorizedGuild

    if interaction.guild_id not in settings.ALLOWED_GUILDS:
        raise exceptions.UnathorizedGuild

    return True
