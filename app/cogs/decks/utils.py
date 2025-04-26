from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import LeagueDeck, LeagueSetting


async def update_league_season(db_session: AsyncSession, new_season: int) -> None:
    result = await db_session.execute(select(LeagueSetting))
    league_setting = result.scalar_one_or_none()
    league_setting.current_season = new_season

    await db_session.commit()


async def update_league_week(db_session: AsyncSession, new_week: int) -> None:
    result = await db_session.execute(select(LeagueSetting))
    league_setting = result.scalar_one_or_none()
    league_setting.current_week = new_week

    await db_session.commit()


async def update_league_deck_submission_status(
    db_session: AsyncSession, new_enable: bool
) -> None:
    result = await db_session.execute(select(LeagueSetting))
    league_setting = result.scalar_one_or_none()
    league_setting.enable_deck_submissions = new_enable

    await db_session.commit()


async def get_league_settings(db_session: AsyncSession) -> LeagueSetting:
    result = await db_session.execute(select(LeagueSetting))
    return result.scalar_one()


async def load_league_decks_to_db(
    entries: list[LeagueDeck], db_session: AsyncSession
) -> None:
    db_session.add_all(entries)
    await db_session.commit()
