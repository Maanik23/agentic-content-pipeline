"""Tests for the pipeline graph structure and routing logic."""

from pipeline.graph.state import ReviewResult
from pipeline.graph.workflow import _route_after_review


class TestRouteAfterReview:
    def test_approved(self) -> None:
        state = {
            "review": ReviewResult(approved=True, score=8.5, feedback="Good", issues=[]),
            "revision_count": 0,
        }
        assert _route_after_review(state) == "approved"

    def test_revise(self) -> None:
        state = {
            "review": ReviewResult(
                approved=False, score=4.0, feedback="Needs work", issues=["tone"],
            ),
            "revision_count": 1,
        }
        assert _route_after_review(state) == "revise"

    def test_max_revisions_forces_accept(self) -> None:
        state = {
            "review": ReviewResult(
                approved=False, score=5.0, feedback="Still off", issues=[],
            ),
            "revision_count": 3,
        }
        assert _route_after_review(state) == "max_revisions"

    def test_edge_case_exactly_at_max(self) -> None:
        state = {
            "review": ReviewResult(
                approved=False, score=6.0, feedback="Close", issues=["minor"],
            ),
            "revision_count": 3,
        }
        assert _route_after_review(state) == "max_revisions"

    def test_no_review_triggers_revise(self) -> None:
        state = {"revision_count": 0}
        assert _route_after_review(state) == "revise"
