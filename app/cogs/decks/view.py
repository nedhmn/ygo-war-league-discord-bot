from typing import Any

import discord

from app.cogs.decks.utils import get_available_weeks_by_season
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
            discord.SelectOption(label=week, value=week) for week in available_weeks
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

        await interaction.response.send_message(
            f"Selected week is {selected_week} and season is {self.season}",
            ephemeral=True,
        )


class TeamSelectView(discord.ui.View):
    pass


class TeamSelect(discord.ui.Select[Any]):
    pass
