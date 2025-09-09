from typing import Any, Union
from agno.knowledge import AgentKnowledge
from agno.knowledge.markdown import MarkdownKnowledgeBase
from agno.vectordb import VectorDb
from polysynergy_node_runner.setup_context.dock_property import dock_dict, dock_property
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

from polysynergy_nodes_agno.agno_agent.utils.find_connected_service import find_connected_service
from polysynergy_nodes_agno.agno_knowledge.utils.chunking_strategy import chunking_strategy, CHUNKING_SELECT_VALUES
from polysynergy_nodes_agno.agno_knowledge.utils.enrich_metadata import enrich_metadata
from polysynergy_nodes_agno.agno_knowledge.utils.download_url_items_to_tmp import download_url_items_to_tmp


@node(
    name="Markdown URL Knowledge Base",
    category="agno_knowledge",
    icon="file-text.svg",
    has_enabled_switch=False,
)
class MarkdownUrlKnowledge(ServiceNode):
    """
    Markdown (.md) URL-based knowledge base for Agno agents.
    """

    vector_db: VectorDb | None = NodeVariableSettings(
        label="Vector Database",
        has_in=True,
        info="Connected vector database service for storing and querying document vectors.",
    )

    urls: list[Union[str, dict[str, Any]]] = NodeVariableSettings(
        label="Markdown URLs",
        has_in=True,
        dock=dock_dict(
            key_label="URL",
            value_label="Metadata",
            info="List of Markdown URLs with optional metadata."
        ),
        default=[],
    )

    num_documents: int | None = NodeVariableSettings(label="Max Documents", dock=True)
    optimize_on: int | None = NodeVariableSettings(label="Optimize On", dock=True, default=1000)

    chunking_strategy: str | None = NodeVariableSettings(
        label="Chunking Strategy",
        dock=dock_property(select_values=CHUNKING_SELECT_VALUES),
        default="fixed",
        info="How to split documents into chunks for embedding.",
    )

    knowledge_base_instance: AgentKnowledge | None = NodeVariableSettings(
        label="Knowledge Base Instance", has_out=True
    )

    async def provide_instance(self) -> AgentKnowledge:
        vector_db = await find_connected_service(self, "vector_db", VectorDb)
        if not vector_db:
            raise ValueError("No vector database connected.")

        extensions = (".md",)

        url_items = enrich_metadata(self.urls or [], extensions=extensions)
        path_items = download_url_items_to_tmp(url_items, extensions=extensions)

        kwargs = {"path": path_items, "vector_db": vector_db}
        if self.num_documents is not None:
            kwargs["num_documents"] = self.num_documents
        if self.optimize_on is not None:
            kwargs["optimize_on"] = self.optimize_on

        if self.chunking_strategy:
            kwargs["chunking_strategy"] = chunking_strategy(self.chunking_strategy)

        kb = MarkdownKnowledgeBase(**kwargs)
        self.knowledge_base_instance = kb
        return kb