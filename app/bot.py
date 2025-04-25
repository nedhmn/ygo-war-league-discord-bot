from pathlib import Path

import discord
from discord.ext import commands

from app.core.db import init_db

# Intents
intents = discord.Intents.default()
intents.message_content = True


class MyBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix="!", intents=intents)

    async def load_cogs(self) -> None:
        # Load all cogs from the app/cogs directory
        for folder in Path("app/cogs").iterdir():
            if not folder.is_dir():
                continue
            # Cogs need to follow path structure app/cogs/foo/foo.py
            file = folder / f"{folder.name}.py"
            if not file.exists():
                continue
            await self.load_extension(f"app.cogs.{folder.name}.{folder.name}")

    async def setup_hook(self) -> None:
        await init_db()
        await self.load_cogs()
