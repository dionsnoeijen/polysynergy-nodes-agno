from agno.storage.base import Storage
from polysynergy_node_runner.setup_context.node import Node
from polysynergy_node_runner.execution_context.is_compatible_provider import is_compatible_provider


async def find_connected_storage(node: Node) -> Storage | None:
    """Find and return storage from connected storage node."""
    storage_connections = [c for c in node.get_in_connections() if c.target_handle == "storage"]

    for conn in storage_connections:
        storage_node = node.state.get_node_by_id(conn.source_node_id)
        if hasattr(storage_node, "provide_instance") and is_compatible_provider(storage_node, Storage):
            return await storage_node.provide_instance()

    return None