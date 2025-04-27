from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DecklistProcessorSetting(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    CARD_IMAGE_BASE_URL: str = Field(description="The base url for card images")
    CARD_IMAGE_FORMAT: str = Field(description="The card image format - eg. .png")


decklist_processor_settings = DecklistProcessorSetting()


class DeckImagerSetting(BaseModel):
    CARD_SIZE: tuple[int, int] = Field(description="Resize cards to these dimensions")
    DECK_SPACING: int = Field(description="Spacing between main, side, and extra decks")
    IMAGE_QUALITY: int = Field(description="Quality of the final composition image")
    IMAGE_FORMAT: str = Field(description="Image type")


deck_imager_settings = DeckImagerSetting(
    CARD_SIZE=(60, 84), DECK_SPACING=10, IMAGE_QUALITY=80, IMAGE_FORMAT="WEBP"
)
