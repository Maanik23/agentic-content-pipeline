"""Shared test fixtures."""

from __future__ import annotations

import pytest

from pipeline.config import Settings
from pipeline.graph.state import PipelineState, Strategy


@pytest.fixture
def settings() -> Settings:
    return Settings(llm_provider="openai", llm_api_key="test-key")


@pytest.fixture
def sample_strategy() -> Strategy:
    return Strategy(
        target_audience="Tech-savvy professionals aged 25-40",
        key_messages=["AI agents automate workflows", "Production-ready from day one"],
        tone="Professional yet approachable",
        content_type="blog_post",
        platform="LinkedIn",
    )


@pytest.fixture
def sample_state(sample_strategy: Strategy) -> PipelineState:
    return PipelineState(
        topic="AI Agents in Production",
        brand_context="We build enterprise AI solutions.",
        strategy=sample_strategy,
        draft="Sample draft content about AI agents in production systems...",
        revision_count=0,
        trace=[],
    )
