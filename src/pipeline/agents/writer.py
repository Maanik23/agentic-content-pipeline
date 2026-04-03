"""Writer agent — generates content drafts based on the strategy."""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from pipeline.graph.state import PipelineState

PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert content writer. Write content that precisely matches "
        "the strategy below.\n\n"
        "Strategy:\n"
        "- Audience: {audience}\n"
        "- Key messages:\n{messages}\n"
        "- Tone: {tone}\n"
        "- Format: {content_type}\n"
        "- Platform: {platform}\n\n"
        "{revision_context}",
    ),
    ("human", "Write content about: {topic}"),
])


def create_writer(llm: BaseChatModel):
    """Return a LangGraph node that drafts (or revises) content."""
    chain = PROMPT | llm

    async def node(state: PipelineState) -> dict:
        strategy = state["strategy"]
        review = state.get("review")

        revision_context = ""
        if review and not review.approved:
            revision_context = (
                f"REVISION REQUIRED — previous draft scored {review.score}/10.\n"
                f"Feedback: {review.feedback}\n"
                f"Issues to fix: {', '.join(review.issues)}\n"
                "Address every issue listed above."
            )

        response = await chain.ainvoke({
            "topic": state["topic"],
            "audience": strategy.target_audience,
            "messages": "\n".join(f"  - {m}" for m in strategy.key_messages),
            "tone": strategy.tone,
            "content_type": strategy.content_type,
            "platform": strategy.platform,
            "revision_context": revision_context,
        })

        count = state.get("revision_count", 0) + (1 if review else 0)
        return {
            "draft": response.content,
            "revision_count": count,
            "status": f"draft_v{count + 1}",
            "trace": [
                *state.get("trace", []),
                f"writer: draft v{count + 1} ({len(response.content)} chars)",
            ],
        }

    return node
