import ollama
from typing import List, Tuple
from .models import Player

# Use a synchronous client for simplicity in this example
CLIENT = ollama.Client()

async def generate_initial_story(scenario: str, players: List[Player]) -> str:
    """
    Generates the initial story based on the given scenario and players.
    """
    return f"This is a mock initial story for the scenario: {scenario}"

async def process_turn(game_state: str, players: List[Player], player_actions: List[Tuple[str, str]]) -> str:
    """
    Processes a turn by sending the game state and player actions to the AI
    and returning the new story segment.
    """
    return "This is a mock story segment."