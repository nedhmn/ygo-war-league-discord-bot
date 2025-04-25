import discord
from discord import app_commands
from discord.ext import commands


class UtilsCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command(name="latency", description="Check the bot's latency")
    async def latency(self, interaction: discord.Interaction) -> None:
        latency = round(self.bot.latency * 1000)  # Convert to milliseconds
        await interaction.response.send_message(f"🏓 Latency: {latency}ms")


async def setup(bot):
    await bot.add_cog(UtilsCog(bot))
