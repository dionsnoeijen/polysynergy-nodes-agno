from agno.storage.base import Storage
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Team Settings Storage",
    category="agno_settings",
    has_enabled_switch=False,
    icon='agno.svg',
)
class TeamSettingsStorage(ServiceNode):

    settings: list = [
        'storage',
        'extra_data',
    ]

    storage: Storage | None = NodeVariableSettings(
        dock=True,
        has_in=True,
        info="The storage backend used by this agent for team settings. For example: DynamoDbStorage, SqliteStorage, etc.",
    )

    extra_data: dict | None = NodeVariableSettings(
        dock=True,
        info="Additional data to store in the storage backend.",
    )

    instance: "TeamSettingsStorage" = NodeVariableSettings(
        label="Settings",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.team_settings_storage.TeamSettingsStorage"
    )

    async def provide_instance(self) -> "TeamSettingsStorage":
        return self
