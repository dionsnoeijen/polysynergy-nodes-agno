from agno.knowledge.chunking.fixed import FixedSizeChunking
from agno.knowledge.chunking.strategy import ChunkingStrategy
from polysynergy_node_runner.setup_context.node import Node
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Fixed Size Chunking",
    category="agno_knowledge",
    icon="brain.svg",
    has_enabled_switch=False,
)
class FixedSizeChunkingNode(ServiceNode):
    """Node for configuring fixed-size chunking strategy with customizable chunk size and overlap."""

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
        info="Number of characters to overlap between chunks. Must be less than chunk size.",
    )

    chunking_strategy_instance: ChunkingStrategy | None = NodeVariableSettings(
        label="Chunking Strategy",
        has_out=True,
        info="Fixed-size chunking strategy instance with configured parameters.",
        type="agno.knowledge.chunking.strategy.ChunkingStrategy",
    )

    async def provide_instance(self) -> ChunkingStrategy:
        """Create and return a configured FixedSizeChunking instance."""
        if self.overlap >= self.chunk_size:
            raise ValueError(f"Overlap ({self.overlap}) must be less than chunk size ({self.chunk_size})")

        strategy = FixedSizeChunking(
            chunk_size=self.chunk_size,
            overlap=self.overlap
        )

        self.chunking_strategy_instance = strategy
        return strategy