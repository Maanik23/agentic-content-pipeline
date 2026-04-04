"""API endpoints.sync generation and SSE streaming."""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from pipeline import __version__
from pipeline.api.schemas import HealthResponse, PipelineRequest, PipelineResponse
from pipeline.config import Settings
from pipeline.graph.workflow import create_pipeline

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(version=__version__)


@router.post("/generate", response_model=PipelineResponse)
async def generate(req: PipelineRequest, request: Request) -> PipelineResponse:
    """Run the full pipeline and return the final result."""
    settings: Settings = request.app.state.settings
    pipeline = create_pipeline(settings)

    result = await pipeline.ainvoke({
        "topic": req.topic,
        "brand_context": req.brand_context,
        "content_type": req.content_type,
        "revision_count": 0,
        "trace": [],
    })

    return PipelineResponse(
        final_content=result.get("final_content", result.get("draft", "")),
        strategy=result["strategy"],
        review=result.get("review"),
        revision_count=result.get("revision_count", 0),
        trace=result.get("trace", []),
    )


@router.post("/generate/stream")
async def generate_stream(req: PipelineRequest, request: Request) -> EventSourceResponse:
    """Stream pipeline progress as Server-Sent Events.

    Each event corresponds to one agent completing its work.
    """
    settings: Settings = request.app.state.settings
    pipeline = create_pipeline(settings)

    async def event_stream() -> AsyncGenerator[dict, None]:
        async for chunk in pipeline.astream(
            {
                "topic": req.topic,
                "brand_context": req.brand_context,
                "content_type": req.content_type,
                "revision_count": 0,
                "trace": [],
            },
            stream_mode="updates",
        ):
            for node_name, update in chunk.items():
                yield {
                    "event": node_name,
                    "data": json.dumps(update, default=str),
                }

    return EventSourceResponse(event_stream())
