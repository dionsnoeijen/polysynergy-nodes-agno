from polysynergy_node_runner.execution_context.flow_state import FlowState
from polysynergy_node_runner.setup_context.dock_property import dock_dict, dock_text_area
from polysynergy_node_runner.setup_context.node import Node
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.path_settings import PathSettings


@node(
    name='Ango Flow Tool',
    category='flow',
    icon='hammer.svg',
    has_enabled_switch=False,
    flow_state=FlowState.PENDING,
)
class AgnoFlowTool(Node):

    agent: str = NodeVariableSettings(
        label="Agent",
        has_in=True
    )

    name: str = NodeVariableSettings(
        label="Name",
        dock=True,
    )

    description: str = NodeVariableSettings(
        label="Description",
        dock=True,
    )

    strict: bool | None = NodeVariableSettings(
        label="Strict Parameter Checking",
        dock=True,
    )

    sanitize_arguments: bool | None = NodeVariableSettings(
        label="Sanitize Arguments",
        dock=True
    )

    instructions: str = NodeVariableSettings(
        label="Instructions",
        dock=dock_text_area(),
        info='Instructions for using the tool',
    )

    add_instructions: bool = NodeVariableSettings(
        label="Add Instructions",
        dock=True,
        default=False,
        info='If True, add instructions to the system message'
    )

    show_result: bool | None = NodeVariableSettings(
        label="Show Result",
        dock=True,
        info='If True, shows the result after function call'
    )

    stop_after_tool_call: bool | None = NodeVariableSettings(
        label="Stop After Tool Call",
        dock=True,
        info='If True, the agent will stop after the function call.'
    )

    requires_confirmation: bool | None = NodeVariableSettings(
        label="Requires Confirmation",
        dock=True,
        info='If True, the function will require user confirmation before execution'
    )

    requires_user_input: bool | None = NodeVariableSettings(
        label="Requires User Input",
        dock=True,
        info='If True, the function will require user input before execution'
    )

    # @todo: Figure out what this means
    user_input_fields: list[str] | None = NodeVariableSettings(
        label="User Input Fields",
        dock=True,
        info='List of fields that will be provided to the function as user input'
    )

    external_execution: bool | None = NodeVariableSettings(
        label="External Execution",
        dock=True,
        info='If True, the function will be executed outside of the agent\'s context'
    )

    # @todo: Check how to integrate this
    # cache_results: bool = NodeVariableSettings(
    #     label="Cache Results",
    #     dock=True,
    #     default=False,
    #     info='If True, enable caching of function results'
    # )

    parameters: dict = NodeVariableSettings(
        label="Parameters",
        dock=dock_dict(
            key_label="Name",
            value_label="Instructions",
            in_switch=False,
            out_switch_default=True
        )
    )

    '''
    name: Optional[str] - Override for the function name
    description: Optional[str] - Override for the function description
    strict: Optional[bool] - Flag for strict parameter checking
    sanitize_arguments: Optional[bool] - If True, arguments are sanitized before passing to function (Deprecated)
    instructions: Optional[str] -  Instructions for using the tool
    add_instructions: bool - If True, add instructions to the system message
    show_result: Optional[bool] - If True, shows the result after function call
    stop_after_tool_call: Optional[bool] - If True, the agent will stop after the function call.
    requires_confirmation: Optional[bool] - If True, the function will require user confirmation before execution
    requires_user_input: Optional[bool] - If True, the function will require user input before execution
    user_input_fields: Optional[List[str]] - List of fields that will be provided to the function as user input
    external_execution: Optional[bool] - If True, the function will be executed outside of the agent's context
    pre_hook: Optional[Callable] - Hook that runs before the function is executed.
    post_hook: Optional[Callable] - Hook that runs after the function is executed.
    tool_hooks: Optional[List[Callable]] - List of hooks that run before and after the function is executed.
    cache_results: bool - If True, enable caching of function results
    cache_dir: Optional[str] - Directory to store cache files
    cache_ttl: int - Time-to-live for cached results in seconds
    '''

    true_path: bool = PathSettings(default=True, label="On Call")

    def execute(self):
        pass