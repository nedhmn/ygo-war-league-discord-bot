from pydantic import BaseModel, Field


class DeckSettings(BaseModel):
    ALLOWED_ROLES: list[int] = Field(
        default=[], description="List of allowed roles for deck submission"
    )

    SESSION_TIMEOUT: int = Field(
        default=60 * 1, description="Timeout for the deck submission session in seconds"
    )
    NUMBER_OF_DECKS: int = Field(default=1, description="Number of decks to submit")


deck_settings = DeckSettings(
    ALLOWED_ROLES=[
        1365601587795333120,  # Admin
        1365601543021264936,  # Team leader
    ]
)
