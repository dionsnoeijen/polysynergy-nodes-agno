from agno.knowledge.agent import AgentKnowledge
from polysynergy_node_runner.setup_context.node import Node
from polysynergy_node_runner.execution_context.is_compatible_provider import is_compatible_provider


async def find_connected_knowledge_base(node: Node) -> AgentKnowledge | None:
    """Find and return connected knowledge base instance from connected knowledge provider nodes."""
    knowledge_connections = [c for c in node.get_in_connections() if c.target_handle == "knowledge"]

    for conn in knowledge_connections:
        knowledge_node = node.state.get_node_by_id(conn.source_node_id)
        if hasattr(knowledge_node, "provide_instance"):
            # Check if it provides any type that inherits from AgentKnowledge
            knowledge_instance = await knowledge_node.provide_instance()
            if isinstance(knowledge_instance, AgentKnowledge):
                return knowledge_instance

    return None