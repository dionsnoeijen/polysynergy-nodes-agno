from agno.memory import AgentMemory
from agno.memory.v2 import Memory
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode


@node(
    name="Agent Memory Settings",
    category="agno_settings",
    has_enabled_switch=False,
    icon="agno.svg",
)
class AgentSettingsMemory(ServiceNode):

    # Settings that can be used by the agent on runtime.
    settings: list = [
        'memory',
        'enable_agentic_memory',
        'enable_user_memories',
        'add_memory_references',
        'enable_session_summaries',
        'add_session_summary_references',
    ]

    memory: AgentMemory | Memory | None = NodeVariableSettings(
        dock=True,
        has_in=True,
        info="The memory backend used by this agent. For example: DynamoDbMemory, SqliteMemory, etc.",
    )

    enable_agentic_memory: bool = NodeVariableSettings(
        dock=True,
        info="If True, the agent automatically manages memories for the current session.",
    )

    enable_user_memories: bool = NodeVariableSettings(
        dock=True,
        info="If True, the agent stores or updates memories for the user after each run.",
    )

    add_memory_references: bool | None = NodeVariableSettings(
        dock=True,
        info="If True, memory references are added to the response output.",
    )

    enable_session_summaries: bool = NodeVariableSettings(
        dock=True,
        info="If True, the agent generates a summary of the session after completion.",
    )

    add_session_summary_references: bool | None = NodeVariableSettings(
        dock=True,
        info="If True, references to session summaries are added to the response.",
    )

    instance: "AgentSettingsMemory" = NodeVariableSettings(
        label="Settings",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.agent_settings_memory.AgentSettingsMemory"
    )

    def provide_instance(self) -> "AgentSettingsMemory":
        return self