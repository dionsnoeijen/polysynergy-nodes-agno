import asyncio
import re
from typing import Callable, Dict
from polysynergy_node_runner.execution_context.send_flow_event import send_flow_event


def is_valid_uuid(value: str) -> bool:
    """Check if a string is a valid UUID."""
    uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.IGNORECASE)
    return bool(uuid_pattern.match(value))


def create_team_tool_hook(context, function_name_to_node_id: Dict[str, str], mcp_toolkits: list = None):
    """
    Creates a tool hook function for Agno teams that handles tool execution
    with proper event emission. Teams use different event types and don't store results.

    Args:
        context: The node execution context
        function_name_to_node_id: Mapping of function names to their node IDs

    Returns:
        Async function that can be used as a tool hook in Agno teams
    """
    async def tool_hook(function_name: str, function_call: Callable, arguments: dict):
        # Check if this is a mapped node tool or an internal Agno tool
        is_node_tool = function_name in function_name_to_node_id
        node_id = function_name_to_node_id.get(function_name, function_name)

        # If not in static mapping, assume it's from an MCP toolkit (dynamic tools)
        # MCP tools are loaded dynamically by Agno, so any unmapped tool likely comes from MCP
        if not is_node_tool and mcp_toolkits:
            # For now, assume first MCP toolkit (we can make this smarter later)
            if len(mcp_toolkits) > 0:
                mcp_info = mcp_toolkits[0]  # Use first MCP toolkit
                node_id = mcp_info["node_id"]
                is_node_tool = True

        # Only send events for valid node tools (not internal Agno tools)
        # Validate by checking if it's in the mapping and has a valid UUID
        should_send_events = is_node_tool and is_valid_uuid(node_id)

        async def wrapper():
            # Only send events for actual node tools
            if should_send_events:
                send_flow_event(
                    flow_id=context.node_setup_version_id,
                    run_id=context.run_id,
                    node_id=node_id,
                    event_type='start_tool_or_member',
                )

            try:
                # Execute the tool function (always execute, whether it's a node or internal tool)
                result = function_call(**arguments)
                if asyncio.iscoroutine(result):
                    result = await result
                return result

            except Exception as e:
                # Log tool error but don't crash the hook
                print(f"Tool {function_name} failed: {e}")
                raise  # Re-raise so Agno can handle it properly

            finally:
                # Only send end event for actual node tools
                if should_send_events:
                    send_flow_event(
                        flow_id=context.node_setup_version_id,
                        run_id=context.run_id,
                        node_id=node_id,
                        event_type='end_tool_or_member',
                    )

        return await wrapper()

    return tool_hook