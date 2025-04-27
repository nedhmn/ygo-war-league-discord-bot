from pathlib import Path

import discord
from discord.ext import commands
from sqlalchemy import select

from app.core.db import async_engine, get_async_db_session
from app.core.models import Base, LeagueSetting
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

    @staticmethod
    async def init_league_setting() -> None:
        """Insert a default LeagueSetting record if none exists"""
        async with get_async_db_session() as session:
            result = await session.execute(select(LeagueSetting))

            if result.scalar_one_or_none() is None:
                session.add(LeagueSetting())
                await session.commit()

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
        await self.init_league_setting()
        await self.load_cogs()

    async def on_ready(self) -> None:
        await self.tree.sync()
