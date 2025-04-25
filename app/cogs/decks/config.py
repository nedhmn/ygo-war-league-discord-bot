from pydantic import BaseModel, Field


class DeckSettings(BaseModel):
    SESSION_TIMEOUT: int = Field(
        default=300, description="Timeout for the deck submission session in seconds"
    )
    NUMBER_OF_DECKS: int = Field(default=1, description="Number of decks to submit")


deck_settings = DeckSettings()
