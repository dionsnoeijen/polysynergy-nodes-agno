from typing import Optional

from agno.vectordb.lancedb import LanceDb
from agno.vectordb.base import VectorDb
from agno.embedder.base import Embedder
from agno.reranker.base import Reranker
from agno.vectordb.search import SearchType
from agno.vectordb.distance import Distance
from polysynergy_node_runner.setup_context.dock_property import dock_property
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode
from polysynergy_node_runner.execution_context.is_compatible_provider import is_compatible_provider


@node(
    name="LanceDB Vector Database",
    category="agno_vectordb",
    icon="lancedb.svg",
    has_enabled_switch=False,
)
class LanceDBVectorDB(ServiceNode):
    """
    LanceDB vector database service for use with knowledge bases.
    High-performance vector database built on Apache Arrow.
    """

    # Core Configuration
    uri: str = NodeVariableSettings(
        label="Database URI",
        dock=True,
        default="/tmp/lancedb",
        info="LanceDB database URI. Use local path or remote URI for cloud deployments.",
    )

    table_name: str = NodeVariableSettings(
        label="Table Name", 
        dock=True,
        default="knowledge",
        info="Name of the LanceDB table to store knowledge vectors.",
    )

    api_key: str | None = NodeVariableSettings(
        label="API Key",
        dock=True,
        info="API key for LanceDB Cloud (optional for local databases).",
    )

    # Connected Services (these come from other nodes)
    embedder: Embedder | None = NodeVariableSettings(
        label="Embedder",
        dock=True,
        has_in=True,
        info="Embedder service to use for generating document vectors.",
    )

    reranker: Reranker | None = NodeVariableSettings(
        label="Reranker",
        dock=True,
        has_in=True,
        info="Reranker service to reorder search results by relevance.",
    )

    # Search Configuration
    search_type: str = NodeVariableSettings(
        label="Search Type",
        dock=dock_property(select_values={
            "vector": "vector",
            "keyword": "keyword", 
            "hybrid": "hybrid"
        }),
        default="vector",
        info="Type of search to perform: vector (semantic), keyword (text), or hybrid.",
    )

    distance: str = NodeVariableSettings(
        label="Distance Metric",
        dock=dock_property(select_values={
            "cosine": "cosine",
            "l2": "l2",
            "max_inner_product": "max_inner_product"
        }),
        default="cosine", 
        info="Distance metric for vector similarity search.",
    )

    nprobes: int = NodeVariableSettings(
        label="Number of Probes",
        dock=True,
        default=20,
        info="Number of partitions to search. Higher = better recall but slower.",
    )

    # Advanced Configuration
    use_tantivy: bool = NodeVariableSettings(
        label="Use Tantivy Search",
        dock=True,
        default=True,
        info="Enable Tantivy full-text search for hybrid vector + text search.",
    )

    on_bad_vectors: str = NodeVariableSettings(
        label="Bad Vector Handling",
        dock=dock_property(select_values={
            "error": "error",
            "drop": "drop", 
            "fill": "fill",
            "null": "null"
        }),
        default="error",
        info="How to handle invalid vectors: error, drop, fill with value, or set to null.",
    )

    fill_value: float = NodeVariableSettings(
        label="Fill Value",
        dock=True,
        default=0.0,
        info="Value to use when on_bad_vectors is set to 'fill'.",
    )

    # Output
    vector_db_instance: VectorDb | None = NodeVariableSettings(
        label="Vector Database Instance",
        has_out=True,
        info="LanceDB vector database instance for use in knowledge bases",
    )

    async def _find_connected_embedder(self) -> Embedder | None:
        """Find connected embedder service from input connections."""
        embedder_connections = [c for c in self.get_in_connections() if c.target_handle == "embedder"]
        
        for conn in embedder_connections:
            embedder_node = self.state.get_node_by_id(conn.source_node_id)
            if hasattr(embedder_node, "provide_instance") and is_compatible_provider(embedder_node, Embedder):
                return await embedder_node.provide_instance()
        
        return None

    async def _find_connected_reranker(self) -> Reranker | None:
        """Find connected reranker service from input connections."""
        reranker_connections = [c for c in self.get_in_connections() if c.target_handle == "reranker"]
        
        for conn in reranker_connections:
            reranker_node = self.state.get_node_by_id(conn.source_node_id)
            if hasattr(reranker_node, "provide_instance") and is_compatible_provider(reranker_node, Reranker):
                return await reranker_node.provide_instance()
        
        return None

    async def provide_instance(self) -> VectorDb:
        """Create and return LanceDB vector database instance."""
        
        # Find connected embedder and reranker services
        connected_embedder = await self._find_connected_embedder()
        connected_reranker = await self._find_connected_reranker()
        
        # Use connected services if available, otherwise use property values
        embedder_to_use = connected_embedder or self.embedder
        reranker_to_use = connected_reranker or self.reranker
        
        # Convert string enums to proper enum types
        search_type_enum = None
        if self.search_type:
            search_type_map = {
                "vector": SearchType.vector,
                "keyword": SearchType.keyword,
                "hybrid": SearchType.hybrid
            }
            search_type_enum = search_type_map.get(self.search_type)

        distance_enum = None
        if self.distance:
            distance_map = {
                "cosine": Distance.cosine,
                "l2": Distance.l2,
                "max_inner_product": Distance.max_inner_product
            }
            distance_enum = distance_map.get(self.distance)
        
        # Create LanceDB instance with full configuration
        self.vector_db_instance = LanceDb(
            uri=self.uri,
            table_name=self.table_name,
            api_key=self.api_key,
            embedder=embedder_to_use,
            search_type=search_type_enum,
            distance=distance_enum,
            nprobes=self.nprobes,
            reranker=reranker_to_use,
            use_tantivy=self.use_tantivy,
            on_bad_vectors=self.on_bad_vectors,
            fill_value=self.fill_value,
        )
        
        return self.vector_db_instance
