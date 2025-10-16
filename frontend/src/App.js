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
  const [gameState, setGameState] = useState('');
  const [action, setAction] = useState('');
  const [socket, setSocket] = useState(null);
  const [theme, setTheme] = useState('dark');

  const handleCreateGame = async () => {
    try {
      const response = await fetch('http://localhost:8000/game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario, password }),
      });
      const data = await response.json();
      console.log("Game created:", data);
      setGameId(data.game_id);
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
  };

  const handleStartGame = async () => {
    await fetch(`http://localhost:8000/game/${gameId}/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId }),
    });
  };

  const handleSendAction = () => {
    if (socket) {
      socket.send(action);
      setAction('');
    }
  };

  useEffect(() => {
    console.log("gameId changed:", gameId);
  }, [gameId]);

  useEffect(() => {
    if (gameId && playerId) {
      const ws = new WebSocket(`ws://localhost:8000/ws/${gameId}/${playerId}`);
      ws.onmessage = (event) => {
        setGameState((prev) => prev + '\n' + event.data);
      };
      setSocket(ws);

      const interval = setInterval(async () => {
        const response = await fetch(`http://localhost:8000/game/${gameId}`);
        const data = await response.json();
        setPlayers(data.players);
      }, 1000);

      return () => {
        ws.close();
        clearInterval(interval);
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
      {!gameId ? (
        <div>
          <h2>Create Game</h2>
          <input type="text" placeholder="Scenario" value={scenario} onChange={(e) => setScenario(e.target.value)} />
          <input type="password" placeholder="Password (optional)" value={password} onChange={(e) => setPassword(e.target.value)} />
          <button onClick={handleCreateGame}>Create Game</button>
        </div>
      ) : !playerId ? (
        <div>
          <h2>Join Game</h2>
          <input type="text" placeholder="Game ID" value={gameId} onChange={(e) => setGameId(e.target.value)} />
          <input type="text" placeholder="Your Name" value={playerName} onChange={(e) => setPlayerName(e.target.value)} />
          <input type="text" placeholder="Your Class" value={playerClass} onChange={(e) => setPlayerClass(e.target.value)} />
          <input type="password" placeholder="Password (optional)" value={password} onChange={(e) => setPassword(e.target.value)} />
          <button onClick={handleJoinGame}>Join Game</button>
        </div>
      ) : (
        <div>
          <h2>Game ID: {gameId}</h2>
          <h3>Players</h3>
          <ul>
            {players.map((p) => (
              <li key={p.id}>
                {p.name} ({p.player_class})
              </li>
            ))}
          </ul>
          {isHost && <button onClick={handleStartGame}>Start Game</button>}
          <div>
            <h3>Game State</h3>
            <pre>{gameState}</pre>
          </div>
          <input type="text" placeholder="What do you do?" value={action} onChange={(e) => setAction(e.target.value)} />
          <button onClick={handleSendAction}>Send Action</button>
        </div>
      )}
    </div>
  );
}

export default App;