from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode


@node(
    name="Agent Team Settings",
    category="agno_settings",
    has_enabled_switch=False,
    icon="agno.svg",
)
class AgentSettingsTeam(ServiceNode):

    # Settings that can be used by the agent on runtime.
    settings: list = [
        'team_data',
        'role',
        'respond_directly',
        'add_transfer_instructions',
        'team_response_separator',
        'team_session_id',
        'team_id',
        'team_session_state',
    ]

    team_data: dict | None = NodeVariableSettings(
        dock=True,
        info="Additional data related to the agent team."
    )

    role: str | None = NodeVariableSettings(
        dock=True,
        info="If this agent is part of a team, this is its role."
    )

    respond_directly: bool = NodeVariableSettings(
        dock=True,
        info="If True, this agent responds directly to the user instead of routing through the leader agent."
    )

    add_transfer_instructions: bool = NodeVariableSettings(
        dock=True,
        info="Add instructions for transferring tasks to other team members."
    )

    team_response_separator: str = NodeVariableSettings(
        dock=True,
        info="Separator string between responses from team members."
    )

    team_session_id: str | None = NodeVariableSettings(
        dock=True,
        info="Optional team session ID, set by the leader agent."
    )

    team_id: str | None = NodeVariableSettings(
        dock=True,
        info="Optional team ID. Indicates this agent is part of a team."
    )

    team_session_state: dict | None = NodeVariableSettings(
        dock=True,
        info="Team session state passed down by the leader agent."
    )

    instance: "AgentSettingsTeam" = NodeVariableSettings(
        label="Settings",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.agent_settings_team.AgentSettingsTeam"
    )

    def provide_instance(self) -> "AgentSettingsTeam":
        return self
