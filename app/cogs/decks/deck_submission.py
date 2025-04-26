import asyncio

import discord
from discord.ext import commands
from sqlalchemy.ext.asyncio import AsyncSession

from app.cogs.decks.config import DeckSettings
from app.core.exceptions import UserCancelled, UserRetry
from app.core.models import LeagueDeck


class DeckSubmissionSession:
    def __init__(
        self,
        bot: commands.Bot,
        user: discord.User | discord.Member,
        db_session: AsyncSession,
        settings: DeckSettings,
    ) -> None:
        self.bot = bot
        self.user = user
        self.db_session = db_session
        self.settings = settings
        self.dm_channel: discord.DMChannel | None = None

    async def run(self) -> list[LeagueDeck]:
        if not self.dm_channel:
            self.dm_channel = await self.user.create_dm()

        entries: list[LeagueDeck] = []

        while len(entries) < self.settings.NUMBER_OF_DECKS:
            try:
                entry = await self._collect_deck_entry(len(entries) + 1)
                entries.append(entry)
            except UserRetry:
                await self.dm_channel.send("⚠️ **Let's try that deck again.**")
                continue

        await self.dm_channel.send("✅ **All decks received. Thanks!**")
        return entries

    async def _collect_deck_entry(self, index: int) -> LeagueDeck:
        assert self.dm_channel is not None

        # Prompt for the player's name
        player_name = await self._get_player_name(index)

        # Prompt for the .ydk file
        deck_file_attachment = await self._get_deck_file_attachment()

        # Confirm the submission
        if not await self._get_confirmation(index, player_name, deck_file_attachment):
            raise UserRetry(f"User requested to retry deck {index}.")

        # Preparing league_decks entry
        deck_contents = await self._get_deck_ydk_contents(deck_file_attachment)

        # TODO: league_team_id should be fetched from the league teams table
        return LeagueDeck(
            league_team_id="dummy_team_role_id",
            submitter_id=self.user.id,
            submitter_name=self.user.name,
            player_name=player_name,
            player_order=index,
            deck_filename=deck_file_attachment.filename,
            deck_url=deck_file_attachment.url,
            deck_ydk_contents=deck_contents,
        )

    async def _get_player_name(self, index: int) -> str:
        assert self.dm_channel is not None

        msg = await self._ask(f"**Deck {index}**\nPlease enter the **player's name**.")
        return msg.content.strip()

    async def _get_deck_file_attachment(self) -> discord.Attachment:
        assert self.dm_channel is not None
        while True:
            file_msg = await self._ask(
                "📎 **Upload your deck file**\nPlease attach your `.ydk` file."
            )

            if not file_msg.attachments:
                await self.dm_channel.send(
                    "❗ Please **attach** a `.ydk` file. Text messages alone won't work."
                )
                continue

            attachment = file_msg.attachments[0]
            if not attachment.filename.lower().endswith(".ydk"):
                await self.dm_channel.send("❌ **Invalid file type.**\n\n")
                continue

            return attachment

    async def _get_confirmation(
        self, index: int, player_name: str, deck_file_attachment: discord.Attachment
    ) -> bool:
        assert self.dm_channel is not None
        while True:
            confirmation = await self._ask(
                "🔔 **Confirm Your Submission**\n"
                f"> **Order:** {index}\n"
                f"> **Player Name:** {player_name}\n"
                f"> **Deck File:** {deck_file_attachment.filename}\n\n"
                "Type `yes` to confirm or `no` to retry."
            )

            if confirmation.content.lower() in ("yes", "y"):
                return True

            if confirmation.content.lower() in ("no", "n"):
                return False

            await self.dm_channel.send("❗ **Invalid response.**\n")

    async def _ask(self, prompt: str, add_reminder: bool = True) -> discord.Message:
        assert self.dm_channel is not None
        if add_reminder:
            prompt = (
                prompt + "\n\n"
                f"(Type `cancel` to abort. You have "
                f"{self.settings.SESSION_TIMEOUT // 60} minute(s) for this step.)"
            )

        await self.dm_channel.send(prompt)

        try:
            msg: discord.Message = await self.bot.wait_for(
                "message",
                check=lambda m: (
                    m.author == self.user and isinstance(m.channel, discord.DMChannel)
                ),
                timeout=self.settings.SESSION_TIMEOUT,
            )
        except asyncio.TimeoutError:
            await self.dm_channel.send(
                "⌛ **Session timed out.** Due to inactivity, the process has ended. "
                "Please start again when you are ready."
            )
            raise

        if msg.content.lower().strip() == "cancel":
            await self.dm_channel.send(
                "🚫 **Submission cancelled.** You can start the process again anytime."
            )
            raise UserCancelled

        return msg

    async def _get_deck_ydk_contents(self, attachment: discord.Attachment) -> str:
        file_bytes = await attachment.read()
        return file_bytes.decode("utf-8")
