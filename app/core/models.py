import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )  # Sqlite doesn't support UUIDs
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class LeagueSetting(BaseModel):
    __tablename__ = "league_settings"

    current_season: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_week: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    enable_deck_submissions: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )


class LeagueDeck(BaseModel):
    __tablename__ = "league_decks"

    season: Mapped[int] = mapped_column(Integer, nullable=False)
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    submitter_id: Mapped[int] = mapped_column(Integer, nullable=False)
    submitter_name: Mapped[str] = mapped_column(String, nullable=False)
    team_role_id: Mapped[int] = mapped_column(Integer, nullable=False)
    team_name: Mapped[str] = mapped_column(String, nullable=False)
    player_name: Mapped[str] = mapped_column(String, nullable=False)
    player_order: Mapped[int] = mapped_column(Integer, nullable=False)
    deck_filename: Mapped[str] = mapped_column(String, nullable=False)
    deck_ydk_url: Mapped[str] = mapped_column(String)
    deck_image_url: Mapped[str] = mapped_column(String)
    deck_ydk_content: Mapped[str] = mapped_column(String, nullable=False)
