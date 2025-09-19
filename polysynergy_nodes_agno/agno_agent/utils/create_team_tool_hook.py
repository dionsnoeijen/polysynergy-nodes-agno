import asyncio
from typing import Callable, Dict
from polysynergy_node_runner.execution_context.send_flow_event import send_flow_event


def create_team_tool_hook(context, function_name_to_node_id: Dict[str, str]):
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
        node_id = function_name_to_node_id.get(function_name, function_name)

        async def wrapper():
            send_flow_event(
                flow_id=context.node_setup_version_id,
                run_id=context.run_id,
                node_id=node_id,
                event_type='start_tool_or_member',
            )
            
            try:
                # Execute the tool function
                result = function_call(**arguments)
                if asyncio.iscoroutine(result):
                    result = await result
                return result
                
            except Exception as e:
                # Log tool error but don't crash the hook
                print(f"Tool {function_name} failed: {e}")
                raise  # Re-raise so Agno can handle it properly
                
            finally:
                send_flow_event(
                    flow_id=context.node_setup_version_id,
                    run_id=context.run_id,
                    node_id=node_id,
                    event_type='end_tool_or_member',
                )

        return await wrapper()

    return tool_hook