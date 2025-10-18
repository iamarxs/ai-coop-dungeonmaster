import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [gameId, setGameId] = useState('');
  const [playerId, setPlayerId] = useState('');
  const [isHost, setIsHost] = useState(false);
  const [scenario, setScenario] = useState('');
  const [password, setPassword] = useState('');
  const [playerName, setPlayerName] = useState('');
  const [playerClass, setPlayerClass] = useState('');
  const [players, setPlayers] = useState([]);
  const [action, setAction] = useState('');
  const [socket, setSocket] = useState(null);
  const [theme, setTheme] = useState('dark');
  const [view, setView] = useState('create');
  const [turns, setTurns] = useState([]);
  const [currentPlayerId, setCurrentPlayerId] = useState(null);
  const [statusMessage, setStatusMessage] = useState('');

  const handleCreateGame = async () => {
    try {
      const response = await fetch('http://localhost:8000/game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario, player_name: playerName, player_class: playerClass, password }),
      });
      const data = await response.json();
      console.log("Game created:", data);
      setGameId(data.game_id);
      setPlayerId(data.player_id);
      setIsHost(true);
      setView('lobby');
    } catch (error) {
      console.error("Error creating game:", error);
    }
  };

  const handleJoinGame = async () => {
    const response = await fetch(`http://localhost:8000/game/${gameId}/join`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_name: playerName, player_class: playerClass, password }),
    });
    const data = await response.json();
    setPlayerId(data.player_id);
    setIsHost(data.is_host);
    setView('lobby');
  };

  const handleStartGame = async () => {
    await fetch(`http://localhost:8000/game/${gameId}/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId }),
    });
  };

  const handleSendAction = () => {
    if (socket && action.trim() !== '') {
      socket.send(action);
      setAction('');
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      handleSendAction();
    }
  };

  useEffect(() => {
    console.log("gameId changed:", gameId);
  }, [gameId]);

  useEffect(() => {
    if (gameId && playerId) {
      const ws = new WebSocket(`ws://localhost:8000/ws/${gameId}/${playerId}`);
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        // Use functional updates to avoid stale state
        setPlayers(prevPlayers => {
          switch (data.type) {
            case 'game_start':
              setTurns([{ player_id: 'game', action: data.game_state }]);
              setCurrentPlayerId(data.current_player_id);
              return data.players;
            case 'player_joined':
              return [...prevPlayers, data.player];
            case 'action_received':
              setCurrentPlayerId(data.next_player_id);
              const actingPlayer = prevPlayers.find(p => p.id === data.player_id);
              const nextPlayer = prevPlayers.find(p => p.id === data.next_player_id);
              if (actingPlayer && nextPlayer) {
                setStatusMessage(`${actingPlayer.name} has acted. Now it's ${nextPlayer.name}'s turn.`);
              }
              return prevPlayers; // No change to players
            case 'new_turn':
              setTurns(prevTurns => [...prevTurns, { player_id: 'game', action: data.story_segment }]);
              setCurrentPlayerId(data.current_player_id);
              const currentPlayer = prevPlayers.find(p => p.id === data.current_player_id);
              if (currentPlayer) {
                setStatusMessage(`A new turn begins. It's ${currentPlayer.name}'s turn.`);
              }
              return prevPlayers; // No change to players
            case 'player_left':
              setStatusMessage(`${data.player_name} has left the game.`);
              return prevPlayers.filter(p => p.name !== data.player_name);
            default:
              console.log("Unhandled message type:", data.type);
              return prevPlayers;
          }
        });
      };
      setSocket(ws);

      // Fetch initial game state
      const fetchGameStatus = async () => {
        const response = await fetch(`http://localhost:8000/game/${gameId}/status`);
        const data = await response.json();
        if (data.status !== 'pending') {
          setPlayers(data.players);
          setTurns(data.turns);
          setCurrentPlayerId(data.current_player_id);
          setView('lobby');
        }
      };
      fetchGameStatus();

      return () => {
        ws.close();
      };
    }
  }, [gameId, playerId]);

  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === 'dark' ? 'light' : 'dark'));
  };

  return (
    <div className={`App ${theme}-mode`}>
      <button onClick={toggleTheme}>
        Switch to {theme === 'dark' ? 'Light' : 'Dark'} Mode
      </button>
      <h1>Multiplayer Text Adventure</h1>
      {view === 'create' && (
        <div>
          <h2>Create Game</h2>
          <input
            type="text"
            placeholder="Your Name"
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
          />
          <input
            type="text"
            placeholder="Your Class"
            value={playerClass}
            onChange={(e) => setPlayerClass(e.target.value)}
          />
          <input
            type="text"
            placeholder="Scenario"
            value={scenario}
            onChange={(e) => setScenario(e.target.value)}
          />
          <input
            type="password"
            placeholder="Password (optional)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button onClick={handleCreateGame}>Create Game</button>
          <p>
            Already have a game ID?{' '}
            <button onClick={() => setView('join')}>Join a Game</button>
          </p>
        </div>
      )}
      {view === 'join' && (
        <div>
          <h2>Join Game</h2>
          <input
            type="text"
            placeholder="Game ID"
            value={gameId}
            onChange={(e) => setGameId(e.target.value)}
          />
          <input
            type="text"
            placeholder="Your Name"
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
          />
          <input
            type="text"
            placeholder="Your Class"
            value={playerClass}
            onChange={(e) => setPlayerClass(e.target.value)}
          />
          <input
            type="password"
            placeholder="Password (optional)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button onClick={handleJoinGame}>Join Game</button>
          <p>
            Want to host a game?{' '}
            <button onClick={() => setView('create')}>Create a Game</button>
          </p>
        </div>
      )}
      {view === 'lobby' && (
        <div>
          <h2>Game ID: {gameId}</h2>
          <h3>Players</h3>
          <ul className="player-status-list">
            {players.map((p) => {
              let status = p.is_alive ? 'Alive' : 'Dead';
              if (p.id === currentPlayerId) {
                status = 'Writing...';
              }
              return (
                <li key={p.id} className={`status-${status.toLowerCase()}`}>
                  {p.name} ({p.player_class}) - {status}
                </li>
              );
            })}
          </ul>
          {isHost && turns.length === 0 && <button onClick={handleStartGame}>Start Game</button>}
          <div>
            <h3>Story</h3>
            <div className="game-state">
              {turns.map((turn, index) => {
                const content = { __html: turn.action.replace(/"(.*?)"/g, '<b>"$1"</b>') };
                return (
                  <p
                    key={index}
                    className={turn.player_id === 'game' ? 'game-narrative' : 'player-action'}
                    dangerouslySetInnerHTML={content}
                  />
                );
              })}
            </div>
          </div>
          <p>{statusMessage}</p>
          <input
            type="text"
            placeholder="What do you do?"
            value={action}
            onChange={(e) => setAction(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={playerId !== currentPlayerId}
            className="action-input"
          />
          <button onClick={handleSendAction} disabled={playerId !== currentPlayerId} className="action-button">
            Send Action
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
