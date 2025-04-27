import asyncio

import discord
from discord.ext import commands
from sqlalchemy.ext.asyncio import AsyncSession

from app.cogs.decks.config import DeckSettings
from app.cogs.decks.utils import get_deck_image_buffer, has_team_submitted
from app.core.exceptions import UserCancelled, UserRetry
from app.core.models import LeagueDeck, LeagueSetting


class DeckSubmissionSession:
    def __init__(
        self,
        bot: commands.Bot,
        interaction: discord.Interaction,
        team_role: discord.Role,
        db_session: AsyncSession,
        deck_settings: DeckSettings,
        league_settings: LeagueSetting,
    ) -> None:
        self.bot = bot
        self.interaction = interaction
        self.team_role = team_role
        self.db_session = db_session
        self.deck_settings = deck_settings
        self.league_settings = league_settings
        self.dm_channel: discord.DMChannel | None = None

    async def run(self) -> list[LeagueDeck]:
        # Create dm with user
        if not self.dm_channel:
            self.dm_channel = await self.interaction.user.create_dm()

        # Check if team has submitted and confirm resubmission
        await self._deck_resubmission_handler()

        entries: list[LeagueDeck] = []

        # Collect submission
        while len(entries) < self.deck_settings.NUMBER_OF_DECKS:
            try:
                entry = await self._collect_deck_entry(len(entries) + 1)
                entries.append(entry)
            except UserRetry:
                await self.dm_channel.send("⚠️ **Let's try that deck again.**")
                continue

        await self.dm_channel.send("✅ **All decks received. Thanks!**")
        return entries

    async def _deck_resubmission_handler(self) -> None:
        assert self.dm_channel is not None

        team_submitted = await has_team_submitted(
            self.db_session, self.league_settings, self.team_role.id
        )

        if not team_submitted:
            return

        while True:
            msg = await self._ask(
                f"🔔 **Existing Submission Detected**\n"
                f"Your team **{self.team_role.name}** has already submitted decks for "
                f"Season **{self.league_settings.current_season}** and Week "
                f"**{self.league_settings.current_week}**.\n\n"
                "Do you want to update your previous submission? (yes/no)"
            )
            confirmation = msg.content.lower().strip()

            if confirmation in ("yes", "y"):
                await self.dm_channel.send("✅ **Submission update confirmed.**")
                return

            if confirmation in ("no", "n"):
                await self.dm_channel.send(
                    "🚫 **Submission update cancelled.** "
                    "Your previous submission remains unchanged."
                )
                raise UserCancelled("User chose not to update their submission.")

            await self.dm_channel.send(
                "❗ **Invalid response. Please type `yes` or `no`.**"
            )

    async def _collect_deck_entry(self, index: int) -> LeagueDeck:
        assert self.dm_channel is not None

        # Get player name and deck
        player_name = await self._get_player_name(index)
        deck_file_attachment = await self._get_deck_file_attachment()
        deck_ydk_content = await self._get_deck_ydk_content(deck_file_attachment)

        # Confirm the submission
        confirmed_deck_attachment = await self._get_confirmed_deck(
            index, player_name, deck_file_attachment, deck_ydk_content
        )

        if not isinstance(confirmed_deck_attachment, discord.Attachment):
            raise UserRetry(f"User requested to retry deck {index}.")

        return LeagueDeck(
            season=self.league_settings.current_season,
            week=self.league_settings.current_week,
            submitter_id=self.interaction.user.id,
            submitter_name=self.interaction.user.name,
            team_role_id=self.team_role.id,
            team_name=self.team_role.name,
            player_name=player_name,
            player_order=index,
            deck_filename=deck_file_attachment.filename,
            deck_ydk_url=deck_file_attachment.url,
            deck_image_url=confirmed_deck_attachment.url,
            deck_ydk_content=deck_ydk_content,
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
                    "❗ **Invalid response. Please **attach** a `.ydk` file."
                )
                continue

            attachment = file_msg.attachments[0]
            if not attachment.filename.lower().endswith(".ydk"):
                await self.dm_channel.send("❌ **Invalid file type.**\n\n")
                continue

            return attachment

    async def _get_confirmed_deck(
        self,
        index: int,
        player_name: str,
        deck_file_attachment: discord.Attachment,
        deck_ydk_content: str,
    ) -> discord.Attachment | None:
        assert self.dm_channel is not None

        await self.dm_channel.send("🔔 **Confirm Your Submission**")

        await self.dm_channel.send(
            f"> **Order:** {index}\n"
            f"> **Player Name:** {player_name}\n"
            f"> **Deck File:** {deck_file_attachment.filename}"
        )

        async with self.dm_channel.typing():
            image_buffer = await get_deck_image_buffer(deck_ydk_content)
            image_buffer.seek(0)
            deck_image_file = discord.File(image_buffer, "deck_preview.webp")

        deck_image_msg = await self.dm_channel.send(
            file=deck_image_file,
        )

        retries = 0
        max_retries = 3

        while True:
            if retries == max_retries:
                await self.dm_channel.send("❗ **Maximum number of retries met.")
                return None

            confirmation = await self._ask("Type `yes` to confirm or `no` to retry.")

            if confirmation.content.lower() in ("yes", "y"):
                return deck_image_msg.attachments[0]

            if confirmation.content.lower() in ("no", "n"):
                return None

            await self.dm_channel.send("❗ **Invalid response.**\n")
            retries += 1

    async def _ask(self, prompt: str, add_reminder: bool = True) -> discord.Message:
        assert self.dm_channel is not None
        if add_reminder:
            prompt = (
                prompt + "\n\n"
                f"(Type `cancel` to abort. You have "
                f"{self.deck_settings.SESSION_TIMEOUT // 60} minute(s) for this step.)"
            )

        await self.dm_channel.send(prompt)

        try:
            msg: discord.Message = await self.bot.wait_for(
                "message",
                check=lambda m: (
                    m.author == self.interaction.user
                    and isinstance(m.channel, discord.DMChannel)
                ),
                timeout=self.deck_settings.SESSION_TIMEOUT,
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

    async def _get_deck_ydk_content(self, attachment: discord.Attachment) -> str:
        file_bytes = await attachment.read()
        return file_bytes.decode("utf-8")
