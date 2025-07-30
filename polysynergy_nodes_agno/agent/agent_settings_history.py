from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode


@node(
    name="Agent History Settings",
    category="agno",
    has_enabled_switch=False,
    icon="agno.svg",
)
class AgentSettingsHistory(ServiceNode):

    # Settings that can be used by the agent on runtime.
    settings: list = [
        'add_history_to_messages',
        'num_history_responses',
        'num_history_runs',
    ]

    add_history_to_messages: bool = NodeVariableSettings(
        dock=True,
        info="If True, adds messages from chat history to the list sent to the model for better context.",
    )

    num_history_responses: int | None = NodeVariableSettings(
        dock=True,
        info="(Deprecated) Number of previous responses to include in the messages. Use 'num_history_runs' instead.",
    )

    num_history_runs: int = NodeVariableSettings(
        dock=True,
        info="Number of previous runs to include in the messages for contextual continuity.",
    )

    instance: "AgentSettingsHistory" = NodeVariableSettings(
        label="Settings",
        group="messaging",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.agent_settings_history.AgentSettingsHistory"
    )

    def provide_instance(self) -> "AgentSettingsHistory":
        return self