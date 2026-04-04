"""Pipeline state definitions shared across all agents."""

from __future__ import annotations

from typing import TypedDict

from pydantic import BaseModel, Field


class Strategy(BaseModel):
    """Output of the Strategist agent."""

    target_audience: str
    key_messages: list[str] = Field(min_length=1, max_length=5)
    tone: str
    content_type: str
    platform: str


class ReviewResult(BaseModel):
    """Output of the Reviewer agent."""

    approved: bool
    score: float = Field(ge=0, le=10)
    feedback: str
    issues: list[str] = Field(default_factory=list)


class PipelineState(TypedDict, total=False):
    """Typed state flowing through the LangGraph pipeline.

    LangGraph nodes return partial dicts. Only the keys they update.
    ``total=False`` allows nodes to omit keys they don't touch.
    """

    # Inputs
    topic: str
    brand_context: str

    # Intermediate
    strategy: Strategy
    draft: str
    review: ReviewResult
    revision_count: int

    # Output
    final_content: str

    # Observability
    status: str
    trace: list[str]
