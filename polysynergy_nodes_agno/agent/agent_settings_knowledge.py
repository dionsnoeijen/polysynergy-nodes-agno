from __future__ import annotations
from typing import Callable

from agno.knowledge import AgentKnowledge
from polysynergy_node_runner.setup_context.dock_property import dock_property
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Agent Knowledge Settings",
    category="agno",
    has_enabled_switch=False,
    icon="agno.svg",
)
class AgentSettingsKnowledge(ServiceNode):

    # Settings that can be used by the agent on runtime.
    settings: list = [
        'knowledge',
        'knowledge_filters',
        'enable_agentic_knowledge_filters',
        'add_references',
        'retriever',
        'references_format',
    ]

    knowledge: AgentKnowledge | None = NodeVariableSettings(
        dock=True,
        has_in=True,
        info="Knowledge base for retrieval-augmented generation (RAG)."
    )

    knowledge_filters: dict | None = NodeVariableSettings(
        dock=True,
        info="Default filters for knowledge retrieval (e.g. tags or document types).",
    )

    enable_agentic_knowledge_filters: bool = NodeVariableSettings(
        dock=True,
        info="If True, the agent can decide which knowledge filters to apply.",
    )

    add_references: bool = NodeVariableSettings(
        dock=True,
        info="If True, adds references from the knowledge base to the agent output.",
    )

    retriever: Callable[..., list[dict | str]] | None = NodeVariableSettings(
        dock=True,
        info="Custom retrieval function for knowledge search. Overrides the default search_knowledge method.",
    )

    references_format: str = NodeVariableSettings(
        dock=dock_property(select_values={"json": "json", "yaml": "yaml"}),
        info="Format used when rendering references in the agent output (json or yaml).",
    )

    instance: "AgentSettingsKnowledge" = NodeVariableSettings(
        label="Settings",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.agent_settings_knowledge.AgentSettingsKnowledge"
    )

    def provide_instance(self) -> "AgentSettingsKnowledge":
        return self
