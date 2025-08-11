from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Team Settings Streaming",
    category="agno_settings",
    has_enabled_switch=False,
    icon='agno.svg',
)
class TeamSettingsStreaming(ServiceNode):

    settings: list = [
        'stream',
        'stream_intermediate_steps',
        'stream_member_events',
        'store_events',
        'events_to_skip',
    ]

    stream: bool | None = NodeVariableSettings(
        dock=True,
        info="If True, the agent streams responses for team interactions.",
    )

    stream_intermediate_steps: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="If True, the agent streams intermediate steps during team interactions.",
    )

    stream_member_events: bool = NodeVariableSettings(
        dock=True,
        default=True,
        info="If True, the agent streams events related to team members during interactions.",
    )

    store_events: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="If True, the agent stores events related to team interactions.",
    )

    events_to_skip: list[str] | None = NodeVariableSettings(
        dock=True,
        info="List of event types to skip during streaming.",
    )

    instance: "TeamSettingsStreaming" = NodeVariableSettings(
        label="Settings",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.team_settings_streaming.TeamSettingsStreaming"
    )

    def provide_instance(self) -> "TeamSettingsStreaming":
        return self