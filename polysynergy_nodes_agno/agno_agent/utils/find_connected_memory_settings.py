from polysynergy_node_runner.setup_context.node import Node


def find_connected_memory_settings(node: Node) -> dict:
    """Find and return memory settings from connected memory node."""
    memory_connections = [c for c in node.get_in_connections() if c.target_handle == "memory"]

    for conn in memory_connections:
        memory_node = node.state.get_node_by_id(conn.source_node_id)
        if hasattr(memory_node, "provide_memory_settings"):
            return memory_node.provide_memory_settings()

    # Return default settings if no memory node is connected
    return {
        'enable_agentic_memory': False,
        'enable_user_memories': False,
        'create_user_memories': False,
        'enable_session_summaries': False,
        'create_session_summary': False,
    }