import asyncio

import discord
from discord import app_commands
from discord.ext import commands

from app.cogs.decks.config import deck_settings
from app.cogs.decks.deck_submission import DeckSubmissionSession
from app.cogs.decks.utils import (
    get_available_seasons,
    get_league_settings,
    get_submitted_teams,
    load_league_decks_to_db,
    update_league_deck_submission_status,
    update_league_season,
    update_league_week,
)
from app.cogs.decks.views import SeasonSelectView
from app.core.db import get_async_db_session
from app.core.exceptions import UserCancelled


class DecksCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.active_sessions: set[int] = set()

    @app_commands.command(
        name="set_season", description="Mod only - Sets the current season"
    )
    @app_commands.describe(season="The season to set")
    @app_commands.checks.has_any_role(*deck_settings.ADMIN_ROLES)
    async def set_season(self, interaction: discord.Interaction, season: int) -> None:
        async with get_async_db_session() as db_session:
            await update_league_season(db_session, season)

        await interaction.response.send_message(
            f"✅ Season has been updated to **{season}**!"
        )

    @app_commands.command(
        name="set_week", description="Mod only - Sets the current week"
    )
    @app_commands.describe(week="The week to set")
    @app_commands.checks.has_any_role(*deck_settings.ADMIN_ROLES)
    async def set_week(self, interaction: discord.Interaction, week: int) -> None:
        async with get_async_db_session() as db_session:
            await update_league_week(db_session, week)

        await interaction.response.send_message(
            f"✅ Week has been updated to **{week}**!"
        )

    @app_commands.command(
        name="enable_deck_submissions",
        description="Mod only - Enables deck submissions",
    )
    @app_commands.describe(enable="Enable deck submissions")
    @app_commands.checks.has_any_role(*deck_settings.ADMIN_ROLES)
    async def set_deck_submission_status(
        self, interaction: discord.Interaction, enable: bool
    ) -> None:
        async with get_async_db_session() as db_session:
            await update_league_deck_submission_status(db_session, enable)

        await interaction.response.send_message(
            f"✅ Deck submissions are **{'enabled' if enable else 'disabled'}**!"
        )

    @app_commands.command(name="submit_decks", description="Submit decks")
    @app_commands.checks.has_any_role(*deck_settings.ALLOWED_ROLES)
    async def submit_decks(self, interaction: discord.Interaction) -> None:
        # User is a guild member because of checks but this ensures for mypy
        if not isinstance(interaction.user, discord.Member):
            return

        async with get_async_db_session() as db_session:
            league_settings = await get_league_settings(db_session)

        # Check if deck submissions are enabled
        if not league_settings.enable_deck_submissions:
            await interaction.response.send_message("⚠️ Deck submissions are closed.")
            return

        # Check if user has an active session
        if interaction.user.id in self.active_sessions:
            await interaction.response.send_message(
                "⚠️ You already have an active submission session."
            )
            return

        team_roles = [
            role
            for role in interaction.user.roles
            if role.id in deck_settings.TEAM_ROLES
        ]

        # Check if user has an authorized team role
        if not team_roles:
            await interaction.response.send_message(
                "⚠️ You need to have a team role to submit decks."
            )
            return

        # Check if user has more than one team role
        if len(team_roles) > 1:
            await interaction.response.send_message(
                "⚠️ You need to have only one team role to submit decks."
            )
            return

        team_role: discord.Role = team_roles[0]
        self.active_sessions.add(interaction.user.id)
        await interaction.response.send_message(
            "📬 Check your DMs to submit decks!", ephemeral=True
        )

        try:
            async with get_async_db_session() as db_session:
                submission_session = DeckSubmissionSession(
                    bot=self.bot,
                    interaction=interaction,
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

    @app_commands.command(
        name="get_team_submission",
        description="Mod only - Get a team's submission by season and week",
    )
    @app_commands.checks.has_any_role(*deck_settings.ADMIN_ROLES)
    async def get_team_submission(self, interaction: discord.Interaction) -> None:
        # Get available seasons
        async with get_async_db_session() as db_session:
            available_seasons = await get_available_seasons(db_session)

        if not available_seasons:
            await interaction.response.send_message("❗ **No available seasons!**")
            return

        options = [
            discord.SelectOption(label=str(season)) for season in available_seasons
        ]
        season_select_view = SeasonSelectView(
            options, initiated_user=interaction.user.id
        )

        await interaction.response.send_message(
            content="Select a season:", view=season_select_view
        )

    @app_commands.command(
        name="get_current_week_status",
        description="Mod only - Get current week's status",
    )
    @app_commands.checks.has_any_role(*deck_settings.ADMIN_ROLES)
    async def get_current_week_status(self, interaction: discord.Interaction) -> None:
        # Get current league settings
        async with get_async_db_session() as db_session:
            league_settings = await get_league_settings(db_session)
            submitted_teams = await get_submitted_teams(db_session, league_settings)

        all_team_ids = set(deck_settings.TEAM_ROLES)

        # Content for submitted temas
        submitted_ids = {team.team_role_id for team in submitted_teams}
        submitted_list = (
            "\n".join(f"- <@&{team.team_role_id}>" for team in submitted_teams)
            if submitted_teams
            else "None"
        )

        # Content for non-submitted teams
        non_submitted_ids = all_team_ids - submitted_ids
        non_submitted_list = (
            "\n".join(f"- <@&{role_id}>" for role_id in sorted(non_submitted_ids))
            if non_submitted_ids
            else "None"
        )

        # Create current week status embed
        embed = discord.Embed(
            title="Current Week Status", color=discord.Color.blurple()
        )
        embed.description = (
            f"**Season:** {league_settings.current_season}\n"
            f"**Week:** {league_settings.current_week}\n"
            f"**Submissions:** {len(submitted_ids)}/{len(all_team_ids)}"
        )

        embed.add_field(name="Submitted Teams", value=submitted_list, inline=False)
        embed.add_field(
            name="Non-Submitted Teams", value=non_submitted_list, inline=False
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DecksCog(bot))
