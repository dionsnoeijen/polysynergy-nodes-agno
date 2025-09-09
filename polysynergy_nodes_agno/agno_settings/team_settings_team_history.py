from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Team Settings Team History",
    category="agno_settings",
    has_enabled_switch=False,
    icon='agno.svg',
)
class TeamSettingsTeamHistory(ServiceNode):

    settings: list = [
        'enable_team_history',
        'add_history_to_messages',
        'num_of_interactions_from_history',
        'num_history_runs',
    ]

    enable_team_history: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="If True, the agent reads the team history to provide context for interactions.",
    )

    add_history_to_messages: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="If True, the team history is added to the messages sent to the agent.",
    )

    num_of_interactions_from_history: int | None = NodeVariableSettings(
        dock=True,
        info="The number of interactions from the team history to include in the messages.",
    )

    num_history_runs: int = NodeVariableSettings(
        dock=True,
        default=20,
        info="The number of runs to include in the team history.",
    )

    instance: "TeamSettingsTeamHistory" = NodeVariableSettings(
        label="Settings",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.team_settings_team_history.TeamSettingsTeamHistory"
    )

    async def provide_instance(self) -> "TeamSettingsTeamHistory":
        return self