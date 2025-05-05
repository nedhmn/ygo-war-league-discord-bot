import logging

import discord

logger = logging.getLogger(__name__)


class MyCommandTree(discord.app_commands.CommandTree):
    """
    App commands tree class
    ref: https://discordpy.readthedocs.io/en/stable/interactions/api.html?highlight=app_commands#commandtree
    """

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        """App commands error handler"""
        logger.exception("An error occured:")

        if isinstance(error, discord.app_commands.errors.MissingAnyRole):
            message = "❌ You don't have the required role to use this command."
        elif isinstance(error, discord.app_commands.errors.NoPrivateMessage):
            message = "❌ This command cannot be used in DMs."
        else:
            message = "❌ An unexpected error occurred."

        if interaction.response.is_done():
            await interaction.followup.send(message)
        else:
            await interaction.response.send_message(message)
