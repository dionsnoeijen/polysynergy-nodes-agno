from polysynergy_node_runner.execution_context.flow_state import FlowState
from polysynergy_node_runner.setup_context.dock_property import dock_dict, dock_text_area
from polysynergy_node_runner.setup_context.node import Node
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.path_settings import PathSettings


@node(
    name='Agno Path Tool',
    category='agno_path_tool',
    icon='hammer.svg',
    has_enabled_switch=False,
    flow_state=FlowState.PENDING,
)
class AgnoPathTool(Node):

    agent: str = NodeVariableSettings(
        label="Agent",
        has_in=True
    )

    name: str = NodeVariableSettings(
        label="Name",
        dock=True,
        info="Display name for the tool (can contain spaces)"
    )

    function_name: str = NodeVariableSettings(
        label="Function Name",
        dock=True,
        info="Valid function identifier for LLM (letters, numbers, underscores only). Example: process_receipt"
    )

    description: str = NodeVariableSettings(
        label="Description",
        dock=True,
        info="Description of what this tool does and when to use it"
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

    user_input_fields: list | None = NodeVariableSettings(
        label="User Input Fields",
        dock=True,
        info='List of fields that will be provided to the function as user input'
    )

    external_execution: bool | None = NodeVariableSettings(
        label="External Execution",
        dock=True,
        info='If True, the function will be executed outside of the agent\'s context'
    )

    parameters: dict = NodeVariableSettings(
        label="Parameters",
        has_out=True,
        dock=dock_dict(
            key_label="Name",
            value_label="Instructions",
            in_switch=False,
            out_switch_default=True
        )
    )

    true_path: bool = PathSettings(default=True, label="On Call")

    def execute(self):
        pass