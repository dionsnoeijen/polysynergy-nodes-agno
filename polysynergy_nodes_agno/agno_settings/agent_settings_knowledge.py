from __future__ import annotations
from typing import Callable

from agno.knowledge import Knowledge
from agno.vectordb import VectorDb

from polysynergy_node_runner.setup_context.dock_property import dock_property
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode
from polysynergy_nodes_agno.agno_agent.utils.find_connected_service import find_connected_service

@node(
    name="Agent Knowledge Settings",
    category="agno_settings",
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
        'search_knowledge',
        'update_knowledge',
    ]

    vector_db: VectorDb | None = NodeVariableSettings(
        label="Vector Database",
        has_in=True,
        info="Connected vector database service for storing and querying document vectors.",
        type="agno.vectordb.base.VectorDb",
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

    max_results: int | None = NodeVariableSettings(
        label="Max Results",
        dock=True,
        default=10,
        info="Maximum number of results to retrieve from knowledge base on each search (default: 10).",
    )

    retriever: Callable[..., list[dict | str]] | None = NodeVariableSettings(
        dock=True,
        info="Custom retrieval function for knowledge search. Overrides the default search_knowledge method.",
    )

    references_format: str = NodeVariableSettings(
        dock=dock_property(select_values={"json": "json", "yaml": "yaml"}),
        default="json",
        info="Format used when rendering references in the agent output (json or yaml).",
    )

    search_knowledge: bool = NodeVariableSettings(
        dock=True,
        default=True,
        info="Adds a tool that allows the model to search the knowledge base. Only enabled if knowledge is provided.",
    )

    update_knowledge: bool = NodeVariableSettings(
        dock=True,
        info="Adds a tool that allows the model to update the knowledge base.",
    )


    instance: "AgentSettingsKnowledge" = NodeVariableSettings(
        label="Settings",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.agent_settings_knowledge.AgentSettingsKnowledge"
    )

    knowledge: Knowledge | None = None

    async def provide_instance(self) -> "AgentSettingsKnowledge":
        try:
            connected_vector_db = await find_connected_service(self, "vector_db", VectorDb)
            print(f"[AgentSettingsKnowledge] Got knowledge base: {type(connected_vector_db).__name__ if connected_vector_db else 'None'}")
            if connected_vector_db:
                self.knowledge = Knowledge(
                    vector_db=connected_vector_db,
                    max_results=self.max_results
                )
                print(f"[AgentSettingsKnowledge] Created Knowledge with max_results={self.max_results}")
            return self
        except Exception as e:
            print(f"[AgentSettingsKnowledge] ERROR: {e}")
            raise
