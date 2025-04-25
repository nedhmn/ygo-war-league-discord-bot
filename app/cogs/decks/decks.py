import asyncio
import logging

import discord
from discord import app_commands
from discord.ext import commands

from app.cogs.decks.config import DeckSettings
from app.cogs.decks.deck_submission import DeckSubmissionSession
from app.core.exceptions import UserCancelled

logger = logging.getLogger(__name__)


class DecksCog(commands.Cog):
    def __init__(self, bot: commands.Bot, settings: DeckSettings) -> None:
        self.bot = bot
        self.settings = settings
        self.active_sessions: set[int] = set()

    @app_commands.command(name="submit_decks", description="Submit decks")
    async def submit_decks(self, interaction: discord.Interaction) -> None:
        if interaction.user.id in self.active_sessions:
            await interaction.response.send_message(
                "⚠️ You already have an active submission session.", ephemeral=True
            )
            return

        self.active_sessions.add(interaction.user.id)
        await interaction.response.send_message(
            "📬 Check your DMs to submit decks!", ephemeral=True
        )

        session = DeckSubmissionSession(self.bot, interaction.user, self.settings)

        try:
            entries = await session.run()
            logger.info(f"User {interaction.user} submitted {len(entries)} decks.")
            logger.debug(f"Deck entries: {entries}")
        except (asyncio.TimeoutError, UserCancelled):
            pass
        finally:
            self.active_sessions.remove(interaction.user.id)


async def setup(bot: commands.Bot) -> None:
    deck_settings = DeckSettings()
    await bot.add_cog(DecksCog(bot, deck_settings))
