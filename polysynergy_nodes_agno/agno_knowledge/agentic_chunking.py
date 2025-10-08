from agno.knowledge.chunking.agentic import AgenticChunking
from agno.knowledge.chunking.strategy import ChunkingStrategy
from polysynergy_node_runner.setup_context.node import Node
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Agentic Chunking",
    category="agno_knowledge",
    icon="robot.svg",
    has_enabled_switch=False,
)
class AgenticChunkingNode(ServiceNode):
    """Node for configuring AI-powered agentic chunking strategy that uses LLM to intelligently split text."""

    max_chunk_size: int = NodeVariableSettings(
        label="Max Chunk Size",
        dock=True,
        default=2000,
        info="Maximum size of each chunk in characters (for agentic chunking).",
    )

    overlap: int = NodeVariableSettings(
        label="Overlap",
        dock=True,
        default=200,
        info="Number of characters to overlap between chunks.",
    )

    chunking_strategy_instance: ChunkingStrategy | None = NodeVariableSettings(
        label="Chunking Strategy",
        has_out=True,
        info="AI-powered agentic chunking strategy instance with configured parameters.",
        type="agno.knowledge.chunking.strategy.ChunkingStrategy",
    )

    async def provide_instance(self) -> ChunkingStrategy:
        """Create and return a configured AgenticChunking instance."""
        strategy = AgenticChunking(
            max_chunk_size=self.max_chunk_size,
            overlap=self.overlap
        )

        self.chunking_strategy_instance = strategy
        return strategy