import asyncio
import logging

import discord
from discord import app_commands
from discord.ext import commands

from app.cogs.decks.config import deck_settings
from app.cogs.decks.deck_submission import DeckSubmissionSession
from app.cogs.decks.utils import get_league_settings, load_league_decks_to_db
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
        # User is a guild member because of checks but this ensures for mypy
        if not isinstance(interaction.user, discord.Member):
            return

        async with get_async_db_session() as db_session:
            league_settings = await get_league_settings(db_session)

        # Check if the season is active
        if league_settings is None or not league_settings.is_active:
            await interaction.response.send_message(
                "⚠️ Deck submissions are closed.", ephemeral=True
            )
            return

        # Check if user has an active session
        if interaction.user.id in self.active_sessions:
            await interaction.response.send_message(
                "⚠️ You already have an active submission session.", ephemeral=True
            )
            return

        # Grab all team roles the user has
        team_roles = [
            role
            for role in interaction.user.roles
            if role.id in deck_settings.TEAM_ROLES
        ]

        # Check if user has a team role
        if not team_roles:
            await interaction.response.send_message(
                "⚠️ You need to have a team role to submit decks.", ephemeral=True
            )
            return

        # Check if user has more than one team role
        if len(team_roles) > 1:
            await interaction.response.send_message(
                "⚠️ You need to have only one team role to submit decks.", ephemeral=True
            )
            return

        # Save team role and create a new session
        team_role: discord.Role = team_roles[0]
        self.active_sessions.add(interaction.user.id)
        await interaction.response.send_message(
            "📬 Check your DMs to submit decks!", ephemeral=True
        )

        try:
            async with get_async_db_session() as db_session:
                submission_session = DeckSubmissionSession(
                    bot=self.bot,
                    user=interaction.user,
                    team_role=team_role,
                    db_session=db_session,
                    deck_settings=deck_settings,
                    league_settings=league_settings,
                )

                entries = await submission_session.run()
                await load_league_decks_to_db(entries, db_session)

        except (asyncio.TimeoutError, UserCancelled):
            pass
        finally:
            self.active_sessions.remove(interaction.user.id)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DecksCog(bot))
