from agno.knowledge import AgentKnowledge
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.base import VectorDb
from polysynergy_node_runner.setup_context.dock_property import dock_property, dock_dict
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode
from polysynergy_node_runner.execution_context.is_compatible_provider import is_compatible_provider


@node(
    name="PDF URL Knowledge Base",
    category="agno_knowledge",
    icon="brain.svg",
    has_enabled_switch=False,
)
class PDFUrlKnowledge(ServiceNode):
    """
    PDF URL-based knowledge base for Agno agents.
    Loads PDF documents from URLs with metadata for filtering.
    """

    # Vector Database Input (connected from vector DB service nodes)
    vector_db: VectorDb | None = NodeVariableSettings(
        label="Vector Database",
        dock=True,
        has_in=True,
        info="Vector database service to store document embeddings (e.g., LanceDB, Qdrant).",
    )

    # PDF URLs with metadata
    urls: list[dict[str, any]] = NodeVariableSettings(
        label="PDF URLs",
        has_in=True,
        dock=dock_dict(
            key_label="URL",
            value_label="Metadata",
            info="List of PDF URLs with optional metadata for filtering."
        ),
        default=[],
        info="PDF URLs to load with optional metadata (cuisine, source, region, etc.)",
    )

    # Knowledge Base Configuration
    num_documents: int | None = NodeVariableSettings(
        label="Max Documents",
        dock=True,
        info="Maximum number of documents to load (optional limit).",
    )

    optimize_on: str | None = NodeVariableSettings(
        label="Optimize On",
        dock=dock_property(select_values={
            "accuracy": "accuracy",
            "latency": "latency",
            "cost": "cost"
        }),
        default="accuracy",
        info="Optimization preference: accuracy, latency, or cost.",
    )

    chunking_strategy: str | None = NodeVariableSettings(
        label="Chunking Strategy", 
        dock=dock_property(select_values={
            "basic": "basic",
            "by_title": "by_title",
            "sentence": "sentence"
        }),
        default="basic",
        info="How to split documents into chunks for embedding.",
    )

    formats: list[str] | None = NodeVariableSettings(
        label="Supported Formats",
        dock=True,
        default=["pdf"],
        info="Document formats to process (default: pdf).",
    )

    # Output
    knowledge_base_instance: AgentKnowledge | None = NodeVariableSettings(
        label="Knowledge Base Instance",
        has_out=True,
        info="PDF URL knowledge base instance for use in agents",
    )

    async def _find_connected_vector_db(self) -> VectorDb | None:
        """Find connected vector database from input connections."""
        vector_db_connections = [c for c in self.get_in_connections() if c.target_handle == "vector_db"]
        
        for conn in vector_db_connections:
            vector_db_node = self.state.get_node_by_id(conn.source_node_id)
            if hasattr(vector_db_node, "provide_instance") and is_compatible_provider(vector_db_node, VectorDb):
                return await vector_db_node.provide_instance()
        
        return None

    async def provide_instance(self) -> AgentKnowledge:
        """Create and return PDF URL knowledge base instance."""
        
        # Get connected vector database
        vector_db = await self._find_connected_vector_db()
        if not vector_db:
            raise ValueError("No vector database connected. Please connect a vector database service node.")

        # Convert URLs from dock format to expected format
        formatted_urls = []
        if self.urls:
            for url_item in self.urls:
                if isinstance(url_item, dict):
                    # Extract URL and metadata from dock dict format
                    url = url_item.get("key", "")
                    metadata_str = url_item.get("value", "{}")
                    
                    # Parse metadata if it's a string
                    if isinstance(metadata_str, str):
                        try:
                            import json
                            metadata = json.loads(metadata_str) if metadata_str.strip() else {}
                        except:
                            metadata = {}
                    else:
                        metadata = metadata_str or {}
                    
                    if url:
                        formatted_urls.append({
                            "url": url,
                            "metadata": metadata
                        })

        # Prepare constructor arguments
        kwargs = {
            "urls": formatted_urls,
            "vector_db": vector_db,
        }

        # Add optional parameters if provided
        if self.num_documents is not None:
            kwargs["num_documents"] = self.num_documents
        if self.optimize_on:
            kwargs["optimize_on"] = self.optimize_on
        if self.chunking_strategy:
            kwargs["chunking_strategy"] = self.chunking_strategy
        if self.formats:
            kwargs["formats"] = self.formats

        # Create PDF URL knowledge base instance
        self.knowledge_base_instance = PDFUrlKnowledgeBase(**kwargs)
        return self.knowledge_base_instance
