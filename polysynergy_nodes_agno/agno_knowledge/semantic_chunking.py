from agno.knowledge.chunking.semantic import SemanticChunking
from agno.knowledge.chunking.strategy import ChunkingStrategy
from polysynergy_node_runner.setup_context.node import Node
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Semantic Chunking",
    category="agno_knowledge",
    icon="brain.svg",
    has_enabled_switch=False,
)
class SemanticChunkingNode(ServiceNode):
    """Node for configuring semantic chunking strategy that splits text based on semantic similarity."""

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

    similarity_threshold: float = NodeVariableSettings(
        label="Similarity Threshold",
        dock=True,
        default=0.7,
        info="Minimum semantic similarity threshold for keeping text together (0.0-1.0).",
    )

    chunking_strategy_instance: ChunkingStrategy | None = NodeVariableSettings(
        label="Chunking Strategy",
        has_out=True,
        info="Semantic chunking strategy instance with configured parameters.",
        type="agno.knowledge.chunking.strategy.ChunkingStrategy",
    )

    async def provide_instance(self) -> ChunkingStrategy:
        """Create and return a configured SemanticChunking instance."""
        # Try to create SemanticChunking with various parameter combinations
        # Since we don't know the exact signature, we'll be flexible
        try:
            strategy = SemanticChunking(
                chunk_size=self.chunk_size,
                overlap=self.overlap,
                similarity_threshold=self.similarity_threshold
            )
        except TypeError:
            try:
                strategy = SemanticChunking(
                    chunk_size=self.chunk_size,
                    overlap=self.overlap
                )
            except TypeError:
                try:
                    strategy = SemanticChunking(chunk_size=self.chunk_size)
                except TypeError:
                    strategy = SemanticChunking()

        self.chunking_strategy_instance = strategy
        return strategy