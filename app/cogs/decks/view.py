from typing import Any

import discord


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
        value = self.values[0]
        # Here you can trigger the next dynamic select or process the choice.
        await interaction.response.send_message(
            f"You selected season: {value}", ephemeral=True
        )


class WeekSelectView(discord.ui.View):
    pass


class WeekSelect(discord.ui.Select[Any]):
    pass


class TeamSelectView(discord.ui.View):
    pass


class TeamSelect(discord.ui.Select[Any]):
    pass
