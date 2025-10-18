# Do not modify the modules to include a dot at the beginning, as this will break imports.
import ollama

from .ai_config import OLLAMA_MODEL
from .models import Player

CLIENT = ollama.AsyncClient()


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
    print(f"Generating initial story. Prompt used for generation: {prompt}")
    response = await CLIENT.generate(
        model=OLLAMA_MODEL, prompt=prompt, stream=False, options={"num_ctx": 16384}, keep_alive=360
    )
    return response["response"]


async def process_turn(
    game_state: str, players: list[Player], player_actions: list[tuple[str, str]]
) -> str:
    prompt = f"Current game state: {game_state}\n\n"
    for player_id, action in player_actions:
        player = next((p for p in players if p.id == player_id), None)
        if player:
            prompt += f"{player.name} the {player.player_class} wants to: {action}\n"
    prompt += (
        "\nUpdate the game state based on the players' actions, describing it from the players' "
        "perspective. Act the role of any non-player "
        "characters as needed. Keep the story engaging and coherent. Keep the plot challenging, "
        "acting as any antagonists or obstacles the players may face."
    )
    print(f"Processing turn, prompt: {prompt}")
    response = await CLIENT.generate(
        model=OLLAMA_MODEL, prompt=prompt, stream=False, options={"num_ctx": 16384}, keep_alive=360
    )
    return response["response"]
