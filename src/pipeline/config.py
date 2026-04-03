"""Pipeline configuration via environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "PIPELINE_", "env_file": ".env"}

    # LLM — provider and model are swappable without code changes
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.7
    llm_api_key: str = ""

    # Redis for semantic caching
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 3600
    cache_similarity_threshold: float = 0.92

    # API server
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Pipeline behaviour
    max_revisions: int = 3
    review_score_threshold: float = 7.0
    enable_cache: bool = True
    enable_hitl: bool = False
