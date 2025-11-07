import asyncio
import re
from typing import Callable, Dict
from polysynergy_node_runner.execution_context.send_flow_event import send_flow_event


def is_valid_uuid(value: str) -> bool:
    """Check if a string is a valid UUID."""
    uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.IGNORECASE)
    return bool(uuid_pattern.match(value))


def create_tool_hook(context, function_name_to_node_id: Dict[str, str], mcp_toolkits: list = None):
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
        # DEBUG: Print wat we hebben
        print(f"\n🔧 TOOL HOOK CALLED: {function_name}")
        print(f"   Context id: {id(context)}")
        print(f"   Execution flow id: {id(context.execution_flow)}")
        print(f"   Run ID: {context.run_id}")
        print(f"   function_name_to_node_id keys: {list(function_name_to_node_id.keys())}")
        print(f"   Is in mapping: {function_name in function_name_to_node_id}")

        # Check if this is a mapped node tool or an internal Agno tool
        is_node_tool = function_name in function_name_to_node_id
        node_id = function_name_to_node_id.get(function_name, function_name)

        # If not in static mapping, assume it's from an MCP toolkit (dynamic tools)
        # MCP tools are loaded dynamically by Agno, so any unmapped tool likely comes from MCP
        if not is_node_tool and mcp_toolkits:
            print(f"   Tool not in static mapping, checking {len(mcp_toolkits)} MCP toolkit(s)...")
            # For now, assume first MCP toolkit (we can make this smarter later)
            if len(mcp_toolkits) > 0:
                mcp_info = mcp_toolkits[0]  # Use first MCP toolkit
                node_id = mcp_info["node_id"]
                is_node_tool = True
                print(f"   ⚡ Assuming MCP tool '{function_name}' belongs to node {node_id}")

        print(f"   is_node_tool: {is_node_tool}")
        print(f"   node_id: {node_id}")

        # Check if this is a registered node by looking in state
        # Don't check execution_flow['nodes_order'] because tools may not be executed yet
        is_valid_node = False
        node_order = None

        if is_node_tool:
            # For UUID node_ids, check if registered in state
            if is_valid_uuid(node_id):
                print(f"   Checking if node {node_id} is registered in state")
                try:
                    # Check if node is registered in state (works even if not executed yet)
                    node_instance = context.state.get_node_by_id(node_id)
                    if node_instance:
                        print(f"   ✓ Found node in state: handle={node_instance.handle}")
                        is_valid_node = True

                        # Try to find order if node already executed
                        for node in context.execution_flow.get("nodes_order", []):
                            if node["id"] == node_id:
                                node_order = node.get("order")
                                print(f"   ✓ Node already executed with order={node_order}")
                                break
                    else:
                        print(f"   ✗ Node {node_id} not registered in state")
                except Exception as e:
                    print(f"   ✗ Error checking state: {e}")
            else:
                # Non-UUID node_id (e.g. path tools with function names)
                # These are internal/dynamic tools, not node tools
                print(f"   ✗ node_id '{node_id}' is not a UUID - treating as internal tool")
                is_valid_node = False

        print(f"   FINAL is_valid_node: {is_valid_node}")
        print(f"   Will send events: {is_valid_node}")

        async def wrapper():
            # Check if there's an active listener before sending events
            has_listener = context.active_listeners.has_listener(
                context.node_setup_version_id,
                required_stage=context.stage
            )

            # Only send events for actual node tools AND if there's a listener
            if is_valid_node and has_listener:
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
                # Only send end event for actual node tools AND if there's a listener
                if is_valid_node and has_listener:
                    send_flow_event(
                        flow_id=context.node_setup_version_id,
                        run_id=context.run_id,
                        node_id=node_id,
                        event_type='end_tool',
                    )

        return await wrapper()

    return tool_hook