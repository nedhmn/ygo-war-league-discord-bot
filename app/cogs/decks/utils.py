from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import LeagueDeck, LeagueSetting


async def get_league_settings(db_session: AsyncSession) -> LeagueSetting | None:
    result = await db_session.execute(select(LeagueSetting))
    return result.scalar_one_or_none()


async def load_league_decks_to_db(
    entries: list[LeagueDeck], db_session: AsyncSession
) -> None:
    db_session.add_all(entries)
    await db_session.commit()
