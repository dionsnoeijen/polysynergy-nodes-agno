from polysynergy_node_runner.setup_context.node import Node


def find_connected_chat_play_agent(node: Node):
    chatplayagetnconnections = [c for c in node.get_in_connections() if c.target_handle == "node"]

    instances = []
    for conn in chatplayagetnconnections:
        node = node.state.get_node_by_id(conn.source_node_id)
        if node.__class__.__name__.tolower() == "chatplayagent":
            instances.append(node)

    return instances