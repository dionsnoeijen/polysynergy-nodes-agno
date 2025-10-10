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

    # Keep track of MCP toolkits for dynamic mapping
    mcp_toolkits = []

    # Add regular tools
    for item in tool_info_list:
        maybe_tool = item["tool"]
        node_id = item["node_id"]

        print(f"\n🔧 BUILD TOOL MAPPING: Processing node {node_id}")
        print(f"   Type of maybe_tool: {type(maybe_tool)}")

        # Handle async tools
        import inspect
        toolkit = await maybe_tool if inspect.iscoroutine(maybe_tool) else maybe_tool
        tool_instances.append(toolkit)

        print(f"   Type of toolkit: {type(toolkit)}")
        print(f"   Has .tools attribute: {hasattr(toolkit, 'tools')}")

        # Check if this is an MCP toolkit (tools loaded dynamically)
        toolkit_type_name = type(toolkit).__name__
        is_mcp = toolkit_type_name == "MCPTools"

        if is_mcp:
            print(f"   ⚡ Detected MCPTools instance - will map dynamically")
            mcp_toolkits.append({"toolkit": toolkit, "node_id": node_id})

        # Map function names to node IDs for tracking
        if hasattr(toolkit, "tools"):
            tools_list = toolkit.tools if toolkit.tools else []
            print(f"   Number of tools in toolkit: {len(tools_list)}")

            for tool in tools_list:
                fn_name = (
                    getattr(tool, "name", None)
                    or getattr(getattr(tool, "fn", None), "__name__", None)
                    or getattr(tool, "__name__", None)
                )
                if fn_name:
                    print(f"   ✓ Mapping tool '{fn_name}' -> {node_id}")
                    function_name_to_node_id[fn_name] = node_id
                else:
                    print(f"   ✗ Could not extract name from tool: {type(tool)}")
        else:
            print(f"   ✗ Toolkit has no .tools attribute")

    # Add path tools (flow tools)
    for path_tool in path_tools or []:
        tool_instances.append(path_tool)
        # Path tools are Agno Function objects with name attribute
        if hasattr(path_tool, 'name'):
            function_name_to_node_id[path_tool.name] = f"path_tool_{path_tool.name}"

    print(f"\n📋 MAPPING SUMMARY:")
    print(f"   Total tool instances: {len(tool_instances)}")
    print(f"   MCP toolkits detected: {len(mcp_toolkits)}")
    print(f"   Static mappings: {list(function_name_to_node_id.keys())}")

    return tool_instances, function_name_to_node_id, mcp_toolkits