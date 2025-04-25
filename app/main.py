from pathlib import Path

import discord
from discord.ext import commands

from app.config import settings

intents = discord.Intents.default()


class MyBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self) -> None:
        # auto-load every cog in cogs/*.py except __init__.py
        for path in Path("cogs").glob("*.py"):
            if path.stem == "__init__":
                continue
            await self.load_extension(f"cogs.{path.stem}")
        # sync slash commands once all cogs are loaded
        await self.tree.sync()


bot = MyBot()

if __name__ == "__main__":
    bot.run(settings.BOT_TOKEN)
