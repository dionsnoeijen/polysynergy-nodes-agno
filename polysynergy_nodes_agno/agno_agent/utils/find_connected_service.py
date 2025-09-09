import string
from typing import TypeVar, Type, Optional
from polysynergy_node_runner.setup_context.node import Node
from polysynergy_node_runner.execution_context.is_compatible_provider import is_compatible_provider

T = TypeVar('T')


async def find_connected_service(node: Node, target_handle: str, expected_type: Type[T]) -> Optional[T]:
    """
    Generic service finder that handles both regular nodes and GroupNodes.
    
    Args:
        node: The node to search for connected services
        target_handle: The handle to look for (e.g., "storage", "memory", "knowledge")
        expected_type: The expected service type (e.g., Storage, Memory, AgentKnowledge)
    
    Returns:
        The service instance if found, None otherwise
    """
    connections = [c for c in node.get_in_connections() if c.target_handle == target_handle]
    
    for conn in connections:
        service_node = node.state.get_node_by_id(conn.source_node_id)

        if hasattr(service_node, "provide_instance"):
            return await service_node.provide_instance()

        if _is_group_node(service_node):
            actual_service_node = await _find_service_in_group(
                service_node, conn.source_handle, expected_type, node.state
            )

            print(f"[find_connected_service] Inside GroupNode "
                  f"'{service_node.handle}', found actual service node: "
                  f"{actual_service_node.handle if actual_service_node else 'None'}"
                  f" for handle '{conn.source_handle}'"
                  f" expecting type '{expected_type.__name__}'"
                  f" from connection '{conn.source_node_id}.{conn.source_handle}' -> '{conn.target_node_id}.{conn.target_handle}'")

            if actual_service_node:
                return await actual_service_node.provide_instance()
    return None


def _is_group_node(node) -> bool:
    """Detect if node is a GroupNode by class name pattern."""
    return node.__class__.__name__.startswith("GroupNode_")


async def _find_service_in_group(group_node, source_handle: str, expected_type: Type[T], state) -> Optional[Node]:
    """
    Find the actual service provider inside a GroupNode.
    
    The GroupNode has properties like 'a_instance' where 'a' is the prefix for the internal node
    and 'instance' is the original handle. We need to find which internal node this maps to.
    """
    # Parse the prefixed handle (e.g., "a_instance" -> prefix="a", handle="instance")
    if "_" not in source_handle:
        return None
        
    prefix, original_handle = source_handle.split("_", 1)
    
    # Find all connections that target this group (connections going INTO the group)
    group_input_connections = _get_group_input_connections(group_node.id, state)
    
    # Build prefix mapping (same as code generation: a=first_node, b=second_node, etc.)
    prefix_to_node_id = {}
    unique_source_nodes = []
    for conn in group_input_connections:
        if conn.source_node_id not in unique_source_nodes:
            unique_source_nodes.append(conn.source_node_id)
    
    for i, node_id in enumerate(unique_source_nodes):
        prefix_to_node_id[string.ascii_lowercase[i]] = node_id
    
    # Find the target node by prefix
    if prefix not in prefix_to_node_id:
        return None
        
    target_node_id = prefix_to_node_id[prefix]
    internal_node = state.get_node_by_id(target_node_id)
    
    # Special handling based on expected type
    if expected_type == object:
        # For object type (settings), bypass broken type checking
        if hasattr(internal_node, "provide_instance"):
            return internal_node
    else:
        # For specific types, try type check but fall back if it fails
        if hasattr(internal_node, "provide_instance"):
            try:
                if is_compatible_provider(internal_node, expected_type):
                    return internal_node
            except Exception:
                # Type check failed due to import issues, trust the connection
                return internal_node
                
    return None


def _get_group_input_connections(group_id: str, state):
    """Get all connections that feed into the group."""
    return [c for c in state.connections if c.target_node_id == group_id]