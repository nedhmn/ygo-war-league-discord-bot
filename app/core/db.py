from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# Create the async engine and sessionmaker
engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()


async def init_db() -> None:
    """Creates the database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
