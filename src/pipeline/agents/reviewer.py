"""Reviewer agent.evaluates content quality with structured scoring."""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from pipeline.graph.state import PipelineState, ReviewResult

PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a strict content reviewer. Evaluate the draft against the strategy.\n\n"
        "Scoring rules:\n"
        "- Score 1-10 on: accuracy, tone match, audience fit, completeness, clarity\n"
        "- Approve ONLY if the overall score >= {threshold}\n"
        "- List every issue found, no matter how minor\n\n"
        "Strategy:\n{strategy}\n\n"
        "Draft to review:\n{draft}",
    ),
    ("human", "Review this content and provide structured feedback."),
])


def create_reviewer(llm: BaseChatModel, score_threshold: float = 7.0):
    """Return a LangGraph node that reviews drafts with a quality gate."""
    chain = PROMPT | llm.with_structured_output(ReviewResult)

    async def node(state: PipelineState) -> dict:
        strategy = state["strategy"]
        result = await chain.ainvoke({
            "threshold": score_threshold,
            "strategy": strategy.model_dump_json(indent=2),
            "draft": state["draft"],
        })

        # Enforce threshold as a guardrail.LLM scores are suggestive, not authoritative
        result.approved = result.score >= score_threshold

        update: dict = {
            "review": result,
            "status": "approved" if result.approved else "revision_needed",
            "trace": [
                *state.get("trace", []),
                f"reviewer: {'approved' if result.approved else 'rejected'} "
                f"({result.score}/10)",
            ],
        }
        if result.approved:
            update["final_content"] = state["draft"]
        return update

    return node
