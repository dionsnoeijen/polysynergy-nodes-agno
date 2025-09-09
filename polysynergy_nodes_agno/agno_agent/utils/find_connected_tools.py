from agno.tools import Toolkit
from polysynergy_node_runner.setup_context.node import Node
from .find_connected_service import find_connected_service


async def find_connected_tools(node: Node) -> list[dict]:
    """Find all connected tool nodes and return their instances."""
    tool_connections = [c for c in node.get_out_connections() if c.target_handle == "agent_or_team"]

    tools = []
    for conn in tool_connections:
        # Note: This uses target_node_id since tools connect FROM agents TO tool nodes
        target_node = node.state.get_node_by_id(conn.target_node_id)
        
        # For tools, we need to handle the service discovery on the target node
        if hasattr(target_node, "provide_instance"):
            try:
                tool_instance = await target_node.provide_instance()
                tools.append({
                    "node_id": target_node.id,
                    "tool": tool_instance
                })
            except Exception as e:
                print(f"[ERROR] instantiating tool from node {target_node.id}: {e}")
                pass  # Skip tools that can't be instantiated

    return tools