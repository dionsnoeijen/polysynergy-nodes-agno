from agno.knowledge import AgentKnowledge
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.path_settings import PathSettings
from polysynergy_node_runner.setup_context.node import Node
from polysynergy_node_runner.execution_context.is_compatible_provider import is_compatible_provider


@node(
    name="Knowledge Base Load",
    category="agno_knowledge",
    icon="brain.svg",
    has_enabled_switch=False,
)
class KnowledgeBaseLoad(Node):
    """
    Load/index documents into a knowledge base.
    Separate flow for data ingestion without requiring an agent.
    """

    # Input
    knowledge_base: AgentKnowledge | None = NodeVariableSettings(
        label="Knowledge Base",
        dock=True,
        has_in=True,
        info="Knowledge base to load documents into (e.g., PDFUrlKnowledgeBase).",
    )

    recreate: bool = NodeVariableSettings(
        label="Recreate Collection",
        dock=True,
        default=False,
        info="If True, recreates the collection in the vector database.",
    )

    upsert: bool = NodeVariableSettings(
        label="Upsert Documents",
        dock=True,
        default=False,
        info="If True, upserts documents to the vector database (update existing or insert new).",
    )

    skip_existing: bool = NodeVariableSettings(
        label="Skip Existing",
        dock=True,
        default=True,
        info="If True, skips documents which already exist in the vector database when inserting.",
    )

    # Output paths
    true_path: bool | str = PathSettings("Success", info="Path taken when documents are loaded successfully.")
    false_path: bool | str = PathSettings("Error", info="Path taken when loading fails.")

    async def _find_connected_knowledge_base(self) -> AgentKnowledge | None:
        """Find connected knowledge base from input connections."""
        knowledge_connections = [c for c in self.get_in_connections() if c.target_handle == "knowledge_base"]
        
        for conn in knowledge_connections:
            knowledge_node = self.state.get_node_by_id(conn.source_node_id)
            if hasattr(knowledge_node, "provide_instance"):
                knowledge_instance = await knowledge_node.provide_instance()
                if isinstance(knowledge_instance, AgentKnowledge):
                    return knowledge_instance
        
        return None

    async def execute(self):
        """Load documents into the knowledge base."""
        try:
            # Get connected knowledge base
            knowledge_base = await self._find_connected_knowledge_base()
            if not knowledge_base:
                self.false_path = "No knowledge base connected. Please connect a knowledge base node."
                return

            # Load documents into the knowledge base with all parameters
            knowledge_base.load(
                recreate=self.recreate,
                upsert=self.upsert,
                skip_existing=self.skip_existing
            )
            
            self.true_path = f"Successfully loaded documents (recreate={self.recreate}, upsert={self.upsert}, skip_existing={self.skip_existing})"
            
        except Exception as e:
            self.false_path = f"Failed to load knowledge base: {str(e)}"