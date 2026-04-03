"""API request and response models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from pipeline.graph.state import ReviewResult, Strategy


class PipelineRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)
    brand_context: str = Field(default="", max_length=2000)
    content_type: str = Field(default="blog_post")


class PipelineResponse(BaseModel):
    final_content: str
    strategy: Strategy
    review: ReviewResult | None = None
    revision_count: int = 0
    trace: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
