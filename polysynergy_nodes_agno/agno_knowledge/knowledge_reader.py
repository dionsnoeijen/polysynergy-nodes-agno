from agno.knowledge import AgentKnowledge
from agno.vectordb.base import VectorDb
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode
from polysynergy_node_runner.execution_context.is_compatible_provider import is_compatible_provider


@node(
    name="Knowledge Reader",
    category="agno_knowledge",
    icon="brain.svg",
    has_enabled_switch=False,
)
class KnowledgeReader(ServiceNode):
    """
    Vector database agnostic knowledge reader for existing collections.
    This node does NOT load any documents - it only provides read access
    to existing knowledge for agent queries.
    
    Use this when:
    - Knowledge has already been loaded in a separate flow
    - You only need to query existing knowledge
    - You want to avoid reloading documents on every agent execution
    
    Works with any vector database (Qdrant, LanceDB, etc.)
    """

    # Vector Database Input (connected from any vector DB service node)
    vector_db: VectorDb | None = NodeVariableSettings(
        label="Vector Database",
        has_in=True,
        info="Vector database service with existing knowledge data (e.g., Qdrant, LanceDB).",
    )

    # Output
    knowledge_base_instance: AgentKnowledge | None = NodeVariableSettings(
        label="Knowledge Base Instance",
        has_out=True,
        type="agno.knowledge.agent.AgentKnowledge",
        info="Knowledge base instance for use in agents (read-only access to existing data)",
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
        """Create and return a knowledge base instance connected to existing vector database."""
        
        print(f"[KnowledgeReader] Starting knowledge reader for existing data")
        
        # Get connected vector database
        vector_db = await self._find_connected_vector_db()
        if not vector_db:
            print(f"[KnowledgeReader] ERROR: No vector database connected")
            raise ValueError("No vector database connected. Please connect a vector database service node with existing knowledge data.")
        
        print(f"[KnowledgeReader] Connected to vector database: {type(vector_db).__name__}")
        
        # Create a minimal PDFUrlKnowledgeBase instance
        # We pass empty URLs since we're not loading any documents
        # The knowledge base will only be used for queries against existing data

        # in je node.provide_instance()
        self.knowledge_base_instance = AgentKnowledge(
            reader=None,
            vector_db=vector_db,
            num_documents=5
        )

        # Enable debug logging to see if queries are happening
        print(f"[KnowledgeReader] Vector DB search_type: {getattr(vector_db, 'search_type', 'unknown')}")
        print(f"[KnowledgeReader] Vector DB collection: {getattr(vector_db, 'collection', 'unknown')}")
        
        print(f"[KnowledgeReader] Knowledge reader ready - read-only access to existing knowledge")
        print(f"[KnowledgeReader] Vector DB type: {type(vector_db).__name__}")
        
        return self.knowledge_base_instance