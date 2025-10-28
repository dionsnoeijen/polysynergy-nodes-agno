import json

from polysynergy_node_runner.setup_context.dock_property import dock_json
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
        'session_state',
        'search_previous_sessions_history',
        'num_history_sessions',
        'cache_session',
    ]

    session_state: str | dict | list | None = NodeVariableSettings(
        dock=dock_json(),
        info="Internal state object for this session an, persisted between runs.",
        has_in=True
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

    async def provide_instance(self) -> "AgentSettingsSession":
        # Parse JSON string to dict if needed (for by-reference mutation)
        if isinstance(self.session_state, str):
            try:
                self.session_state = json.loads(self.session_state)
                print(f"[AgentSettingsSession] Parsed session_state from JSON string to dict: {self.session_state}")
            except json.JSONDecodeError as e:
                print(f"[AgentSettingsSession] WARNING: session_state is a string but not valid JSON: {e}")
                print(f"[AgentSettingsSession] WARNING: Agno expects a dict, setting to empty dict")
                self.session_state = {}

        return self
