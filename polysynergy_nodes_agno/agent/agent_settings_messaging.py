from collections.abc import Callable

from agno.models.message import Message
from polysynergy_node_runner.setup_context.dock_property import dock_text_area
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode


@node(
    name="Agent Messaging Settings",
    category="agno",
    has_enabled_switch=False,
    icon="agno.svg",
)
class AgentSettingsMessaging(ServiceNode):

    # Settings that can be used by the agent on runtime.
    settings: list = [
        'system_message',
        'system_message_role',
        'create_default_system_message',
        'additional_context',
        'markdown',
        'add_name_to_instructions',
        'add_datetime_to_instructions',
        'add_location_to_instructions',
        'timezone_identifier',
        'add_state_in_messages',
        'add_messages',
        'success_criteria',
        'user_message',
        'user_message_role',
    ]

    system_message: str | Callable | Message | None = NodeVariableSettings(
        dock=dock_text_area(),
        info="The system message that guides model behavior. Can be a string, callable, or Message.",
    )

    system_message_role: str = NodeVariableSettings(
        dock=True,
        default="system",
        info="The role assigned to the system message (typically 'system')."
    )

    create_default_system_message: bool = NodeVariableSettings(
        dock=True,
        info="If true, generates a default system message based on agent settings.",
    )

    additional_context: str | None = NodeVariableSettings(
        dock=dock_text_area(rich=True),
        info="Extra context appended to the end of the system message."
    )

    markdown: bool = NodeVariableSettings(
        dock=True,
        info="If true, instructs the agent to format output using markdown.",
    )

    add_name_to_instructions: bool = NodeVariableSettings(
        dock=True,
        info="If true, includes the agent name in the prompt instructions.",
    )

    add_datetime_to_instructions: bool = NodeVariableSettings(
        dock=True,
        info="If true, includes the current date and time in the prompt.",
    )

    add_location_to_instructions: bool = NodeVariableSettings(
        dock=True,
        info="If true, includes location information in the prompt.",
    )

    timezone_identifier: str | None = NodeVariableSettings(
        dock=True,
        info="Custom timezone for datetime, in TZ Database format (e.g., 'Etc/UTC').",
    )

    add_state_in_messages: bool = NodeVariableSettings(
        dock=True,
        info="If true, includes session state variables in user/system messages.",
    )

    add_messages: list[dict | Message] | None = NodeVariableSettings(
        dock=True,
        info="Extra messages (e.g. few-shot examples) added after the system message and before the user message. Not retained in memory.",
    )

    success_criteria: str | None = NodeVariableSettings(
        dock=True,
        info="Criteria for what a successful response should include. Used to evaluate the model output.",
    )

    user_message: list | dict | str | Callable | Message | None = NodeVariableSettings(
        dock=True,
        info="Custom user message, overrides the runtime input sent to the agent.",
    )

    user_message_role: str = NodeVariableSettings(
        info="Role for the user message (e.g. 'user').",
        default="user",
    )

    instance: "AgentSettingsMessaging" = NodeVariableSettings(
        label="Settings",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.agent_settings_messaging.AgentSettingsMessaging"
    )

    def provide_instance(self) -> "AgentSettingsMessaging":
        return self