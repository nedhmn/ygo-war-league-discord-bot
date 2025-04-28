from typing import Any

import discord


class BaseSelectView(discord.ui.View):
    def __init__(self, initiated_user: int) -> None:
        super().__init__()
        self.initiated_user = initiated_user

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.initiated_user:
            await interaction.response.send_message(
                content="🚫 Only the user who initiated the command can make a selection!",
                ephemeral=True,
            )
            return False

        return True


class BaseSelect(discord.ui.Select[Any]):
    async def disable_view(self, interaction: discord.Interaction) -> None:
        self.disabled = True
        await interaction.response.edit_message(view=self.view)
