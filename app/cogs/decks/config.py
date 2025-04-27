from pydantic import BaseModel, Field


class DeckSettings(BaseModel):
    ADMIN_ROLES: list[int] = Field(
        default=[], description="List of admin roles for deck submission"
    )
    ALLOWED_ROLES: list[int] = Field(
        default=[], description="List of allowed roles for deck submission"
    )
    TEAM_ROLES: list[int] = Field(
        default=[], description="List of team roles for deck submission"
    )

    SESSION_TIMEOUT: int = Field(
        default=60 * 2, description="Timeout for the deck submission session in seconds"
    )
    NUMBER_OF_DECKS: int = Field(default=2, description="Number of decks to submit")


# TODO: Make roles dynamic
deck_settings = DeckSettings(
    ADMIN_ROLES=[
        1365601587795333120,  # Admin
    ],
    ALLOWED_ROLES=[
        1365601543021264936,  # Team leader
    ],
    TEAM_ROLES=[
        1365601489954930699,  # Team 1
        1365601617675685889,  # Team 2
    ],
)
