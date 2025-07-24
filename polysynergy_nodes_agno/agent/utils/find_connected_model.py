from agno.models.base import Model
from polysynergy_node_runner.setup_context.node import Node
from polysynergy_node_runner.execution_context.is_compatible_provider import is_compatible_provider


def find_connected_model(node: Node) -> Model | None:
    client_connections = [c for c in node.get_in_connections() if c.target_handle == "model"]

    for conn in client_connections:
        node = node.state.get_node_by_id(conn.source_node_id)
        if hasattr(node, "provide_instance") and is_compatible_provider(node, Model):
            return node.provide_instance()

    return None
