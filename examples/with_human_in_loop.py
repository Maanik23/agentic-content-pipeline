"""Pipeline with human-in-the-loop approval gate.

The graph pauses before the "finalize" node, letting a human
review and approve content before it's marked as published.
"""

import asyncio

from pipeline import Settings, create_pipeline


async def main() -> None:
    settings = Settings(
        llm_provider="openai",
        llm_model="gpt-4o",
        enable_hitl=True,
    )
    pipeline = create_pipeline(settings)

    # Thread ID enables checkpoint-based resumption
    config = {"configurable": {"thread_id": "hitl-demo-1"}}

    # Phase 1: run until the HITL interrupt (before "finalize" node)
    result = await pipeline.ainvoke(
        {
            "topic": "Building Reliable AI Agents for Enterprise",
            "brand_context": "Enterprise AI platform company targeting CTOs.",
            "revision_count": 0,
            "trace": [],
        },
        config=config,
    )

    print("=== Draft Ready for Human Review ===")
    print(result.get("draft", "")[:500])
    if result.get("review"):
        print(f"\nReview score: {result['review'].score}/10")

    # Phase 2: human decides
    approval = input("\nApprove this content? (y/n): ").strip().lower()
    if approval == "y":
        # Resume the graph — executes the "finalize" node
        final = await pipeline.ainvoke(None, config=config)
        print("\n=== Published ===")
        print(final.get("final_content", "")[:500])
    else:
        print("\nContent rejected by human reviewer.")


if __name__ == "__main__":
    asyncio.run(main())
