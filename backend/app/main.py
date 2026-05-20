"""
dragon-pet-ai — FastAPI application entry point.

Start with:
    uvicorn app.main:app --reload --port 8000

TASK-003: Minimal skeleton — /health and /chat (mock) only.
No LLM, no TTS, no STT, no Live2D, no shell execution, no file access.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown logic."""
    # Startup
    init_db()
    yield
    # Shutdown (nothing to clean up yet)


app = FastAPI(
    title="dragon-pet-ai",
    description="AI desktop pet companion — backend API",
    version="0.1.0-skeleton",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — allow Electron renderer (file:// origin) to reach the backend.
# In production this should be tightened to a specific origin.
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Electron uses file:// — restrict further in Phase 2
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(router)
