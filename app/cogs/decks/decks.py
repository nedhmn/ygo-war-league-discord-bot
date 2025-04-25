import discord
from discord import app_commands
from discord.ext import commands


class DecksCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="submit_decks", description="Submit decks")
    async def submit_decks(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("TBD")

    @app_commands.command(name="deck", description="Get a deck")
    async def decks(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("TBD")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DecksCog(bot))
