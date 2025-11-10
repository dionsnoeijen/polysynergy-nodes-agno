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
    # session_state is automatically injected by Agno as first parameter
    async def flow_entrypoint(session_state=None, **kwargs):
        print(f'INVOKING AGNO TOOL: {function_name}', kwargs)

        try:
            start_node = node.state.get_node_by_id(tool_node.id)

            # Find the nodes in the tool subflow FIRST
            nodes_for_tool, end_node = find_nodes_for_tool(start_node)

            print('START_NODE', start_node)
            print('END_NODE', end_node)
            print('TOOL NODES', [getattr(n, 'handle', 'no_handle') for n in nodes_for_tool])

            if not start_node or not end_node:
                return f"Could not resolve tool subflow for {function_name}"

            # IMPORTANT: Resurrect all nodes BEFORE setting any state
            # This ensures nodes are in clean state for re-execution (like in loops)
            # CRITICAL: Resurrect the path tool node itself first!
            # find_nodes_until returns downstream nodes but NOT the start_node itself
            start_node.resurrect()
            print(f"[Path Tool] Resurrected start_node (path tool): {start_node.id}")

            for node_for_tool in nodes_for_tool:
                node_for_tool.resurrect()

            # CRITICAL: Also resurrect the end_node (AgnoToolResult)!
            # find_nodes_until uses end_node as the stopping point, so it's NOT in nodes_for_tool
            # Without this, second tool call reads stale result from first call
            end_node.resurrect()
            print(f"[Path Tool] Resurrected end_node (tool result): {end_node.id}")

            print(f"[Path Tool] Resurrected {len(nodes_for_tool)} downstream nodes for execution")

            # Use session_state parameter that Agno provides
            # Agno automatically injects the correct session_state (we loaded it from DB in agno_agent.py)
            if session_state is not None:
                start_node.session_state = session_state
                print(f"[Path Tool] Injected session_state from Agno: {session_state}")
            else:
                print(f"[Path Tool] No session_state provided by Agno")

            # Set arguments from function call into parameters dict
            # CRITICAL: Create a NEW dict instead of mutating the old one
            # After resurrect(), mutating the old dict doesn't propagate via connections
            if hasattr(start_node, 'parameters'):
                start_node.parameters = {arg_name: value for arg_name, value in kwargs.items()}
                print(f"Replaced start_node.parameters with NEW dict: {start_node.parameters}")
            else:
                # Fallback: set individual attributes
                for arg_name, value in kwargs.items():
                    setattr(start_node, arg_name, value)
                    print(f"Set {arg_name} = {value} as attribute")
            
            # Enable the start node
            start_node.flow_state = FlowState.ENABLED
            
            # Add found_by connections
            for connection in start_node.get_in_connections():
                start_node.add_found_by(connection.uuid)
            
            # Execute the flow starting from this node
            await node.flow.execute_node(start_node)

            # The session_state dict was mutated by the path tool in-place
            # Use the mutated session_state dict as the result (not end_node.result)
            print(f'[Path Tool] Session state after execution: {session_state}')

            # CRITICAL: Write back the mutated session_state to the agent
            # Agno may not detect mutations to the dict, so we explicitly assign it back
            if session_state is not None and hasattr(node, 'instance'):
                node.instance.session_state = session_state
                print(f"[Path Tool] Wrote back mutated session_state to agent: {session_state}")

            # Find ALL executed AgnoToolResult nodes (not just the first one found)
            # This handles multiple result nodes in different branches or parallel paths
            executed_results = []

            # Check all nodes in the tool subflow
            for node_in_tool in nodes_for_tool:
                if (node_in_tool.__class__.__name__.lower().startswith("agnotoolresult") and
                    node_in_tool.flow_state == FlowState.EXECUTED):
                    result = getattr(node_in_tool, 'result', None)
                    executed_results.append(result)
                    print(f'[Path Tool] Found executed result node: {node_in_tool.id} with result: {result}')

            # Also check end_node (in case it wasn't in nodes_for_tool)
            if (end_node.flow_state == FlowState.EXECUTED and
                end_node not in [n for n in nodes_for_tool if n.__class__.__name__.lower().startswith("agnotoolresult")]):
                result = getattr(end_node, 'result', None)
                executed_results.append(result)
                print(f'[Path Tool] Found executed end_node: {end_node.id} with result: {result}')

            print(f'[Path Tool] Total executed result nodes: {len(executed_results)}')

            # Smart return logic based on number of results
            if len(executed_results) == 0:
                # No executed results found, return session_state as fallback
                tool_result = session_state
                print(f'[Path Tool] No executed results found, returning session_state')
            elif len(executed_results) == 1:
                # Single result - return as-is (backwards compatible)
                tool_result = executed_results[0]
                print(f'[Path Tool] Single result found: {tool_result}')
            else:
                # Multiple results - return as list for LLM to interpret
                tool_result = executed_results
                print(f'[Path Tool] Multiple results found: {tool_result}')

            # Return the result(s)
            # Note: nodes will be resurrected at the start of the next tool invocation
            return str(tool_result)

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

    # Add user_input_fields for HITL user input pattern
    user_input_fields = getattr(tool_node, 'user_input_fields', None)
    if user_input_fields is not None:
        function_kwargs['user_input_fields'] = user_input_fields

    # Add sanitize_arguments
    sanitize_arguments = getattr(tool_node, 'sanitize_arguments', None)
    if sanitize_arguments is not None:
        function_kwargs['sanitize_arguments'] = sanitize_arguments

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