from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Team Session Settings",
    category="agno",
    has_enabled_switch=False,
    icon="agno.svg",
)
class TeamSettingsSession(ServiceNode):

    # Settings that can be used by the agent on runtime.
    settings: list = [
        'session_id',
        'session_name',
        'session_state',
        'search_previous_sessions_history',
        'num_history_sessions',
        'cache_session',
        'team_session_state',
        'workflow_session_state',
        'add_state_in_messages',
    ]

    session_id: str | None = NodeVariableSettings(
        dock=True,
        info="Unique session ID to group messages. Leave empty to auto-generate."
    )

    session_name: str | None = NodeVariableSettings(
        dock=True,
        info="Optional name for the session, useful for debugging or display."
    )

    session_state: dict | None = NodeVariableSettings(
        dock=True,
        info="Internal state object for this session, persisted between runs.",
    )

    search_previous_sessions_history: bool = NodeVariableSettings(
        dock=True,
        info="Search previous sessions to retrieve relevant memory history.",
    )

    num_history_sessions: int | None = NodeVariableSettings(
        dock=True,
        info="Number of past sessions to search if history search is enabled.",
    )

    cache_session: bool = NodeVariableSettings(
        dock=True,
        default=True,
        info="If True, the session is cached in memory for faster access.",
    )

    team_session_state: dict | None = NodeVariableSettings(
        dock=True,
        info="State object for the team session, persisted between runs.",
    )

    workflow_session_state: dict | None = NodeVariableSettings(
        dock=True,
        info="Workflow session state passed down by the workflow controller.",
    )

    add_state_in_messages: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="If True, the session state is added to messages sent in this session.",
    )

    instance: "TeamSettingsSession" = NodeVariableSettings(
        label="Settings",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.team_settings_session.TeamSettingsSession"
    )

    def provide_instance(self) -> "TeamSettingsSession":
        return self