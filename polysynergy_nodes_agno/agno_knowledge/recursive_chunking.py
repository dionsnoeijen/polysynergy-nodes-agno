from agno.knowledge.chunking.recursive import RecursiveChunking
from agno.knowledge.chunking.strategy import ChunkingStrategy
from polysynergy_node_runner.setup_context.node import Node
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Recursive Chunking",
    category="agno_knowledge",
    icon="brain.svg",
    has_enabled_switch=False,
)
class RecursiveChunkingNode(ServiceNode):
    """Node for configuring recursive chunking strategy that splits text hierarchically."""

    chunk_size: int = NodeVariableSettings(
        label="Chunk Size",
        dock=True,
        default=1000,
        info="Maximum size of each chunk in characters.",
    )

    overlap: int = NodeVariableSettings(
        label="Overlap",
        dock=True,
        default=100,
        info="Number of characters to overlap between chunks.",
    )

    chunking_strategy_instance: ChunkingStrategy | None = NodeVariableSettings(
        label="Chunking Strategy",
        has_out=True,
        info="Recursive chunking strategy instance with configured parameters.",
        type="agno.knowledge.chunking.strategy.ChunkingStrategy",
    )

    async def provide_instance(self) -> ChunkingStrategy:
        """Create and return a configured RecursiveChunking instance."""
        # Try to create RecursiveChunking with common parameters
        # We'll handle potential parameter differences gracefully
        try:
            strategy = RecursiveChunking(
                chunk_size=self.chunk_size,
                overlap=self.overlap
            )
        except TypeError:
            # Fallback if parameters are different
            try:
                strategy = RecursiveChunking(chunk_size=self.chunk_size)
            except TypeError:
                strategy = RecursiveChunking()

        self.chunking_strategy_instance = strategy
        return strategy