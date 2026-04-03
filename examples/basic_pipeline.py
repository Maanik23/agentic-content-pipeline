"""Basic usage — run the full content pipeline end-to-end."""

import asyncio

from pipeline import Settings, create_pipeline


async def main() -> None:
    settings = Settings(
        llm_provider="openai",
        llm_model="gpt-4o",
        # Set PIPELINE_LLM_API_KEY in environment or .env file
    )
    pipeline = create_pipeline(settings)

    result = await pipeline.ainvoke({
        "topic": "How AI Agents Are Transforming Content Marketing in 2026",
        "brand_context": (
            "We are an AI consultancy helping mid-market companies adopt "
            "LLM-based automation. Our voice is technical but accessible."
        ),
        "revision_count": 0,
        "trace": [],
    })

    print("=== Strategy ===")
    print(result["strategy"].model_dump_json(indent=2))

    print("\n=== Final Content ===")
    print(result.get("final_content", result.get("draft", "N/A")))

    print("\n=== Review ===")
    if result.get("review"):
        print(f"  Score:    {result['review'].score}/10")
        print(f"  Approved: {result['review'].approved}")
        if result["review"].issues:
            print(f"  Issues:   {', '.join(result['review'].issues)}")

    print("\n=== Execution Trace ===")
    for step in result.get("trace", []):
        print(f"  -> {step}")


if __name__ == "__main__":
    asyncio.run(main())
