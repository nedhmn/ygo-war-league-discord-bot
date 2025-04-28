from pathlib import Path

import discord

from app.cogs.decks.utils import (
    create_team_decks_embed,
    get_available_teams_by_season_and_week,
    get_available_weeks_by_season,
    get_team_submission_by_season_and_week,
)
from app.core.config import settings
from app.core.db import get_async_db_session
from app.core.views import BaseSelect, BaseSelectView


class SeasonSelectView(BaseSelectView):
    def __init__(
        self, options: list[discord.SelectOption], initiated_user: int
    ) -> None:
        super().__init__(initiated_user)
        self.add_item(SeasonSelect(options))


class SeasonSelect(BaseSelect):
    def __init__(self, options: list[discord.SelectOption]) -> None:
        super().__init__(placeholder="Select a season", options=options)

    async def callback(self, interaction: discord.Interaction) -> None:
        assert isinstance(self.view, SeasonSelectView)
        await self.disable_view(interaction)

        selected_season = int(self.values[0])

        async with get_async_db_session() as db_session:
            available_weeks = await get_available_weeks_by_season(
                db_session, selected_season
            )

        options = [discord.SelectOption(label=str(week)) for week in available_weeks]
        week_select_view = WeekSelectView(
            options, self.view.initiated_user, selected_season
        )

        await interaction.followup.send(content="Select a week:", view=week_select_view)


class WeekSelectView(BaseSelectView):
    def __init__(
        self, options: list[discord.SelectOption], initiated_user: int, season: int
    ) -> None:
        super().__init__(initiated_user)
        self.add_item(WeekSelect(options, season))


class WeekSelect(BaseSelect):
    def __init__(self, options: list[discord.SelectOption], season: int) -> None:
        super().__init__(
            placeholder="Select a week",
            options=options,
        )
        self.season = season

    async def callback(self, interaction: discord.Interaction) -> None:
        assert isinstance(self.view, WeekSelectView)
        await self.disable_view(interaction)

        selected_week = int(self.values[0])

        async with get_async_db_session() as db_session:
            available_teams = await get_available_teams_by_season_and_week(
                db_session, self.season, selected_week
            )

        options = [discord.SelectOption(label=team) for team in available_teams]
        team_select_view = TeamSelectView(
            options, self.view.initiated_user, self.season, selected_week
        )

        await interaction.followup.send(content="Select a team:", view=team_select_view)


class TeamSelectView(BaseSelectView):
    def __init__(
        self,
        options: list[discord.SelectOption],
        initiated_user: int,
        season: int,
        week: int,
    ) -> None:
        super().__init__(initiated_user)
        self.add_item(TeamSelect(options, season, week))


class TeamSelect(BaseSelect):
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
        assert isinstance(self.view, TeamSelectView)
        await self.disable_view(interaction)

        selected_team = self.values[0]

        async with get_async_db_session() as db_session:
            team_decks = await get_team_submission_by_season_and_week(
                db_session, self.season, self.week, selected_team
            )

        # Loop through each deck submission and send a formatted embed
        for deck in team_decks:
            deck_image_filepath = Path(deck.deck_image_path)
            if not deck_image_filepath.is_file():
                deck_image_filepath = settings.NO_IMAGE_FOUND_PATH

            deck_image_file = discord.File(
                deck_image_filepath, filename=deck_image_filepath.name
            )
            submission_embed = create_team_decks_embed(deck, deck_image_filepath.name)

            await interaction.followup.send(
                embed=submission_embed, file=deck_image_file
            )
