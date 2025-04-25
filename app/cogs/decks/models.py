from datetime import datetime

from pydantic import BaseModel


class DeckEntry(BaseModel):
    season: int
    week: int
    submitter_id: int
    submitter_name: str
    player_name: str
    player_order: int
    deck_filename: str
    deck_url: str
    created_at: datetime
