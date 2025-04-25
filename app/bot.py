from pathlib import Path

import discord
from discord.ext import commands

# Intents
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
