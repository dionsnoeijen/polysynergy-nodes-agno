from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode


@node(
    name="Agent Session Settings",
    category="agno_settings",
    has_enabled_switch=False,
    icon="agno.svg",
)
class AgentSettingsSession(ServiceNode):

    # Settings that can be used by the agent on runtime.
    settings: list = [
        'session_id',
        'session_name',
        'session_state',
        'search_previous_sessions_history',
        'num_history_sessions',
        'cache_session',
    ]

    session_id: str | None = NodeVariableSettings(
        dock=True,
        has_in=True,
        info="Unique session ID to group messages. Leave empty to auto-generate."
    )

    session_name: str | None = NodeVariableSettings(
        dock=True,
        has_in=True,
        info="Optional name for the session, useful for debugging or display."
    )

    session_state: dict | None = NodeVariableSettings(
        dock=True,
        info="Internal state object for this session, persisted between runs.",
        node=False
    )

    search_previous_sessions_history: bool = NodeVariableSettings(
        dock=True,
        info="Search previous sessions to retrieve relevant memory history.",
        node=False
    )

    num_history_sessions: int | None = NodeVariableSettings(
        dock=True,
        info="Number of past sessions to search if history search is enabled.",
        node=False
    )

    cache_session: bool = NodeVariableSettings(
        dock=True,
        info="If True, the session is cached in memory for faster access.",
        node=False
    )

    instance: "AgentSettingsSession" = NodeVariableSettings(
        label="Settings",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.agent_settings_session.AgentSettingsSession"
    )

    def provide_instance(self) -> "AgentSettingsSession":
        return self
