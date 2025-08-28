from polysynergy_node_runner.setup_context.node import Node
from .find_connected_service import find_connected_service


async def find_connected_settings(node: Node) -> dict:
    """Find and return all connected settings using the smart service finder."""
    settings_connections = [
        c for c in node.get_in_connections()
        if c.target_handle.lower().startswith("settings.")
    ]

    settings = {}
    for conn in settings_connections:
        key = conn.target_handle.split(".", 1)[-1]

        print('CONN, TARGET HANDLE', conn.target_handle)

        # Use the generic service finder for each settings connection
        # Using object as the expected type since settings can be various types
        settings_instance = await find_connected_service(node, conn.target_handle, object)
        if settings_instance:
            settings[key] = settings_instance

        print('FOUND SETTINGS INSTANCE', settings_instance)

    return settings