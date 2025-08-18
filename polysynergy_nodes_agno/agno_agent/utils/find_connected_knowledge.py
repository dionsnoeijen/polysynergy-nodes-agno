from agno.knowledge import AgentKnowledge
from polysynergy_node_runner.setup_context.node import Node
from polysynergy_node_runner.execution_context.is_compatible_provider import is_compatible_provider


async def find_connected_knowledge(node: Node) -> AgentKnowledge | None:
    knowledge_connections = [c for c in node.get_in_connections() if c.target_handle == "knowledge"]

    for conn in knowledge_connections:
        knowledge_node = node.state.get_node_by_id(conn.source_node_id)
        if hasattr(knowledge_node, "provide_instance") and is_compatible_provider(knowledge_node, AgentKnowledge):
            return await knowledge_node.provide_instance()

    return None