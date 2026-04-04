"""Tests for the pipeline graph structure and routing logic."""

from pipeline.graph.state import ReviewResult
from pipeline.graph.workflow import _make_review_router


class TestRouteAfterReview:
    def setup_method(self) -> None:
        self.route = _make_review_router(max_revisions=3)

    def test_approved(self) -> None:
        state = {
            "review": ReviewResult(approved=True, score=8.5, feedback="Good", issues=[]),
            "revision_count": 0,
        }
        assert self.route(state) == "approved"

    def test_revise(self) -> None:
        state = {
            "review": ReviewResult(
                approved=False, score=4.0, feedback="Needs work", issues=["tone"],
            ),
            "revision_count": 1,
        }
        assert self.route(state) == "revise"

    def test_max_revisions_forces_accept(self) -> None:
        state = {
            "review": ReviewResult(
                approved=False, score=5.0, feedback="Still off", issues=[],
            ),
            "revision_count": 3,
        }
        assert self.route(state) == "max_revisions"

    def test_custom_max_revisions(self) -> None:
        route_5 = _make_review_router(max_revisions=5)
        state = {
            "review": ReviewResult(
                approved=False, score=6.0, feedback="Close", issues=["minor"],
            ),
            "revision_count": 3,
        }
        assert route_5(state) == "revise"  # 3 < 5, so keep revising

    def test_no_review_triggers_revise(self) -> None:
        state = {"revision_count": 0}
        assert self.route(state) == "revise"
