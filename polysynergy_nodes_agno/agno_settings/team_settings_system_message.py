from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Team Settings System Message",
    category="agno_settings",
    has_enabled_switch=False,
    icon="agno.svg",
)
class TeamSettingsSystemMessage(ServiceNode):

    settings: list = [
        'additional_context',
        'markdown',
        'add_datetime_to_instructions',
        'add_location_to_instructions',
        'add_member_names_to_instructions',
        'system_message',
        'system_message_role',
    ]

    additional_context: str | None = NodeVariableSettings(
        dock=True,
        info="Additional context to be added to the system message.",
    )

    markdown: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="If True, the additional context is formatted as Markdown.",
    )

    add_datetime_to_instructions: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="If True, the current date and time is added to the instructions.",
    )

    add_location_to_instructions: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="If True, the current location is added to the instructions.",
    )

    add_member_names_to_instructions: bool = NodeVariableSettings(
        dock=True,
        default=True,
        info="If True, the names of team members are added to the instructions.",
    )

    system_message: str | None = NodeVariableSettings(
        dock=True,
        info="The system message to be used by the team agent.",
    )

    system_message_role: str = NodeVariableSettings(
        dock=True,
        default="system",
        info="The role of the system message, typically 'system'.",
    )

    instance: "TeamSettingsSystemMessage" = NodeVariableSettings(
        label="Settings",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.team_settings_system_message.TeamSettingsSystemMessage"
    )

    async def provide_instance(self) -> "TeamSettingsSystemMessage":
        return self