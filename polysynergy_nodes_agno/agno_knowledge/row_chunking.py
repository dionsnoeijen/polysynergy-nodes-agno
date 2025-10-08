from agno.knowledge.chunking.row import RowChunking
from agno.knowledge.chunking.strategy import ChunkingStrategy
from polysynergy_node_runner.setup_context.node import Node
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Row Chunking",
    category="agno_knowledge",
    icon="table.svg",
    has_enabled_switch=False,
)
class RowChunkingNode(ServiceNode):
    """Node for configuring row-based chunking strategy for structured data like CSV, Excel files."""

    rows_per_chunk: int = NodeVariableSettings(
        label="Rows Per Chunk",
        dock=True,
        default=100,
        info="Number of rows to include in each chunk for tabular data.",
    )

    include_header: bool = NodeVariableSettings(
        label="Include Header",
        dock=True,
        default=True,
        info="Whether to include header row in each chunk for context.",
    )

    chunking_strategy_instance: ChunkingStrategy | None = NodeVariableSettings(
        label="Chunking Strategy",
        has_out=True,
        info="Row-based chunking strategy instance for structured data.",
        type="agno.knowledge.chunking.strategy.ChunkingStrategy",
    )

    async def provide_instance(self) -> ChunkingStrategy:
        """Create and return a configured RowChunking instance."""
        try:
            strategy = RowChunking(
                rows_per_chunk=self.rows_per_chunk,
                include_header=self.include_header
            )
        except TypeError:
            # Fallback if parameters are different
            try:
                strategy = RowChunking(rows_per_chunk=self.rows_per_chunk)
            except TypeError:
                strategy = RowChunking()

        self.chunking_strategy_instance = strategy
        return strategy