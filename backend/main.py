from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import uuid

from .models import Game, Player, Turn
from .ai import generate_initial_story, process_turn

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

    async def broadcast(self, message: str, game_id: str):
        if game_id in self.active_connections:
            for connection in self.active_connections[game_id]:
                await connection.send_text(message)

manager = ConnectionManager()

class CreateGameRequest(BaseModel):
    scenario: str
    password: Optional[str] = None

@app.post("/game")
async def create_game(request: CreateGameRequest):
    game_id = str(uuid.uuid4())
    game = Game(id=game_id, scenario=request.scenario, game_state="pending", password=request.password)
    games[game_id] = game
    return {"game_id": game_id}

class JoinGameRequest(BaseModel):
    player_name: str
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
    player = Player(id=player_id, name=request.player_name, is_host=is_host)
    game.players.append(player)
    await manager.broadcast(f"Player {request.player_name} has joined the game.", game_id)
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
    initial_story = await generate_initial_story(game.scenario)
    game.game_state = initial_story
    await manager.broadcast(initial_story, game_id)
    return {"message": "Game started"}

@app.get("/game/{game_id}")
def get_game(game_id: str):
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    return games[game_id]

@app.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: str):
    await manager.connect(websocket, game_id)
    try:
        while True:
            data = await websocket.receive_text()
            game = games[game_id]
            turn = Turn(player_id=player_id, action=data)
            game.turns.append(turn)

            # If all players have submitted their actions, process the turn
            if len(game.turns) == len(game.players):
                player_actions = [t.action for t in game.turns]
                new_game_state = await process_turn(game.game_state, player_actions)
                game.game_state = new_game_state
                game.turns = []
                await manager.broadcast(new_game_state, game_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket, game_id)
        # Find player name to announce departure
        player = next((p for p in games[game_id].players if p.id == player_id), None)
        player_name = player.name if player else "A player"
        await manager.broadcast(f"{player_name} has left the game.", game_id)