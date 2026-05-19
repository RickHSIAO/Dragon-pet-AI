# dragon-pet-ai — Backend

FastAPI backend for the dragon-pet-ai desktop companion.

## Quick Start

```bash
cd backend

# Create and activate virtual environment (Windows)
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the development server
uvicorn app.main:app --reload --port 8000
```

On macOS / Linux, activate with:
```bash
source .venv/bin/activate
```

## Endpoints (TASK-003 — skeleton only)

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness check — returns `{"status": "ok"}` |
| POST | `/chat` | Mock chat via service layer — returns a character-style reply |

### POST /chat

Request body:
```json
{ "message": "Hello!" }
```

Response:
```json
{
  "reply": "Got it. I'm listening — what else is on your mind?",
  "mood": "focused",
  "source": "mock"
}
```

`source: "mock"` indicates no real LLM is connected yet. `/chat` currently delegates to the backend service layer, but remains mock-only.

## Tests

```bash
cd backend
python -m pytest
```

## Current Limitations (TASK-003)

- `/chat` returns a service-generated mock reply — no real AI model is connected.
- No database tables defined yet (SQLite file is created but empty).
- No memory system, no character state persistence.
- No voice (TTS/STT), no Live2D, no shell execution, no file access.

## Project Structure

```
backend/
  app/
    __init__.py
    main.py           # FastAPI app entry point
    api/
      __init__.py
      routes.py       # GET /health, POST /chat
    services/
      __init__.py
      chat_service.py
      character_service.py
    db/
      __init__.py
      database.py     # SQLModel engine + init_db placeholder
    schemas/
      __init__.py
      chat.py         # ChatRequest / ChatResponse Pydantic models
  requirements.txt
  README.md
```
