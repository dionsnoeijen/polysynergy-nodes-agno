from typing import Dict, List, Any


async def build_tool_mapping(tool_info_list: List[Dict[str, Any]], path_tools: List[Any] = None) -> tuple[List[Any], Dict[str, str]]:
    """
    Builds tool instances and creates a mapping of function names to node IDs.
    
    Args:
        tool_info_list: List of tool information containing tools and their node IDs
        path_tools: Optional list of path tools (flow tools)
        
    Returns:
        Tuple of (tool_instances, function_name_to_node_id_mapping)
    """
    tool_instances = []
    function_name_to_node_id = {}
    
    # Add regular tools
    for item in tool_info_list:
        maybe_tool = item["tool"]
        # Handle async tools
        import inspect
        toolkit = await maybe_tool if inspect.iscoroutine(maybe_tool) else maybe_tool
        tool_instances.append(toolkit)

        # Map function names to node IDs for tracking
        if hasattr(toolkit, "tools"):
            for tool in toolkit.tools:
                fn_name = (
                    getattr(tool, "name", None)
                    or getattr(getattr(tool, "fn", None), "__name__", None)
                    or getattr(tool, "__name__", None)
                )
                if fn_name:
                    function_name_to_node_id[fn_name] = item["node_id"]

    # Add path tools (flow tools)
    for path_tool in path_tools or []:
        tool_instances.append(path_tool)
        # Path tools are Agno Function objects with name attribute
        if hasattr(path_tool, 'name'):
            function_name_to_node_id[path_tool.name] = f"path_tool_{path_tool.name}"
    
    return tool_instances, function_name_to_node_id