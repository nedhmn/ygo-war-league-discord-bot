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


class LeagueDeck(BaseModel):
    __tablename__ = "league_decks"

    season = Column(Integer)
    week = Column(Integer)
    submitter_id = Column(Integer)
    submitter_name = Column(String)
    team_name = Column(String)
    player_name = Column(String)
    player_order = Column(Integer)
    deck_filename = Column(String)
    deck_url = Column(String)
    deck_ydk_contents = Column(String)
