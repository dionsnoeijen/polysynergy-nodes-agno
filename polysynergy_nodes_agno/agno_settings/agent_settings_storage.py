from agno.storage.base import Storage
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode


@node(
    name="Agent Storage Settings",
    category="agno_settings",
    has_enabled_switch=False,
    icon="agno.svg",
)
class AgentSettingsStorage(ServiceNode):

    # Settings that can be used by the agent on runtime.
    settings: list = [
        'storage',
        'extra_data'
    ]

    storage: Storage | None = NodeVariableSettings(
        dock=True,
        has_in=True,
        info="Storage backend for agent state, memory, and events (e.g. DynamoStorage or SqliteStorage).",
    )

    extra_data: dict | None = NodeVariableSettings(
        dock=True,
        info="Additional metadata or configuration stored with this agent.",
    )

    instance: "AgentSettingsStorage" = NodeVariableSettings(
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.agent_settings_storage.AgentSettingsStorage"
    )

    def provide_instance(self) -> "AgentSettingsStorage":
        return self