from polysynergy_node_runner.setup_context.node import Node


def find_connected_storage_settings(node: Node, for_team: bool = False) -> dict:
    """Find and return storage settings from connected storage node."""
    storage_connections = [c for c in node.get_in_connections() if c.target_handle == "storage"]

    settings = None
    for conn in storage_connections:
        storage_node = node.state.get_node_by_id(conn.source_node_id)
        if hasattr(storage_node, "provide_storage_settings"):
            settings = storage_node.provide_storage_settings()
            break

    if settings is None:
        settings = {
            'add_history_to_messages': False,
            'num_history_runs': 0,
            'read_chat_history': False,
        }

    # strip alleen bij team
    if for_team and 'read_chat_history' in settings:
        settings = dict(settings)  # kopie maken
        settings.pop('read_chat_history', None)

    return settings