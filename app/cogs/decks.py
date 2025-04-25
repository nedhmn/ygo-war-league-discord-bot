import discord
from discord import app_commands
from discord.ext import commands


class DecksCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="decks", description="Get a list of decks")
    async def decks(self, interaction: discord.Interaction) -> None:
        decks = ["Deck 1", "Deck 2", "Deck 3"]

        embed = discord.Embed(
            title="Available Decks",
            description="\n".join(decks),
            color=discord.Color.blue(),
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DecksCog(bot))
