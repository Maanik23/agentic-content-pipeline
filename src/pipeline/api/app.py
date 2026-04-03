"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from pipeline import __version__
from pipeline.api.routes import router
from pipeline.config import Settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize shared resources on startup, clean up on shutdown."""
    app.state.settings = Settings()
    yield


def create_app() -> FastAPI:
    """Application factory — used by uvicorn and tests."""
    app = FastAPI(
        title="Agentic Content Pipeline",
        description="Multi-agent content generation with LangGraph",
        version=__version__,
        lifespan=lifespan,
    )
    app.include_router(router)
    return app
