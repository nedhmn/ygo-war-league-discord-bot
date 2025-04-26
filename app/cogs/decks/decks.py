import asyncio
import logging

import discord
from discord import app_commands
from discord.ext import commands

from app.cogs.decks.config import deck_settings
from app.cogs.decks.deck_submission import DeckSubmissionSession
from app.cogs.decks.utils import load_league_decks_to_db
from app.core.db import get_async_db_session
from app.core.exceptions import UserCancelled

logger = logging.getLogger(__name__)


class DecksCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.active_sessions: set[int] = set()

    @app_commands.command(name="submit_decks", description="Submit decks")
    @app_commands.checks.has_any_role(*deck_settings.ALLOWED_ROLES)
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

        async with get_async_db_session() as db_session:
            session = DeckSubmissionSession(
                self.bot, interaction.user, db_session, deck_settings
            )

            try:
                entries = await session.run()
                await load_league_decks_to_db(entries, db_session)
            except (asyncio.TimeoutError, UserCancelled):
                pass
            finally:
                self.active_sessions.remove(interaction.user.id)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DecksCog(bot))
