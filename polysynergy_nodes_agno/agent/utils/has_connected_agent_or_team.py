from polysynergy_node_runner.setup_context.node import Node


def has_connected_agent_or_team(node: Node) -> bool:
    agent_or_team_connections = [c for c in node.get_in_connections()
                                 if c.target_handle == "agent_or_team"
                                 and c.source_handle == "members"]

    print('AGENT OR TEAM CONNECTIONS:', agent_or_team_connections)

    return len(agent_or_team_connections) > 0