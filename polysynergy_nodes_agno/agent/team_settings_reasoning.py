from agno.agent import Agent
from agno.models.base import Model
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Team Settings Reasoning",
    category="agno",
    has_enabled_switch=False,
    icon='agno.svg',
)
class TeamSettingsReasoning(ServiceNode):

    settings: list = [
        'reasoning',
        'reasoning_model',
        'reasoning_agent',
        'reasoning_min_steps',
        'reasoning_max_steps',
    ]

    reasoning: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="If True, the agent uses reasoning to process team settings.",
    )

    reasoning_model: Model | None = NodeVariableSettings(
        dock=True,
        has_in=True,
        info="The model used for reasoning in team settings.",
        type="agno.models.base.Model"
    )

    reasoning_agent: Agent | None = NodeVariableSettings(
        has_out=True,
        info="The agent used for reasoning in team settings.",
        type="agno.agent.Agent"
    )

    reasoning_min_steps: int = NodeVariableSettings(
        dock=True,
        default=1,
        info="The minimum number of reasoning steps to perform.",
    )

    reasoning_max_steps: int = NodeVariableSettings(
        dock=True,
        default=10,
        info="The maximum number of reasoning steps to perform.",
    )

    instance: "TeamSettingsReasoning" = NodeVariableSettings(
        label="Settings",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.team_settings_reasoning.TeamSettingsReasoning"
    )

    def provide_instance(self) -> "TeamSettingsReasoning":
        return self