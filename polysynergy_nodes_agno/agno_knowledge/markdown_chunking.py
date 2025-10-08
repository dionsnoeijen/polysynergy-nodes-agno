from agno.knowledge.chunking.markdown import MarkdownChunking
from agno.knowledge.chunking.strategy import ChunkingStrategy
from polysynergy_node_runner.setup_context.node import Node
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Markdown Chunking",
    category="agno_knowledge",
    icon="markdown.svg",
    has_enabled_switch=False,
)
class MarkdownChunkingNode(ServiceNode):
    """Node for configuring Markdown-aware chunking strategy that respects Markdown structure (headers, lists, etc.)."""

    chunk_size: int = NodeVariableSettings(
        label="Chunk Size",
        dock=True,
        default=1500,
        info="Maximum size of each chunk in characters.",
    )

    overlap: int = NodeVariableSettings(
        label="Overlap",
        dock=True,
        default=150,
        info="Number of characters to overlap between chunks.",
    )

    respect_headers: bool = NodeVariableSettings(
        label="Respect Headers",
        dock=True,
        default=True,
        info="Whether to avoid splitting sections at header boundaries.",
    )

    chunking_strategy_instance: ChunkingStrategy | None = NodeVariableSettings(
        label="Chunking Strategy",
        has_out=True,
        info="Markdown-aware chunking strategy instance with configured parameters.",
        type="agno.knowledge.chunking.strategy.ChunkingStrategy",
    )

    async def provide_instance(self) -> ChunkingStrategy:
        """Create and return a configured MarkdownChunking instance."""
        try:
            strategy = MarkdownChunking(
                chunk_size=self.chunk_size,
                overlap=self.overlap,
                respect_headers=self.respect_headers
            )
        except TypeError:
            try:
                strategy = MarkdownChunking(
                    chunk_size=self.chunk_size,
                    overlap=self.overlap
                )
            except TypeError:
                try:
                    strategy = MarkdownChunking(chunk_size=self.chunk_size)
                except TypeError:
                    strategy = MarkdownChunking()

        self.chunking_strategy_instance = strategy
        return strategy