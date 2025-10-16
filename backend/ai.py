import httpx
from .ai_config import OLLAMA_API_URL, OLLAMA_MODEL
from .models import Player


async def generate_initial_story(scenario: str, players: list[Player]) -> str:
    player_descriptions = "\n".join(
        [f"- {player.name} the {player.player_class}" for player in players]
    )
    prompt = (
        f"You are a text adventure game master. The scenario is: {scenario}. "
        "The players are:\n"
        f"{player_descriptions}\n"
        "Describe the starting situation to the players. "
        "Let the players choose their actions freely, without giving options."
    )
    async with httpx.AsyncClient() as client:
        response = await client.post(
            OLLAMA_API_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=60.0,
        )
        response.raise_for_status()
        return response.json()["response"]


async def process_turn(
    game_state: str, players: list[Player], player_actions: list[tuple[str, str]]
) -> str:
    prompt = f"Current game state: {game_state}\n\n"
    for player_id, action in player_actions:
        player = next((p for p in players if p.id == player_id), None)
        if player:
            prompt += f"{player.name} the {player.player_class} wants to: {action}\n"
    prompt += "\nUpdate the game state based on the players' actions."

    async with httpx.AsyncClient() as client:
        response = await client.post(
            OLLAMA_API_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=60.0,
        )
        response.raise_for_status()
        return response.json()["response"]
