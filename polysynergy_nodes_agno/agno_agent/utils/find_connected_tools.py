from agno.tools import Toolkit
from polysynergy_node_runner.setup_context.node import Node

from polysynergy_node_runner.execution_context.is_compatible_provider import is_compatible_provider


def find_connected_tools(node: Node) -> list[dict]:
    tool_connections = [c for c in node.get_out_connections() if c.target_handle == "agent_or_team"]

    tools = []
    for conn in tool_connections:
        target_node = node.state.get_node_by_id(conn.target_node_id)
        if hasattr(target_node, "provide_instance") and is_compatible_provider(target_node, Toolkit):
            tools.append({
                "node_id": target_node.id,
                "tool": target_node.provide_instance()
            })

    return tools