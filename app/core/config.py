from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    ENVIORNMENT: Literal["local", "production"] = Field(default="local")
    BOT_TOKEN: str
    DATABASE_URL: str
    NO_IMAGE_FOUND_PATH: Path = Field(description="Path for no-image-found image")


settings = Settings(NO_IMAGE_FOUND_PATH=Path("data/no-image.webp"))
