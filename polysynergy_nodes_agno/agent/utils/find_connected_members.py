from agno.agent import Agent
from agno.team import Team

from polysynergy_node_runner.setup_context.node import Node
from polysynergy_node_runner.execution_context.is_compatible_provider import is_compatible_provider

async def find_connected_members(node: Node) -> list | None:
    member_connections = [c for c in node.get_out_connections() if c.target_handle == "agent_or_team"]

    members = []
    for conn in member_connections:
        target_node = node.state.get_node_by_id(conn.target_node_id)

        if not hasattr(target_node, "provide_instance"):
            continue

        await node.flow.execute_node(target_node)

        if is_compatible_provider(target_node, Agent | Team):
            members.append({
                "node_id": target_node.id,
                "member": await target_node.provide_instance()
            })

    return members
