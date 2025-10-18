from typing import List, Optional

from pydantic import BaseModel


class Player(BaseModel):
    id: str
    name: str
    player_class: str
    is_host: bool = False
    is_alive: bool = True


class Turn(BaseModel):
    player_id: str
    action: str


class Game(BaseModel):
    id: str
    scenario: str
    players: List[Player] = []
    turns: List[Turn] = []
    current_round_actions: List[Turn] = []
    password: Optional[str] = None  # For protecting the game
    status: str = "pending"  # pending, in_progress, finished
    current_player_index: int = 0
