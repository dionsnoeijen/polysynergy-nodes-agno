import asyncio
import re
from typing import Callable, Dict
from polysynergy_node_runner.execution_context.send_flow_event import send_flow_event


def is_valid_uuid(value: str) -> bool:
    """Check if a string is a valid UUID."""
    uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.IGNORECASE)
    return bool(uuid_pattern.match(value))


def create_tool_hook(context, function_name_to_node_id: Dict[str, str]):
    """
    Creates a tool hook function for Agno agents that handles tool execution
    with proper event emission and result storage.

    Args:
        context: The node execution context
        function_name_to_node_id: Mapping of function names to their node IDs

    Returns:
        Async function that can be used as a tool hook in Agno agents
    """
    async def tool_hook(function_name: str, function_call: Callable, arguments: dict):
        # Check if this is a mapped node tool or an internal Agno tool
        is_node_tool = function_name in function_name_to_node_id
        node_id = function_name_to_node_id.get(function_name, function_name)

        # Additional validation: Check if the node_id looks like a valid node
        # (has UUID format) and exists in the execution flow
        is_valid_node = False
        node_order = None

        if is_node_tool:
            # Verify the node exists in the execution flow
            for node in context.execution_flow.get("nodes_order", []):
                if node["id"] == node_id:
                    node_handle = node.get("handle", "")
                    node_order = node.get("order")
                    # Only consider it valid if it has a proper handle
                    if node_handle:
                        is_valid_node = True
                    else:
                        print(f"Warning: Node {node_id} has no handle, skipping storage")
                    break

            # Double-check: node_id should be a UUID for real nodes
            if is_valid_node and not is_valid_uuid(node_id):
                print(f"Warning: Node ID {node_id} doesn't look like a UUID")
                is_valid_node = False

        async def wrapper():
            # Only send events for actual node tools
            if is_valid_node:
                send_flow_event(
                    flow_id=context.node_setup_version_id,
                    run_id=context.run_id,
                    node_id=node_id,
                    event_type='start_tool',
                )

            try:
                # Execute the tool function (always execute, whether it's a node or internal tool)
                result = function_call(**arguments)
                if asyncio.iscoroutine(result):
                    result = await result

                # Only store results for valid node tools
                if is_valid_node:
                    # Store the result in the node's output
                    flow_id = context.node_setup_version_id
                    run_id = context.run_id
                    context.storage.set_node_variable_value(
                        flow_id=flow_id,
                        run_id=run_id,
                        node_id=node_id,
                        true_text=result,
                        order=node_order,
                        stage=context.stage,
                        sub_stage=context.sub_stage,
                        handle="output"
                    )
                else:
                    # For internal tools, just log that they were executed
                    print(f"Internal tool '{function_name}' executed successfully")

                return result

            except Exception as e:
                # Log tool error but don't crash the hook
                print(f"Tool {function_name} failed: {e}")
                raise  # Re-raise so Agno can handle it properly

            finally:
                # Only send end event for actual node tools
                if is_valid_node:
                    send_flow_event(
                        flow_id=context.node_setup_version_id,
                        run_id=context.run_id,
                        node_id=node_id,
                        event_type='end_tool',
                    )

        return await wrapper()

    return tool_hook