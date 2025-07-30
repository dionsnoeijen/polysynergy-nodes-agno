from agno.agent import Agent
from agno.models.base import Model
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode


@node(
    name="Agent Reasoning Settings",
    category="agno",
    has_enabled_switch=False,
    icon="agno.svg",
)
class AgentSettingsReasoning(ServiceNode):

    # Settings that can be used by the agent on runtime.
    settings: list = [
        'reasoning',
        'reasoning_model',
        'reasoning_agent',
        'reasoning_min_steps',
        'reasoning_max_steps',
    ]

    reasoning: bool = NodeVariableSettings(
        dock=True,
        info="Enable reasoning mode where the agent works step-by-step through a problem.",
    )

    reasoning_model: Model | None = NodeVariableSettings(
        dock=True,
        has_in=True,
        info="Optional model used specifically for reasoning steps.",
    )

    reasoning_agent: Agent | None = NodeVariableSettings(
        dock=True,
        has_in=True,
        info="Optional agent used to execute reasoning steps."
    )

    reasoning_min_steps: int = NodeVariableSettings(
        dock=True,
        default=1,
        info="Minimum number of reasoning steps to perform.",
    )

    reasoning_max_steps: int = NodeVariableSettings(
        dock=True,
        default=10,
        info="Maximum number of reasoning steps to perform before stopping.",
    )

    instance: "AgentSettingsReasoning" = NodeVariableSettings(
        label="Settings",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.agent_settings_reasoning.AgentSettingsReasoning"
    )

    def provide_instance(self) -> "AgentSettingsReasoning":
        return self