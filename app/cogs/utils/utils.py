import discord
from discord import app_commands
from discord.ext import commands

from app.core.config import settings


class UtilsCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="latency", description="Check the bot's latency")
    async def latency(self, interaction: discord.Interaction) -> None:
        latency = round(self.bot.latency * 1000)  # Convert to milliseconds
        await interaction.response.send_message(f"🏓 Latency: {latency}ms")


async def setup(bot: commands.Bot) -> None:
    if settings.ENVIORNMENT == "local":
        await bot.add_cog(UtilsCog(bot))
