"""Strategist agent — analyses brand context and produces a content strategy."""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from pipeline.graph.state import PipelineState, Strategy

PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a senior marketing strategist. Given a brand context and topic, "
        "produce a focused content strategy.\n\n"
        "Brand context:\n{brand_context}",
    ),
    ("human", "Create a content strategy for: {topic}"),
])


def create_strategist(llm: BaseChatModel):
    """Return a LangGraph node that generates a content strategy."""
    chain = PROMPT | llm.with_structured_output(Strategy)

    async def node(state: PipelineState) -> dict:
        strategy = await chain.ainvoke({
            "topic": state["topic"],
            "brand_context": state.get("brand_context", ""),
        })
        return {
            "strategy": strategy,
            "status": "strategy_complete",
            "trace": [
                *state.get("trace", []),
                f"strategist: {strategy.content_type} for {strategy.platform}",
            ],
        }

    return node
