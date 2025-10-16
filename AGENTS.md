This is a web-based multiplayer text adventure game.

**Backend:**
- The backend is a Python application built with FastAPI.
- It uses Ollama for AI-powered decision-making.
- The entry point for the backend is `backend/main.py`.
- To run the backend, you need to have Python and Ollama installed.

**Frontend:**
- The frontend is a React application.
- It allows users to join a game and interact with the game world.
- The entry point for the frontend is `frontend/src/index.js`.

**Development:**
- To run the backend, run `uvicorn backend.main:app --reload` from the project root.
- To run the frontend, navigate to the `frontend` directory and run `npm start`.
- Make sure to install the dependencies for both the backend and the frontend before running the applications.
- Backend dependencies can be installed using `pip install -r backend/requirements.txt`.
- Frontend dependencies can be installed using `npm install` in the `frontend` directory.