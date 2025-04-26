import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase


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


class LeagueDeck(BaseModel):
    __tablename__ = "league_decks"

    season = Column(Integer, nullable=False)
    week = Column(Integer, nullable=False)
    submitter_id = Column(Integer, nullable=False)
    submitter_name = Column(String, nullable=False)
    team_role_id = Column(Integer, nullable=False)
    team_name = Column(String, nullable=False)
    player_name = Column(String, nullable=False)
    player_order = Column(Integer, nullable=False)
    deck_filename = Column(String, nullable=False)
    deck_url = Column(String, nullable=False)
    deck_ydk_contents = Column(String, nullable=False)
