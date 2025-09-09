from __future__ import annotations
from typing import Literal, Optional

from agno.document.chunking.fixed import FixedSizeChunking
from agno.document.chunking.recursive import RecursiveChunking
from agno.document.chunking.agentic import AgenticChunking
from agno.document.chunking.semantic import SemanticChunking
from agno.document.chunking.document import DocumentChunking
from agno.document.chunking.strategy import ChunkingStrategy

ChunkingName = Literal["fixed", "recursive", "agentic", "semantic", "document"]

# Optioneel: één plek voor je UI-select opties
CHUNKING_SELECT_VALUES: dict[str, str] = {
    "fixed": "fixed",
    "recursive": "recursive",
    # "agentic": "agentic",
    "semantic": "semantic",
    "document": "document",
}

def chunking_strategy(name: Optional[str]) -> ChunkingStrategy:
    """
    Geef een chunking-strategie instance terug op basis van naam.
    Fallback = FixedSizeChunking().
    """
    name = (name or "fixed").lower()
    if name == "fixed":
        return FixedSizeChunking()
    if name == "recursive":
        return RecursiveChunking()
    # @todo: Add this later, because it requires an additional node
    # if name == "agentic":
    #     return AgenticChunking()
    if name == "semantic":
        return SemanticChunking()
    if name == "document":
        return DocumentChunking()
    # fallback
    return FixedSizeChunking()