from typing import Optional, Dict, Any
from polysynergy_node_runner.setup_context.node import Node

PROMPT_NODE_PATH = 'polysynergy_nodes.play.prompt.Prompt'


def find_connected_prompt(node: Node) -> Optional[Dict[str, Any]]:
    """
    Find connected prompt node and extract session/user data.
    
    Returns prompt data that overrides agent's manual settings:
    - user_id: from prompt.active_user
    - session_id: from prompt.active_session  
    - session_name: from prompt.session[active_session] (dict value)
    
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
    """Extract session/user data from prompt node variables."""
    
    def get_variable_value(handle: str):
        """Get value of variable by handle."""
        var = next((v for v in prompt_node.variables if v.handle == handle), None)
        return var.value if var else None
    
    # Get required data from prompt node
    active_user = get_variable_value('active_user')
    active_session = get_variable_value('active_session')
    session_dict = get_variable_value('session') or {}
    
    # Must have both active user and session to override
    if not active_user or not active_session:
        return None
    
    # Extract session name from session dict
    session_name = session_dict.get(active_session) if isinstance(session_dict, dict) else None
    
    return {
        'user_id': active_user,
        'session_id': active_session,
        'session_name': session_name,
        'prompt_node_id': prompt_node.id
    }