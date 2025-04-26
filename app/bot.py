from pathlib import Path

import discord
from discord.ext import commands

from app.core.db import async_engine
from app.core.models import Base
from app.tree import MyCommandTree

# Intents
intents = discord.Intents.default()
intents.message_content = True


class MyBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix="!", intents=intents, tree_cls=MyCommandTree)

    @staticmethod
    async def init_db() -> None:
        """Creates the database tables"""
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def load_cogs(self) -> None:
        """Loads cogs from the app/cogs directory"""
        for folder in Path("app/cogs").iterdir():
            if not folder.is_dir():
                continue
            # Cogs need to follow path structure app/cogs/foo/foo.py
            file = folder / f"{folder.name}.py"
            if not file.exists():
                continue
            await self.load_extension(f"app.cogs.{folder.name}.{folder.name}")

    async def setup_hook(self) -> None:
        await self.init_db()
        await self.load_cogs()
