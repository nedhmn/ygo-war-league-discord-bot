from pathlib import Path
from typing import Any

import discord

from app.cogs.decks.utils import (
    get_available_teams_by_season_and_week,
    get_available_weeks_by_season,
    get_team_submission_by_season_and_week,
)
from app.core.config import settings
from app.core.db import get_async_db_session


class SeasonSelectView(discord.ui.View):
    def __init__(self, options: list[discord.SelectOption]) -> None:
        super().__init__()
        self.add_item(SeasonSelect(options))


class SeasonSelect(discord.ui.Select[Any]):
    def __init__(self, options: list[discord.SelectOption]) -> None:
        super().__init__(
            placeholder="Select a season",
            options=options,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        selected_season = int(self.values[0])
        async with get_async_db_session() as db_session:
            available_weeks = await get_available_weeks_by_season(
                db_session, selected_season
            )

        options = [
            discord.SelectOption(label=week, value=week)
            for week in str(available_weeks)
        ]
        week_select_view = WeekSelectView(options, selected_season)

        await interaction.response.send_message(
            content="Select a week:", view=week_select_view
        )


class WeekSelectView(discord.ui.View):
    def __init__(self, options: list[discord.SelectOption], season: int) -> None:
        super().__init__()
        self.add_item(WeekSelect(options, season))


class WeekSelect(discord.ui.Select[Any]):
    def __init__(self, options: list[discord.SelectOption], season: int) -> None:
        super().__init__(
            placeholder="Select a week",
            options=options,
        )
        self.season = season

    async def callback(self, interaction: discord.Interaction) -> None:
        selected_week = int(self.values[0])
        async with get_async_db_session() as db_session:
            available_teams = await get_available_teams_by_season_and_week(
                db_session, self.season, selected_week
            )

        options = [
            discord.SelectOption(label=team, value=team)
            for team in str(available_teams)
        ]
        team_select_view = TeamSelectView(options, self.season, selected_week)

        await interaction.response.send_message(
            content="Select a team:", view=team_select_view
        )


class TeamSelectView(discord.ui.View):
    def __init__(
        self, options: list[discord.SelectOption], season: int, week: int
    ) -> None:
        super().__init__()
        self.add_item(TeamSelect(options, season, week))


class TeamSelect(discord.ui.Select[Any]):
    def __init__(
        self, options: list[discord.SelectOption], season: int, week: int
    ) -> None:
        super().__init__(
            placeholder="Select a team",
            options=options,
        )
        self.season = season
        self.week = week

    async def callback(self, interaction: discord.Interaction) -> None:
        selected_team = self.values[0]

        async with get_async_db_session() as db_session:
            team_decks = await get_team_submission_by_season_and_week(
                db_session, self.season, self.week, selected_team
            )

        # Loop through each deck submission and send a formatted embed
        for deck in team_decks:
            embed = discord.Embed(
                title="Deck Submission", color=discord.Color.blurple()
            )

            embed.description = (
                f"**Season:** {deck.season}\n"
                f"**Week:** {deck.week}\n"
                f"**Submitter:** {deck.submitter_name}\n"
                f"**Team:** {deck.team_name}"
            )

            embed.add_field(
                name="Player Deck",
                value=(
                    f"**Order:** {deck.player_order}\n**Player:** {deck.player_name}"
                ),
                inline=False,
            )

            file_path = Path(deck.deck_image_path)
            if not file_path.is_file():
                file_path = settings.NO_IMAGE_FOUND_PATH

            discord_file = discord.File(file_path, filename=file_path.name)
            embed.set_image(url=f"attachment://{file_path.name}")

            if not interaction.response.is_done():
                await interaction.response.send_message(embed=embed, file=discord_file)
                continue

            await interaction.followup.send(embed=embed, file=discord_file)
