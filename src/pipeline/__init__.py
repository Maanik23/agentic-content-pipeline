"""Agentic Content Pipeline - Multi-agent content generation with LangGraph."""

__version__ = "0.1.0"

from pipeline.config import Settings
from pipeline.graph.workflow import create_pipeline

__all__ = ["Settings", "create_pipeline"]
