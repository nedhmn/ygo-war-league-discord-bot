import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    id = Column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )  # Sqlite doesn't support UUIDs
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )


class LeagueSetting(BaseModel):
    __tablename__ = "league_settings"

    current_season = Column(Integer, nullable=False, default=0)
    current_week = Column(Integer, nullable=False, default=0)


class LeagueTeam(BaseModel):
    __tablename__ = "league_teams"

    season = Column(Integer, nullable=False)
    team_role_id = Column(Integer, nullable=False)
    team_name = Column(String, nullable=False)

    league_decks = relationship("LeagueDeck", back_populates="league_teams")


class LeagueDeck(BaseModel):
    __tablename__ = "league_decks"

    league_team_id = Column(String, ForeignKey("league_teams.id"), nullable=False)
    submitter_id = Column(Integer, nullable=False)
    submitter_name = Column(String, nullable=False)
    player_name = Column(String, nullable=False)
    player_order = Column(Integer, nullable=False)
    deck_filename = Column(String, nullable=False)
    deck_url = Column(String, nullable=False)
    deck_ydk_contents = Column(String, nullable=False)

    league_teams = relationship("LeagueTeam", back_populates="league_decks")
