from agno.knowledge.embedder import Embedder
from agno.knowledge.embedder.openai import OpenAIEmbedder
from polysynergy_node_runner.setup_context.dock_property import dock_property
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode


@node(
    name="OpenAI Embedder",
    category="agno_embedder",
    icon="openai.svg",
    has_enabled_switch=False,
)
class OpenAIEmbedderNode(ServiceNode):
    """
    OpenAI embedder service for generating document vectors.
    Supports text-embedding-3-small, text-embedding-3-large, and text-embedding-ada-002.
    """

    # Model Configuration
    model_id: str = NodeVariableSettings(
        label="Model ID",
        dock=dock_property(select_values={
            "text-embedding-3-small": "text-embedding-3-small (1536 dims, fastest)",
            "text-embedding-3-large": "text-embedding-3-large (3072 dims, best quality)",
            "text-embedding-ada-002": "text-embedding-ada-002 (1536 dims, legacy)"
        }),
        default="text-embedding-3-small",
        info="OpenAI embedding model to use. Small is fastest, Large has best quality.",
    )

    dimensions: int | None = NodeVariableSettings(
        label="Dimensions",
        dock=True,
        info="Optional: Reduce embedding dimensions (only for text-embedding-3 models).",
    )

    # API Configuration
    api_key: str | None = NodeVariableSettings(
        label="API Key",
        dock=True,
        has_in=True,
        info="OpenAI API key.",
    )

    organization: str | None = NodeVariableSettings(
        label="Organization",
        dock=True,
        info="Optional: OpenAI organization ID.",
    )

    base_url: str | None = NodeVariableSettings(
        label="Base URL",
        dock=True,
        info="Optional: Custom API base URL for OpenAI-compatible endpoints.",
    )

    # Advanced Settings
    encoding_format: str = NodeVariableSettings(
        label="Encoding Format",
        dock=dock_property(select_values={
            "float": "float (standard)",
            "base64": "base64 (compressed)"
        }),
        default="float",
        info="Output format for embeddings. Float is standard, base64 is compressed.",
    )

    user: str | None = NodeVariableSettings(
        label="User ID",
        dock=True,
        info="Optional: Unique identifier for end-user tracking.",
    )

    # Output
    embedder_instance: Embedder | None = NodeVariableSettings(
        label="Embedder Instance",
        has_out=True,
        info="OpenAI embedder instance for use in vector databases",
    )

    async def provide_instance(self) -> Embedder:
        """Create and return OpenAI embedder instance."""
        
        # Create OpenAI embedder with configuration
        self.embedder_instance = OpenAIEmbedder(
            id=self.model_id,
            dimensions=self.dimensions,
            api_key=self.api_key,
            organization=self.organization,
            base_url=self.base_url if self.base_url else None,
            encoding_format=self.encoding_format,  # type: ignore
            user=self.user,
        )
        
        return self.embedder_instance