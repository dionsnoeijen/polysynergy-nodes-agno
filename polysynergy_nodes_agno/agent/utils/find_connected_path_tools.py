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
    handle = tool_node.name or tool_node.handle or "unnamed_tool"
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
        print(f'INVOKING AGNO TOOL: {handle}', kwargs)
        
        try:
            start_node = node.state.get_node_by_id(tool_node.id)
            
            # Set arguments from function call
            for arg_name, value in kwargs.items():
                if hasattr(start_node, 'parameters') and arg_name in start_node.parameters:
                    # Set the parameter value on the start node
                    setattr(start_node, arg_name, value)
                elif hasattr(start_node, arg_name):
                    setattr(start_node, arg_name, value)
            
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
            print(f"[Error invoking agno tool {handle}]: {str(e)}")
            return f"[Error executing tool {handle}]: {str(e)}"

    # Create the Agno Function
    function = Function(
        name=handle,
        description=description,
        parameters=schema,
        entrypoint=flow_entrypoint,
        strict=getattr(tool_node, 'strict', None),
        instructions=getattr(tool_node, 'instructions', None),
        add_instructions=getattr(tool_node, 'add_instructions', True),
        show_result=getattr(tool_node, 'show_result', None),
        stop_after_tool_call=getattr(tool_node, 'stop_after_tool_call', None),
        requires_confirmation=getattr(tool_node, 'requires_confirmation', None),
        requires_user_input=getattr(tool_node, 'requires_user_input', None),
        external_execution=getattr(tool_node, 'external_execution', None),
    )
    
    return function


def find_connected_path_tools(node: Node) -> list:
    tool_connections = [
        c for c in node.get_out_connections()
        if c.source_handle == "path_tools"
    ]
    tools: list[Function] = []

    for connection in tool_connections:
        tool_node = node.state.get_node_by_id(connection.target_node_id)

        if not type(tool_node).__name__.lower().startswith("agnoflowtool"):
            continue

        tool = create_tool_and_invoke(node, tool_node)
        tools.append(tool)

    return tools