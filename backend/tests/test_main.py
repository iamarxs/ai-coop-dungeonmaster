import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.models import Game, Player

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_games_state():
    """
    A fixture to automatically clear the global `games` dictionary before each test.
    This ensures test isolation.
    """
    with patch("backend.main.games", {}) as _mock_games:
        yield _mock_games


@patch("uuid.uuid4")
def test_create_game(mock_uuid4):
    """
    Tests the game creation endpoint.
    """
    mock_uuid4.side_effect = ["test_game_123", "test_player_123"]
    response = client.post(
        "/game",
        json={
            "scenario": "A test adventure",
            "player_name": "HostPlayer",
            "player_class": "Warrior",
            "password": "test_password",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "game_id" in data
    assert "player_id" in data
    assert data["game_id"] == "test_game_123"
    assert data["player_id"] == "test_player_123"


@patch("uuid.uuid4")
def test_join_game(mock_uuid4, clear_games_state):
    """
    Tests the join game endpoint.
    """
    mock_uuid4.return_value = "joining_player_456"
    game_id = "test_game_123"
    # First, ensure a game exists
    clear_games_state[game_id] = Game(
        id=game_id,
        scenario="A test adventure",
        game_state="pending",
        password="test_password",
        players=[],
    )

    response = client.post(
        f"/game/{game_id}/join",
        json={
            "player_name": "Tester",
            "player_class": "Mage",
            "password": "test_password",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "player_id" in data
    assert data["player_id"] == "joining_player_456"
    assert len(clear_games_state[game_id].players) == 1
    assert clear_games_state[game_id].players[0].name == "Tester"


def test_join_game_not_found():
    """
    Tests joining a game that does not exist.
    """
    response = client.post(
        "/game/non_existent_game/join",
        json={"player_name": "Tester", "player_class": "Rogue", "password": "test_password"},
    )
    assert response.status_code == 404


def test_get_game_status(clear_games_state):
    """
    Tests retrieving the status of a game.
    """
    game_id = "test_game_123"
    player = Player(id="p1", name="p1_name", player_class="p1_class")
    clear_games_state[game_id] = Game(
        id=game_id,
        scenario="A test adventure",
        game_state="pending",
        status="pending",
        players=[player],
    )

    response = client.get(f"/game/{game_id}/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert len(data["players"]) == 1
    assert data["players"][0]["name"] == "p1_name"


@patch("backend.main.generate_initial_story", new_callable=AsyncMock)
def test_start_game(mock_generate_story, clear_games_state):
    """Tests that only the host can start the game."""
    mock_generate_story.return_value = "The adventure begins!"
    game_id = "test_game_123"
    host_player = Player(id="host_id", name="Host", player_class="Fighter", is_host=True)
    clear_games_state[game_id] = Game(
        id=game_id, scenario="test", game_state="pending", players=[host_player]
    )

    response = client.post(f"/game/{game_id}/start", json={"player_id": "host_id"})

    assert response.status_code == 200
    assert response.json() == {"message": "Game started"}
    assert clear_games_state[game_id].status == "in_progress"
    # assert clear_games_state[game_id].game_state == "The adventure begins!"
    mock_generate_story.assert_awaited_once()
