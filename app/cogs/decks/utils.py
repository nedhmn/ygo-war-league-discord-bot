from typing import Sequence

from sqlalchemy import select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import LeagueDeck, LeagueSetting, LeagueTeam


async def get_league_settings(db_session: AsyncSession) -> LeagueSetting:
    result = await db_session.execute(select(LeagueSetting))
    return result.scalar_one()


async def get_league_teams_by_season(
    season: int, db_session: AsyncSession
) -> Sequence[Row[tuple[int, str]]]:
    result = await db_session.execute(
        select(LeagueTeam.team_role_id, LeagueTeam.team_name).where(
            LeagueTeam.season == season
        )
    )
    return result.all()


async def load_league_decks_to_db(
    entries: list[LeagueDeck], db_session: AsyncSession
) -> None:
    db_session.add_all(entries)
    await db_session.commit()
