from typing import Optional, Dict, Any
from polysynergy_node_runner.setup_context.node import Node

PROMPT_NODE_PATH = 'polysynergy_nodes.play.prompt.Prompt'


def find_connected_prompt(node: Node) -> Optional[Dict[str, Any]]:
    """
    Find connected prompt node and extract session/user data.
    
    Returns prompt data that overrides agent's manual settings:
    - user_id: from prompt node's active_user property
    - session_id: from prompt node's active_session property  
    - session_name: from prompt node's session dict[active_session]
    
    Returns None if no prompt connected or data incomplete.
    """
    # Find all input connections to this agent/team node
    connections = node.get_in_connections()
    
    for conn in connections:
        source_node = node.state.get_node_by_id(conn.source_node_id)
        
        # Check if source node is a prompt node
        if source_node and source_node.path == PROMPT_NODE_PATH:
            return _extract_prompt_data(source_node)
    
    return None


def _extract_prompt_data(prompt_node: Node) -> Optional[Dict[str, Any]]:
    """Extract session/user data from prompt node properties."""
    
    # Get required data from prompt node properties directly
    active_user = getattr(prompt_node, 'active_user', None)
    active_session = getattr(prompt_node, 'active_session', None)
    session_dict = getattr(prompt_node, 'session', {}) or {}
    
    # Session is optional but if we have no data at all, return None
    if not active_user and not active_session:
        return None
    
    # Extract session name from session dict
    # session_dict could be a dict or a list of NodeVariable-like objects
    session_name = None
    if isinstance(session_dict, dict):
        session_name = session_dict.get(active_session)
    elif isinstance(session_dict, list):
        # Handle case where session is a list of objects with handle/value
        session_item = next((item for item in session_dict if getattr(item, 'handle', None) == active_session), None)
        if session_item:
            session_name = getattr(session_item, 'value', None)
    
    return {
        'user_id': active_user,
        'session_id': active_session,
        'session_name': session_name,
        'prompt_node_id': prompt_node.id
    }