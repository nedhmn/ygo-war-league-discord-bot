import asyncio
from typing import Any, Callable

import discord
from discord.ext import commands

from app.cogs.decks.config import DeckSettings
from app.core.exceptions import UserCancelled, UserRetry
from app.core.models import LeagueDeck


class DeckSubmissionSession:
    def __init__(
        self,
        bot: commands.Bot,
        user: discord.User | discord.Member,
        settings: DeckSettings,
    ) -> None:
        self.bot = bot
        self.user = user
        self.settings = settings
        self.dm_channel: discord.DMChannel | None = None
        self.entries: list[LeagueDeck] = []

    async def run(self) -> list[LeagueDeck]:
        await self._ensure_dm()
        assert self.dm_channel is not None

        while len(self.entries) < self.settings.NUMBER_OF_DECKS:
            try:
                entry = await self._collect_deck_entry(len(self.entries) + 1)
                self.entries.append(entry)
            except UserRetry:
                await self.dm_channel.send("⚠️ **Let's try that deck again.**")
                continue

        await self.dm_channel.send("✅ **All decks received. Thanks!**")
        return self.entries

    async def _ensure_dm(self) -> None:
        if not self.dm_channel:
            self.dm_channel = await self.user.create_dm()

    async def _collect_deck_entry(self, index: int) -> LeagueDeck:
        assert self.dm_channel is not None

        # Prompt for the player's name
        name_msg = await self._ask(
            f"**Deck {index}**\nPlease enter the **player's name**.",
            lambda m: bool(m.content.strip()),
        )
        name = name_msg.content.strip()

        # Prompt for the .ydk file
        while True:
            file_msg = await self._ask(
                "**Upload your deck file**\nPlease attach your `.ydk` file.",
                lambda m: True,  # Accepts any message
            )

            if not file_msg.attachments:
                await self.dm_channel.send(
                    "❗ Please **attach** a `.ydk` file. Text messages alone won't work."
                )
                continue

            attachment = file_msg.attachments[0]
            if attachment.filename.lower().endswith(".ydk"):
                break

            await self.dm_channel.send(
                "❌ **Invalid file type.** Your file must end with `.ydk`. "
                "Please try again or type `cancel`."
            )

        confirmation = await self._ask(
            f"**Confirm Your Submission**\n"
            f"> **Player Name:** {name}\n"
            f"> **Deck File:** {attachment.filename}\n\n"
            "Type `yes` to confirm or `no` to retry.",
            lambda m: m.content.lower().strip() in {"yes", "no", "y", "n"},
        )

        if not confirmation.content.lower().startswith("y"):
            raise UserRetry(f"User requested to retry deck {index}.")

        # Preparing league_decks entry
        deck_contents = await self._get_deck_ydk_contents(attachment)

        # TODO: Better solution for season and week
        return LeagueDeck(
            season=1,
            week=1,
            submitter_id=self.user.id,
            submitter_name=self.user.name,
            team_name="team_name",
            player_name=name,
            player_order=index,
            deck_filename=attachment.filename,
            deck_url=attachment.url,
            deck_ydk_contents=deck_contents,
        )

    async def _ask(self, prompt: str, check: Callable[[discord.Message], bool]) -> Any:
        await self._ensure_dm()
        assert self.dm_channel is not None

        await self.dm_channel.send(
            f"{prompt}\n\n"
            f"(Type `cancel` to abort. You have {self.settings.SESSION_TIMEOUT // 60} "
            "minutes for this step.)"
        )
        try:
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: (
                    m.author == self.user
                    and isinstance(m.channel, discord.DMChannel)
                    and check(m)
                ),
                timeout=self.settings.SESSION_TIMEOUT,
            )
        except asyncio.TimeoutError:
            await self.dm_channel.send(
                "⌛ **Session timed out.** Due to inactivity, the process "
                "has ended. Please start again when you are ready."
            )
            raise

        if msg.content.lower().strip() == "cancel":
            await self.dm_channel.send(
                "🚫 **Submission cancelled.** You can start the process again anytime."
            )
            raise UserCancelled("User cancelled the session")

        return msg

    async def _get_deck_ydk_contents(self, attachment: discord.Attachment) -> str:
        file_bytes = await attachment.read()
        return file_bytes.decode("utf-8")
