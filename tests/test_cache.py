"""Tests for the semantic cache."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from pipeline.cache.semantic import SemanticCache


@pytest.fixture
def mock_embeddings() -> AsyncMock:
    emb = AsyncMock()
    emb.aembed_query = AsyncMock(return_value=[0.1, 0.2, 0.3])
    return emb


@pytest.fixture
def mock_redis() -> AsyncMock:
    r = AsyncMock()
    r.aclose = AsyncMock()
    return r


@pytest.mark.asyncio
async def test_cache_miss_on_empty(mock_redis: AsyncMock, mock_embeddings: AsyncMock) -> None:
    mock_redis.smembers = AsyncMock(return_value=set())

    with patch("redis.asyncio.from_url", return_value=mock_redis):
        cache = SemanticCache("redis://localhost", mock_embeddings, threshold=0.9)
        cache._redis = mock_redis
        result = await cache.get("test query")
        assert result is None


@pytest.mark.asyncio
async def test_cache_hit_above_threshold(
    mock_redis: AsyncMock, mock_embeddings: AsyncMock,
) -> None:
    vec = np.array([0.1, 0.2, 0.3], dtype=np.float32)
    mock_redis.smembers = AsyncMock(return_value={b"abc123"})
    mock_redis.get = AsyncMock(side_effect=lambda k: {
        "pipeline_cache:vec:abc123": vec.tobytes(),
        "pipeline_cache:val:abc123": b"cached response",
    }.get(k))

    with patch("redis.asyncio.from_url", return_value=mock_redis):
        cache = SemanticCache("redis://localhost", mock_embeddings, threshold=0.9)
        cache._redis = mock_redis
        result = await cache.get("test query")
        assert result == "cached response"


@pytest.mark.asyncio
async def test_cache_set_stores_three_keys(
    mock_redis: AsyncMock, mock_embeddings: AsyncMock,
) -> None:
    pipe_mock = AsyncMock()
    pipe_mock.__aenter__ = AsyncMock(return_value=pipe_mock)
    pipe_mock.__aexit__ = AsyncMock(return_value=False)
    mock_redis.pipeline = MagicMock(return_value=pipe_mock)

    with patch("redis.asyncio.from_url", return_value=mock_redis):
        cache = SemanticCache("redis://localhost", mock_embeddings)
        cache._redis = mock_redis
        await cache.set("test query", "test response")

        assert pipe_mock.set.call_count == 2  # vec + val
        assert pipe_mock.sadd.call_count == 1  # keys set
