from uuid import uuid4
import json

from agno.tools import tool, Function
from polysynergy_node_runner.execution_context.flow_state import FlowState
from polysynergy_node_runner.setup_context.node import Node

from polysynergy_node_runner.execution_context.utils.traversal import find_nodes_until


def find_nodes_for_tool(start_node):
    return find_nodes_until(
        start_node=start_node,
        match_end_node_fn=lambda node: node.__class__.__name__.lower().startswith("agnotoolresult"),
        get_node_by_id=start_node.state.get_node_by_id
    )


def create_tool_and_invoke(node: Node, tool_node, agent=None) -> Function:
    # Use function_name if provided, otherwise fall back to handle
    function_name = getattr(tool_node, 'function_name', None) or tool_node.handle or "unnamed_tool"

    # Validate function_name matches OpenAI pattern
    import re
    if not re.match(r'^[a-zA-Z0-9_-]+$', function_name):
        print(f"WARNING: function_name '{function_name}' contains invalid characters. Using sanitized version.")
        function_name = re.sub(r'[^a-zA-Z0-9_-]', '_', function_name)
        if function_name and function_name[0].isdigit():
            function_name = f"tool_{function_name}"

    description = tool_node.description or tool_node.instructions or "No description."
    parameters = tool_node.parameters or {}

    # Build JSON schema for parameters
    schema = {
        "type": "object",
        "properties": {
            arg: {
                "type": "string",
                "description": desc.strip() if isinstance(desc, str) else str(desc)
            } for arg, desc in parameters.items()
        },
        "required": list(parameters.keys()),
        "additionalProperties": False
    }

    # Create the entrypoint function that will execute the flow
    async def flow_entrypoint(**kwargs):
        print(f'INVOKING AGNO TOOL: {function_name}', kwargs)
        
        try:
            start_node = node.state.get_node_by_id(tool_node.id)

            # Set arguments from function call into parameters dict
            for arg_name, value in kwargs.items():
                if hasattr(start_node, 'parameters') and isinstance(start_node.parameters, dict):
                    # Update the parameters dict with runtime value
                    start_node.parameters[arg_name] = value
                    print(f"Updated parameters['{arg_name}'] = {value}")
                else:
                    # Fallback: set as attribute if parameters dict doesn't exist
                    setattr(start_node, arg_name, value)
                    print(f"Set {arg_name} = {value} as attribute")
            
            # Find the nodes in the tool subflow
            nodes_for_tool, end_node = find_nodes_for_tool(start_node)
            
            print('START_NODE', start_node)
            print('END_NODE', end_node)
            print('TOOL NODES', [getattr(n, 'handle', 'no_handle') for n in nodes_for_tool])
            
            if not start_node or not end_node:
                return f"Could not resolve tool subflow for {handle}"
            
            # Resurrect all nodes in the tool path
            for node_for_tool in nodes_for_tool:
                node_for_tool.resurrect()
            
            # Enable the start node
            start_node.flow_state = FlowState.ENABLED
            
            # Add found_by connections
            for connection in start_node.get_in_connections():
                start_node.add_found_by(connection.uuid)
            
            # Execute the flow starting from this node
            await node.flow.execute_node(start_node)
            
            # Reset flow state
            start_node.flow_state = FlowState.PENDING
            
            print('RESULT', getattr(end_node, 'result', 'No result'))
            
            # Return the result from the end node
            return str(getattr(end_node, 'result', 'No result'))

        except Exception as e:
            print(f"[Error invoking agno tool {function_name}]: {str(e)}")
            return f"[Error executing tool {function_name}]: {str(e)}"

    # Create the Agno Function
    # Only include optional parameters if they have non-None values
    function_kwargs = {
        'name': function_name,
        'description': description,
        'parameters': schema,
        'entrypoint': flow_entrypoint,
    }

    # Add optional boolean parameters only if they exist and are not None
    optional_bool_attrs = ['strict', 'show_result', 'stop_after_tool_call',
                           'requires_confirmation', 'requires_user_input', 'external_execution']
    for attr in optional_bool_attrs:
        value = getattr(tool_node, attr, None)
        if value is not None:
            function_kwargs[attr] = value

    # Add optional parameters
    instructions = getattr(tool_node, 'instructions', None)
    if instructions is not None:
        function_kwargs['instructions'] = instructions

    add_instructions = getattr(tool_node, 'add_instructions', None)
    if add_instructions is not None:
        function_kwargs['add_instructions'] = add_instructions

    function = Function(**function_kwargs)
    
    return function


def find_connected_path_tools(node: Node) -> list:
    print(f"\n=== FINDING PATH TOOLS for node {node.id} ===")

    all_out_connections = node.get_out_connections()
    print(f"Total outgoing connections: {len(all_out_connections)}")

    for conn in all_out_connections:
        print(f"  Connection: source_handle='{conn.source_handle}', target_node={conn.target_node_id}")

    tool_connections = [
        c for c in all_out_connections
        if c.source_handle == "path_tools"
    ]
    print(f"Path tool connections found: {len(tool_connections)}")

    tools: list[Function] = []

    for connection in tool_connections:
        tool_node = node.state.get_node_by_id(connection.target_node_id)
        tool_node_type = type(tool_node).__name__

        print(f"\n  Processing tool node: {tool_node.id}")
        print(f"    Type: {tool_node_type}")
        print(f"    Handle: {getattr(tool_node, 'handle', 'NO HANDLE')}")
        print(f"    Name: {getattr(tool_node, 'name', 'NO NAME')}")
        print(f"    Starts with 'agnopathtool': {tool_node_type.lower().startswith('agnopathtool')}")

        if not tool_node_type.lower().startswith("agnopathtool"):
            print(f"    ❌ SKIPPED: Type doesn't start with 'agnopathtool'")
            continue

        print(f"    ✅ Creating tool...")
        tool = create_tool_and_invoke(node, tool_node)
        tools.append(tool)
        print(f"    ✅ Tool created: {tool.name}")

    print(f"\n=== TOTAL PATH TOOLS CREATED: {len(tools)} ===\n")
    return tools