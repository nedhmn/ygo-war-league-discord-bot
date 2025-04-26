from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    BOT_TOKEN: str
    DATABASE_URL: str
    ALLOWED_GUILDS: list[int] = Field(
        default=[], description="List of allowed guild IDs"
    )


# TODO: Make this dynamic and with guild name
settings = Settings(ALLOWED_GUILDS=[1364794587704594462])
