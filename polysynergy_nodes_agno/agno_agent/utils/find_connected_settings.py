from polysynergy_node_runner.setup_context.node import Node

def find_connected_settings(node: Node) -> dict:
    settings_connections = [
        c for c in node.get_in_connections()
        if c.target_handle.lower().startswith("settings.")
    ]

    settings = {}
    for conn in settings_connections:
        source_node = node.state.get_node_by_id(conn.source_node_id)
        key = conn.target_handle.split(".", 1)[-1]
        settings[key] = source_node.provide_instance()

    return settings