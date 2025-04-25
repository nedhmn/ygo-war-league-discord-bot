import logging
from pathlib import Path

import discord
from discord.ext import commands

from app.config import settings
from app.utils.logging import setup_logger

setup_logger("logs/bot.log")
logger = logging.getLogger("app.main")

intents = discord.Intents.default()
intents.message_content = True


class MyBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix="!", intents=intents)

    async def load_cogs(self) -> None:
        # Auto-load every cog in cogs/*.py except __init__.py
        for path in Path("app/cogs").glob("*.py"):
            if path.stem == "__init__":
                continue
            await self.load_extension(f"app.cogs.{path.stem}")
        # Sync slash commands once all cogs are loaded
        await self.tree.sync()

    async def setup_hook(self) -> None:
        await self.load_cogs()


bot = MyBot()


if __name__ == "__main__":
    bot.run(settings.BOT_TOKEN, log_handler=None)
