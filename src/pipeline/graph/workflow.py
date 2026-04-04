"""LangGraph workflow. Assembles agents into a stateful, compiled pipeline."""

from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from pipeline.agents.reviewer import create_reviewer
from pipeline.agents.strategist import create_strategist
from pipeline.agents.writer import create_writer
from pipeline.config import Settings
from pipeline.graph.state import PipelineState
from pipeline.llm import get_llm


def _make_review_router(max_revisions: int = 3):
    """Create a routing function that respects the configured max_revisions."""

    def route(state: PipelineState) -> str:
        review = state.get("review")
        if review and review.approved:
            return "approved"
        if state.get("revision_count", 0) >= max_revisions:
            return "max_revisions"
        return "revise"

    return route


def _finalize(state: PipelineState) -> dict:
    """Terminal node. Marks content as published."""
    return {
        "final_content": state.get("final_content", state.get("draft", "")),
        "status": "published",
        "trace": [*state.get("trace", []), "finalize: content published"],
    }


def create_pipeline(settings: Settings | None = None) -> CompiledStateGraph:
    """Build and compile the multi-agent content pipeline.

    Returns a compiled LangGraph that can be invoked with::

        result = await pipeline.ainvoke({
            "topic": "...",
            "brand_context": "...",
            "revision_count": 0,
            "trace": [],
        })
    """
    settings = settings or Settings()
    llm = get_llm(settings)

    graph = StateGraph(PipelineState)

    # --- Nodes ---
    graph.add_node("strategist", create_strategist(llm))
    graph.add_node("writer", create_writer(llm))
    graph.add_node("reviewer", create_reviewer(llm, settings.review_score_threshold))
    graph.add_node("finalize", _finalize)

    # --- Edges ---
    graph.add_edge(START, "strategist")
    graph.add_edge("strategist", "writer")
    graph.add_edge("writer", "reviewer")
    graph.add_conditional_edges(
        "reviewer",
        _make_review_router(settings.max_revisions),
        {"approved": "finalize", "revise": "writer", "max_revisions": "finalize"},
    )
    graph.add_edge("finalize", END)

    # --- Compile ---
    compile_kwargs: dict = {}
    if settings.enable_hitl:
        compile_kwargs["checkpointer"] = MemorySaver()
        compile_kwargs["interrupt_before"] = ["finalize"]

    return graph.compile(**compile_kwargs)
