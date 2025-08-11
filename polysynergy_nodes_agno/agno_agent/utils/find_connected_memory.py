from agno.memory import AgentMemory
from polysynergy_node_runner.setup_context.node import Node
from polysynergy_node_runner.execution_context.is_compatible_provider import is_compatible_provider


def find_connected_memory(node: Node) -> AgentMemory | None:
    memory_connections = [c for c in node.get_in_connections() if c.target_handle == "memory"]

    for conn in memory_connections:
        memory_node = node.state.get_node_by_id(conn.source_node_id)
        if hasattr(memory_node, "provide_instance") and is_compatible_provider(memory_node, AgentMemory):
            return memory_node.provide_instance()

    return None