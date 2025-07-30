from polysynergy_node_runner.setup_context.dock_property import dock_select_values
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Team Settings Knowledge",
    category="agno",
    has_enabled_switch=False,
    icon="agno.svg",
)
class TeamSettingsKnowledge(ServiceNode):

    settings: list = [
        'knowledge',
        'knowledge_filters',
        'enable_agentic_knowledge_filters',
        'add_references',
        'retriever',
        'references_format',
    ]

    knowledge: list | None = NodeVariableSettings(
        dock=True,
        info="Knowledge settings for the team, such as knowledge base, documents, or other relevant information.",
    )

    knowledge_filters: dict | None = NodeVariableSettings(
        dock=True,
        info="Path to a file containing knowledge information for the team.",
    )

    enable_agentic_knowledge_filters: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="If True, enables agentic knowledge filters for the team agent.",
    )

    add_references: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="If True, adds references to the knowledge in the team agent's responses.",
    )

    retriever: str | None = NodeVariableSettings(
        dock=True,
        info="Retriever settings for the team, such as retriever type or configuration.",
    )

    references_format: str = NodeVariableSettings(
        dock=dock_select_values(select_values={
            "json": "json",
            "yaml": "yaml",
        }),
        default="json",
        info="Format for references, such as 'json' or 'yaml'.",
    )

    instance: "TeamSettingsKnowledge" = NodeVariableSettings(
        label="Settings",
        group="knowledge",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.team_settings_knowledge.TeamSettingsKnowledge"
    )

    def provide_instance(self) -> "TeamSettingsKnowledge":
        return self
