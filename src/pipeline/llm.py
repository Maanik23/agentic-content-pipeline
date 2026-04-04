"""LLM provider factory.swap providers via config without touching agent code."""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel

from pipeline.config import Settings


def get_llm(settings: Settings) -> BaseChatModel:
    """Instantiate the configured chat model."""
    match settings.llm_provider:
        case "openai":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                api_key=settings.llm_api_key,
            )
        case "google":
            from langchain_google_genai import ChatGoogleGenerativeAI

            return ChatGoogleGenerativeAI(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                google_api_key=settings.llm_api_key,
            )
        case "anthropic":
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                api_key=settings.llm_api_key,
            )
        case provider:
            raise ValueError(
                f"Unsupported LLM provider: {provider}. "
                "Choose from: openai, google, anthropic"
            )
