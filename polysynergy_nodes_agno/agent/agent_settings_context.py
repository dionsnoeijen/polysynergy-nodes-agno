from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode


@node(
    name="Agent Context Settings",
    category="agno",
    has_enabled_switch=False,
    icon="agno.svg",
)
class AgentSettingsContext(ServiceNode):

    # Settings that can be used by the agent on runtime.
    settings: list = [
        'context',
        'add_context',
        'resolve_context',
    ]

    context: dict | None = NodeVariableSettings(
        dock=True,
        info="Static or dynamic context available for tools and prompts. Can include strings or callables."
    )

    add_context: bool = NodeVariableSettings(
        dock=True,
        info="If True, includes the context in the prompt sent to the model.",
    )

    resolve_context: bool = NodeVariableSettings(
        dock=True,
        info="If True, resolves any functions in the context before use.",
    )

    instance: "AgentSettingsContext" = NodeVariableSettings(
        label="Settings",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.agent_settings_context.AgentSettingsContext"
    )

    def provide_instance(self) -> "AgentSettingsContext":
        return self