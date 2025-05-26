import io
from typing import Sequence

import aiofiles
import discord
from sqlalchemy import delete, distinct, exists, select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.cogs.decks.models import TeamMatchup, TeamPlayer
from app.core.deck_imager.config import (
    deck_imager_settings,
    decklist_processor_settings,
)
from app.core.deck_imager.deck_imager import DeckImager
from app.core.deck_imager.decklist_processor import DecklistProcessor
from app.core.models import LeagueDeck, LeagueSetting


async def update_league_season(db_session: AsyncSession, new_season: int) -> None:
    result = await db_session.execute(select(LeagueSetting))
    league_setting = result.scalar_one()
    league_setting.current_season = new_season

    await db_session.commit()


async def update_league_week(db_session: AsyncSession, new_week: int) -> None:
    result = await db_session.execute(select(LeagueSetting))
    league_setting = result.scalar_one()
    league_setting.current_week = new_week

    await db_session.commit()


async def update_league_deck_submission_status(
    db_session: AsyncSession, new_enable: bool
) -> None:
    result = await db_session.execute(select(LeagueSetting))
    league_setting = result.scalar_one()
    league_setting.enable_deck_submissions = new_enable

    await db_session.commit()


async def get_league_settings(db_session: AsyncSession) -> LeagueSetting:
    result = await db_session.execute(select(LeagueSetting))
    return result.scalar_one()


async def has_team_submitted(
    db_session: AsyncSession, league_settings: LeagueSetting, team_id: int
) -> bool:
    stmt = select(
        exists().where(
            LeagueDeck.season == league_settings.current_season,
            LeagueDeck.week == league_settings.current_week,
            LeagueDeck.team_role_id == team_id,
        )
    )
    result = await db_session.execute(stmt)
    return bool(result.scalar())


async def load_league_decks_to_db(
    entries: list[LeagueDeck], db_session: AsyncSession
) -> None:
    season = entries[0].season
    week = entries[0].week
    team_role_id = entries[0].team_role_id

    # Delete previous entries that match the season, week, and team_role_id
    await db_session.execute(
        delete(LeagueDeck).where(
            LeagueDeck.season == season,
            LeagueDeck.week == week,
            LeagueDeck.team_role_id == team_role_id,
        )
    )

    db_session.add_all(entries)
    await db_session.commit()


async def get_deck_image_buffer(deck_ydk_content: str) -> io.BytesIO:
    # Initialize processors
    decklist_processor = DecklistProcessor(decklist_processor_settings)
    deck_imager = DeckImager(deck_imager_settings)

    decklist = decklist_processor.create_decklist(deck_ydk_content)
    return await deck_imager.generate_deck_image(decklist)


async def save_deck_image(image_bytes: io.BytesIO, filename: str) -> None:
    """Save deck image locally"""
    async with aiofiles.open(filename, "wb") as f:
        await f.write(image_bytes.getvalue())


async def get_available_seasons(db_session: AsyncSession) -> Sequence[int]:
    unique_seasons = await db_session.execute(select(distinct(LeagueDeck.season)))
    return unique_seasons.scalars().all()


async def get_available_weeks_by_season(
    db_session: AsyncSession, season: int
) -> Sequence[int]:
    unique_weeks = await db_session.execute(
        select(distinct(LeagueDeck.week)).where(LeagueDeck.season == season)
    )
    return unique_weeks.scalars().all()


async def get_available_teams_by_season_and_week(
    db_session: AsyncSession, season: int, week: int
) -> Sequence[str]:
    unique_teams = await db_session.execute(
        select(distinct(LeagueDeck.team_name)).where(
            LeagueDeck.season == season, LeagueDeck.week == week
        )
    )
    return unique_teams.scalars().all()


async def get_team_submission_by_season_and_week(
    db_session: AsyncSession, season: int, week: int, team_name: str
) -> Sequence[LeagueDeck]:
    team_submission = await db_session.execute(
        select(LeagueDeck)
        .where(
            LeagueDeck.season == season,
            LeagueDeck.week == week,
            LeagueDeck.team_name == team_name,
        )
        .order_by(LeagueDeck.player_order)
    )
    return team_submission.scalars().all()


def create_team_decks_embed(
    deck: LeagueDeck, deck_image_filename: str
) -> discord.Embed:
    embed = discord.Embed(title="Deck Submission", color=discord.Color.blurple())

    embed.description = (
        f"**Season:** {deck.season}\n"
        f"**Week:** {deck.week}\n"
        f"**Submitter:** {deck.submitter_name}\n"
        f"**Team:** {deck.team_name}"
    )

    embed.add_field(
        name="Player Deck",
        value=(f"**Order:** {deck.player_order}\n**Player:** {deck.player_name}"),
        inline=False,
    )

    embed.set_image(url=f"attachment://{deck_image_filename}")

    return embed


async def get_submitted_teams(
    db_session: AsyncSession, league_settings: LeagueSetting
) -> Sequence[Row[tuple[int, str]]]:
    result = await db_session.execute(
        select(LeagueDeck.team_role_id, LeagueDeck.team_name)
        .filter(
            LeagueDeck.season == league_settings.current_season,
            LeagueDeck.week == league_settings.current_week,
        )
        .distinct(LeagueDeck.team_role_id)
        .order_by(LeagueDeck.team_name)
    )

    return result.all()


async def get_team_matchups(
    db_session: AsyncSession, season: int, week: int
) -> Sequence[Row[tuple[int, str, int, str]]]:
    result = await db_session.execute(
        select(
            LeagueDeck.team_role_id,
            LeagueDeck.team_name,
            LeagueDeck.player_order,
            LeagueDeck.player_name,
        )
        .where(LeagueDeck.season == season, LeagueDeck.week == week)
        .order_by(LeagueDeck.team_name, LeagueDeck.player_order)
    )

    return result.all()


def group_team_matchups(
    team_matchups: Sequence[Row[tuple[int, str, int, str]]],
) -> dict[int, TeamMatchup]:
    teams: dict[int, TeamMatchup] = {}
    for team_role_id, team_name, player_order, player_name in team_matchups:
        if team_role_id not in teams:
            teams[team_role_id] = TeamMatchup(
                team_role_id=team_role_id, team_name=team_name, players=[]
            )
        teams[team_role_id].players.append(
            TeamPlayer(player_order=player_order, player_name=player_name)
        )
    return teams


def create_team_matchups_embed(
    team_role_id: int, teams: dict[int, TeamMatchup], interaction: discord.Interaction
) -> discord.Embed:
    if team_role_id in teams:
        team_matchup = teams[team_role_id]
        sorted_players = sorted(team_matchup.players, key=lambda x: x.player_order)
        player_lines = "\n".join(
            f"{player.player_order}. {player.player_name}" for player in sorted_players
        )
        embed = discord.Embed(
            title=f"Team {team_matchup.team_name}",
            description=player_lines,
            color=discord.Color.blurple(),
        )
    else:
        assert isinstance(interaction.guild, discord.Guild)
        team_role = interaction.guild.get_role(team_role_id)
        team_name = team_role.name if team_role else "Unknown"
        embed = discord.Embed(
            title=f"Team {team_name}",
            description="No submissions!",
            color=discord.Color.red(),
        )

    return embed
