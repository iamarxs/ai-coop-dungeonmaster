# Multiplayer Text Adventure Game

This is a web-based multiplayer text adventure game where players can join a host's instance, and an AI (Ollama) acts as the game master.

## Project Structure

-   `backend/`: Contains the Python FastAPI server.
-   `frontend/`: Contains the React web client.
-   `AGENTS.md`: Provides context and instructions for AI agents working on this repository.

## Getting Started

To run this project, you will need to have the following installed:

-   Python 3.8+
-   Node.js and npm
-   Ollama (with a model like `llama2` pulled)

### Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the backend server:**
    ```bash
    uvicorn main:app --reload
    ```
    The backend server will be running on `http://localhost:8000`.

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install the required Node.js packages:**
    ```bash
    npm install
    ```

3.  **Run the frontend development server:**
    ```bash
    npm start
    ```
    The frontend will open in your browser at `http://localhost:3000`.

## How to Play

1.  **Start the Backend and Frontend:** Follow the setup instructions above to get both servers running.
2.  **Create a Game:**
    -   Open your browser to `http://localhost:3000`.
    -   Enter a scenario for the game (e.g., "A group of adventurers find themselves in a dark cave.").
    -   Optionally, set a password for the game.
    -   Click "Create Game".
3.  **Join a Game:**
    -   After a game is created, you will be taken to the "Join Game" screen. The Game ID will be pre-filled.
    -   Enter your name.
    -   If a password was set, enter it.
    -   Click "Join Game".
4.  **Start the Game:**
    -   Once all players have joined, the host can click "Start Game".
5.  **Play the Game:**
    -   The AI will describe the initial situation.
    -   On your turn, enter the action you want to take and click "Send Action".
    -   The AI will process the actions of all players and advance the story.

## Known Issues

-   There is a known CORS issue when running the frontend and backend servers separately. The application is configured to work correctly with the provided setup instructions, but you may encounter issues if you deviate from them.