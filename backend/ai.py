import httpx
from ai_config import OLLAMA_API_URL, OLLAMA_MODEL


async def generate_initial_story(scenario: str) -> str:
    prompt = (
        f"You are a text adventure game master. The scenario is: {scenario}. "
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


async def process_turn(game_state: str, player_actions: list[str]) -> str:
    prompt = f"Current game state: {game_state}\n\n"
    for action in player_actions:
        prompt += f"A player wants to: {action}\n"
    prompt += "\nUpdate the game state based on the players' actions."

    async with httpx.AsyncClient() as client:
        response = await client.post(
            OLLAMA_API_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=60.0,
        )
        response.raise_for_status()
        return response.json()["response"]
