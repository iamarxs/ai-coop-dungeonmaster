# AGENTS.md

## Stack

- **Backend:** Python, FastAPI, Ollama
- **Frontend:** React

## Core Architecture

- **Backend Framework:** FastAPI

  - Endpoints:
    - `/game`: Create a new game.
    - `/game/{game_id}/join`: Join an existing game.
    - `/game/{game_id}/start`: Start a game.
    - `/game/{game_id}`: Get game details.
    - `/game/{game_id}/status`: Get game status.
    - `/ws/{game_id}/{player_id}`: WebSocket endpoint for real-time communication.

- **Frontend Framework:** React
  - Entry Point: `index.js`
  - Main Component: `App`

## Critical Patterns

- **FastAPI Endpoints:** The backend uses FastAPI to define RESTful endpoints for game management.
- **WebSocket Endpoint:** A WebSocket endpoint is used for real-time communication between clients and the server.
- **Dependency Injection:** Dependencies like `generate_initial_story` and `process_turn` are injected into the endpoints.

## Code Style

- **Imports:** Imports are grouped by standard library, third-party libraries, and local modules.
- **Type Annotations:** Type annotations are used extensively for function parameters and return types.
- **Error Handling:** HTTP exceptions are used to handle errors.
- **Asynchronous Functions:** Asynchronous functions (`async def`) are used for handling WebSocket connections and game logic.

## Testing Specifics

- **Unit Tests:** Test individual functions and components using frameworks like `pytest` or `unittest`.
- **Integration Tests:** Test interactions between different parts of the application (e.g., backend and frontend) using tools like `requests`.
- **End-to-End (E2E) Tests:** Simulate user interactions with the application using tools like `Selenium` or `Cypress`.
- **Mocking:** Use mocking libraries to isolate dependencies during tests. Libraries like `unittest.mock` can be used for this purpose.
- **Code Coverage:** Ensure that your tests cover a significant portion of the codebase using tools like `coverage.py`.

## Conclusion

This document outlines the key components, architecture, and best practices for the project.
