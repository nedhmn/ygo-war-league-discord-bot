from pydantic import BaseModel, Field


class DeckImagerSetting(BaseModel):
    card_size: tuple[int, int] = Field(description="Resize cards to these dimensions")
    spacing: int = Field(description="Spacing between main, side, and extra decks")
    quality: int = Field(description="Quality of the final composition image")
    format: str = Field(description="Image type")


deck_imager_settings = DeckImagerSetting(
    card_size=(60, 84), spacing=10, quality=80, format="WEBP"
)
