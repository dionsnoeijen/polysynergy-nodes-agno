from agno.guardrails import BaseGuardrail


def find_connected_guardrails(node) -> list[BaseGuardrail]:
    """
    Find all connected guardrail instances from the agent node.

    Returns:
        List of BaseGuardrail instances
    """
    guardrail_instances = []

    # Get all connections to the 'guardrails' handle
    connections = [c for c in node.get_in_connections() if c.target_handle == 'guardrails']

    for conn in connections:
        source_node = node.state.get_node_by_id(conn.source_node_id)

        # Get the guardrail instance from the source node
        if hasattr(source_node, 'instance'):
            instance = getattr(source_node, 'instance', None)
            if instance and isinstance(instance, BaseGuardrail):
                guardrail_instances.append(instance)
                print(f"[Guardrails] Added {type(instance).__name__}")

    if guardrail_instances:
        print(f"[Guardrails] Total guardrails connected: {len(guardrail_instances)}")

    return guardrail_instances
