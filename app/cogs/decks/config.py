from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict
from app.core.config import settings


class DeckSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    ADMIN_ROLES: Annotated[list[int], NoDecode] = Field(
        description="List of admin roles for deck submission",
    )
    ALLOWED_ROLES: Annotated[list[int], NoDecode] = Field(
        description="List of allowed roles for deck submission",
    )
    TEAM_ROLES: Annotated[list[int], NoDecode] = Field(
        description="List of team roles for deck submission",
    )

    # Set roles in env as csv and parse as list
    # ref: https://docs.pydantic.dev/latest/concepts/pydantic_settings/#disabling-json-parsing
    @field_validator("ADMIN_ROLES", "ALLOWED_ROLES", "TEAM_ROLES", mode="before")
    @classmethod
    def parse_csv_to_list(cls, v: str) -> list[int]:
        return [int(x) for x in v.split(",")]

    SESSION_TIMEOUT: int = Field(
        default=60 * 2, description="Timeout for the deck submission session in seconds"
    )
    NUMBER_OF_DECKS: int = Field(default=5, description="Number of decks to submit")


deck_settings = DeckSettings()

if settings.ENVIORNMENT == "local":
    deck_settings.NUMBER_OF_DECKS = 2
