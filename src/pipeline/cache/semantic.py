"""Redis-backed semantic cache using embedding cosine similarity.

Instead of exact key matching, this cache computes cosine similarity between
the query embedding and stored embeddings. A cached response is returned when
similarity exceeds the configured threshold, saving LLM API calls and tokens
for semantically equivalent inputs.
"""

from __future__ import annotations

import hashlib

import numpy as np
import redis.asyncio as aioredis
from langchain_core.embeddings import Embeddings


class SemanticCache:
    """Embedding-aware response cache backed by Redis."""

    def __init__(
        self,
        redis_url: str,
        embeddings: Embeddings,
        threshold: float = 0.92,
        ttl: int = 3600,
        namespace: str = "pipeline_cache",
    ) -> None:
        self._redis = aioredis.from_url(redis_url, decode_responses=False)
        self._embeddings = embeddings
        self._threshold = threshold
        self._ttl = ttl
        self._ns = namespace

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def get(self, query: str) -> str | None:
        """Return cached response if a semantically similar query exists."""
        query_vec = np.array(
            await self._embeddings.aembed_query(query), dtype=np.float32
        )

        keys = await self._redis.smembers(f"{self._ns}:keys")
        best_score, best_key = 0.0, None

        for raw_key in keys:
            key = raw_key.decode() if isinstance(raw_key, bytes) else raw_key
            cached_bytes = await self._redis.get(f"{self._ns}:vec:{key}")
            if cached_bytes is None:
                continue

            cached_vec = np.frombuffer(cached_bytes, dtype=np.float32)
            score = float(
                np.dot(query_vec, cached_vec)
                / (np.linalg.norm(query_vec) * np.linalg.norm(cached_vec) + 1e-8)
            )
            if score > best_score:
                best_score, best_key = score, key

        if best_score >= self._threshold and best_key is not None:
            raw = await self._redis.get(f"{self._ns}:val:{best_key}")
            return raw.decode() if raw else None
        return None

    async def set(self, query: str, response: str) -> None:
        """Store a query-response pair keyed by its embedding vector."""
        key = hashlib.sha256(query.encode()).hexdigest()[:16]
        vec = np.array(
            await self._embeddings.aembed_query(query), dtype=np.float32
        )

        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.set(f"{self._ns}:vec:{key}", vec.tobytes(), ex=self._ttl)
            pipe.set(f"{self._ns}:val:{key}", response, ex=self._ttl)
            pipe.sadd(f"{self._ns}:keys", key)
            await pipe.execute()

    async def clear(self) -> None:
        """Flush all cached entries in this namespace."""
        keys = await self._redis.smembers(f"{self._ns}:keys")
        if not keys:
            return
        to_delete = [f"{self._ns}:keys"]
        for raw in keys:
            k = raw.decode() if isinstance(raw, bytes) else raw
            to_delete.extend([f"{self._ns}:vec:{k}", f"{self._ns}:val:{k}"])
        await self._redis.delete(*to_delete)

    async def close(self) -> None:
        """Close the Redis connection."""
        await self._redis.aclose()
