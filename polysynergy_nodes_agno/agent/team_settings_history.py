from agno.memory import TeamMemory, Memory
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Team History Settings",
    category="agno",
    has_enabled_switch=False,
    icon="agno.svg"
)
class TeamSettingsHistory(ServiceNode):

    settings: list = [
        'memory',
        'enable_agentic_memory',
        'enable_user_memories',
        'add_memory_references',
        'enable_session_summaries',
        'add_session_summary_references',
    ]

    memory: TeamMemory | Memory = NodeVariableSettings(
        dock=True,
        has_in=True,
        info="The memory backend used by this agent for team history. For example: DynamoDbMemory, SqliteMemory, etc.",
    )

    enable_agentic_memory: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="Enable the agent to manage memories of the user.",
    )

    enable_user_memories: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="If True, the agent stores or updates memories for the user after each run.",
    )

    add_memory_references: bool | None = NodeVariableSettings(
        dock=True,
        info="If True, memory references are added to the response output.",
    )

    enable_session_summaries: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="If True, the agent generates a summary of the session after completion.",
    )

    add_session_summary_references: bool | None = NodeVariableSettings(
        dock=True,
        info="If True, references to session summaries are added to the response.",
    )

    instance: "TeamSettingsHistory" = NodeVariableSettings(
        label="Settings",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.team_settings_history.TeamSettingsHistory"
    )

    def provide_instance(self) -> "TeamSettingsHistory":
        return self
