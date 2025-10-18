import uuid
import json
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .ai import generate_initial_story, process_turn
from .models import Game, Player, Turn

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

games: Dict[str, Game] = {}


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, game_id: str):
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        self.active_connections[game_id].append(websocket)

    def disconnect(self, websocket: WebSocket, game_id: str):
        self.active_connections[game_id].remove(websocket)

    async def broadcast(self, message: dict, game_id: str):
        if game_id in self.active_connections:
            for connection in self.active_connections[game_id]:
                await connection.send_text(json.dumps(message))


manager = ConnectionManager()


class CreateGameRequest(BaseModel):
    scenario: str
    player_name: str
    player_class: str
    password: Optional[str] = None


@app.post("/game")
async def create_game(request: CreateGameRequest):
    game_id = str(uuid.uuid4())
    game = Game(
        id=game_id, scenario=request.scenario, password=request.password
    )
    games[game_id] = game
    player_id = str(uuid.uuid4())
    player = Player(
        id=player_id, name=request.player_name, player_class=request.player_class, is_host=True
    )
    game.players.append(player)
    # The host doesn't connect to the websocket until after this request is complete,
    # so we can't broadcast to them. The frontend will need to fetch the player list.
    return {"game_id": game_id, "player_id": player_id}


class JoinGameRequest(BaseModel):
    player_name: str
    player_class: str
    password: Optional[str] = None


@app.post("/game/{game_id}/join")
async def join_game(game_id: str, request: JoinGameRequest):
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = games[game_id]
    if game.password and game.password != request.password:
        raise HTTPException(status_code=401, detail="Incorrect password")

    player_id = str(uuid.uuid4())
    is_host = not game.players
    player = Player(
        id=player_id, name=request.player_name, player_class=request.player_class, is_host=is_host
    )
    game.players.append(player)
    await manager.broadcast({
        "type": "player_joined",
        "player": player.model_dump()
    }, game_id)
    return {"player_id": player_id, "is_host": is_host}


class StartGameRequest(BaseModel):
    player_id: str


@app.post("/game/{game_id}/start")
async def start_game(game_id: str, request: StartGameRequest):
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = games[game_id]
    player = next((p for p in game.players if p.id == request.player_id), None)

    if not player or not player.is_host:
        raise HTTPException(status_code=403, detail="Only the host can start the game")

    game.status = "in_progress"
    initial_story = await generate_initial_story(game.scenario, game.players)
    game.turns.append(Turn(player_id="game", action=initial_story))
    await manager.broadcast({
        "type": "game_start",
        "initial_story": initial_story,
        "players": [p.model_dump() for p in game.players],
        "current_player_id": game.players[0].id
    }, game_id)
    return {"message": "Game started"}


@app.get("/game/{game_id}")
def get_game(game_id: str):
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    return games[game_id]


@app.get("/game/{game_id}/status")
def get_game_status(game_id: str):
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    game = games[game_id]
    current_player_id = None
    if game.status == "in_progress" and game.players:
        current_player_id = game.players[game.current_player_index].id

    return {
        "status": game.status,
        "players": [p.model_dump() for p in game.players],
        "turns": [t.model_dump() for t in game.turns],
        "current_player_id": current_player_id,
    }


@app.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: str):
    await manager.connect(websocket, game_id)
    try:
        while True:
            data = await websocket.receive_text()
            game = games[game_id]
            current_player = game.players[game.current_player_index]

            if player_id != current_player.id:
                # It's not this player's turn.
                continue

            turn = Turn(player_id=player_id, action=data)
            game.turns.append(turn)
            game.current_round_actions.append(turn)

            # If all living players have submitted an action this round
            if len(game.current_round_actions) >= len([p for p in game.players if p.is_alive]):
                game_context = "\n".join([t.action for t in game.turns])
                player_actions = [(t.player_id, t.action) for t in game.current_round_actions]
                new_story_segment = await process_turn(game_context, game.players, player_actions)

                # Update game state and reset for the next round
                game.turns.append(Turn(player_id="game", action=new_story_segment))
                game.current_round_actions = []

                # Find the next alive player to start the new round
                game.current_player_index = 0
                while not game.players[game.current_player_index].is_alive:
                    game.current_player_index = (game.current_player_index + 1) % len(game.players)

                await manager.broadcast({
                    "type": "new_turn",
                    "story_segment": new_story_segment,
                    "current_player_id": game.players[game.current_player_index].id
                }, game_id)
            else:
                # Move to the next player
                while True:
                    game.current_player_index = (game.current_player_index + 1) % len(game.players)
                    next_player = game.players[game.current_player_index]
                    if next_player.is_alive:
                        break
                # Still waiting for other players
                await manager.broadcast({
                    "type": "action_received",
                    "player_id": player_id,
                    "next_player_id": game.players[game.current_player_index].id
                }, game_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket, game_id)
        player = next((p for p in games.get(game_id, Game(id="", scenario="", game_state="")).players if p.id == player_id), None)
        if player:
            await manager.broadcast({
                "type": "player_left",
                "player_name": player.name
            }, game_id)
