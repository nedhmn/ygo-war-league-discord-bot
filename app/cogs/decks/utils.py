from app.core.db import get_async_db_session
from app.core.models import LeagueDeck


async def load_league_decks_to_db(entries: list[LeagueDeck]) -> None:
    async with get_async_db_session() as session:
        session.add_all(entries)
        await session.commit()
