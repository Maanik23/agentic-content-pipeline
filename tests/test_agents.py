"""Tests for agent Pydantic models and validation."""

import pytest

from pipeline.graph.state import ReviewResult, Strategy


class TestStrategy:
    def test_valid_strategy(self) -> None:
        s = Strategy(
            target_audience="Developers",
            key_messages=["Fast", "Reliable"],
            tone="Technical",
            content_type="tutorial",
            platform="Dev.to",
        )
        assert s.target_audience == "Developers"
        assert len(s.key_messages) == 2

    def test_empty_messages_rejected(self) -> None:
        with pytest.raises(ValueError):
            Strategy(
                target_audience="Developers",
                key_messages=[],
                tone="Technical",
                content_type="tutorial",
                platform="Dev.to",
            )

    def test_json_roundtrip(self) -> None:
        s = Strategy(
            target_audience="CTOs",
            key_messages=["Scale AI operations"],
            tone="Executive",
            content_type="whitepaper",
            platform="Email",
        )
        restored = Strategy.model_validate_json(s.model_dump_json())
        assert restored == s


class TestReviewResult:
    def test_approved(self) -> None:
        r = ReviewResult(approved=True, score=8.0, feedback="Great content")
        assert r.approved
        assert r.issues == []

    def test_rejected_with_issues(self) -> None:
        r = ReviewResult(
            approved=False,
            score=3.0,
            feedback="Needs revision",
            issues=["tone mismatch", "too short"],
        )
        assert not r.approved
        assert len(r.issues) == 2

    def test_score_bounds(self) -> None:
        with pytest.raises(ValueError):
            ReviewResult(approved=True, score=11.0, feedback="Invalid")
        with pytest.raises(ValueError):
            ReviewResult(approved=True, score=-1.0, feedback="Invalid")
