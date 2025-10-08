from agno.knowledge.chunking.document import DocumentChunking
from agno.knowledge.chunking.strategy import ChunkingStrategy
from polysynergy_node_runner.setup_context.node import Node
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Document Chunking",
    category="agno_knowledge",
    icon="document.svg",
    has_enabled_switch=False,
)
class DocumentChunkingNode(ServiceNode):
    """Node for configuring document-structure-based chunking strategy that splits on paragraphs and sections."""

    chunk_size: int = NodeVariableSettings(
        label="Chunk Size",
        dock=True,
        default=5000,
        info="Maximum size of each chunk in characters.",
    )

    overlap: int = NodeVariableSettings(
        label="Overlap",
        dock=True,
        default=0,
        info="Number of characters to overlap between chunks.",
    )

    chunking_strategy_instance: ChunkingStrategy | None = NodeVariableSettings(
        label="Chunking Strategy",
        has_out=True,
        info="Document-structure-based chunking strategy instance with configured parameters.",
        type="agno.knowledge.chunking.strategy.ChunkingStrategy",
    )

    async def provide_instance(self) -> ChunkingStrategy:
        """Create and return a configured DocumentChunking instance."""
        strategy = DocumentChunking(
            chunk_size=self.chunk_size,
            overlap=self.overlap
        )

        self.chunking_strategy_instance = strategy
        return strategy