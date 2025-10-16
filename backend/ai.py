import httpx

OLLAMA_API_URL = "http://localhost:11434/api/generate"

async def generate_initial_story(scenario: str) -> str:
    prompt = f"You are a text adventure game master. The scenario is: {scenario}. Describe the starting situation to the players."
    async with httpx.AsyncClient() as client:
        response = await client.post(
            OLLAMA_API_URL,
            json={"model": "llama2", "prompt": prompt, "stream": False},
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
            json={"model": "llama2", "prompt": prompt, "stream": False},
            timeout=60.0,
        )
        response.raise_for_status()
        return response.json()["response"]