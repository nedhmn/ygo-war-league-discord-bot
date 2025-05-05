import io
from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class ConfirmationDetails:
    url: str
    image_bytes: io.BytesIO


class TeamPlayer(BaseModel):
    player_order: int
    player_name: str


class TeamMatchup(BaseModel):
    team_role_id: int
    team_name: str
    players: list[TeamPlayer] = []
