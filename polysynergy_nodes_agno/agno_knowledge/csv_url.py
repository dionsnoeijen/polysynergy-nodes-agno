from typing import Any, Union

from agno.knowledge import AgentKnowledge
from agno.knowledge.csv_url import CSVUrlKnowledgeBase   # ← zorg dat deze bestaat in jouw Agno
from agno.vectordb.base import VectorDb

from polysynergy_node_runner.setup_context.dock_property import dock_property, dock_dict
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

from polysynergy_nodes_agno.agno_agent.utils.find_connected_service import find_connected_service
from polysynergy_nodes_agno.agno_knowledge.utils.chunking_strategy import chunking_strategy, CHUNKING_SELECT_VALUES
from polysynergy_nodes_agno.agno_knowledge.utils.custom_is_valid_url import make_url_validator
from polysynergy_nodes_agno.agno_knowledge.utils.enrich_metadata import enrich_metadata


@node(
    name="CSV URL Knowledge",
    category="agno_knowledge",
    icon="brain.svg",
    has_enabled_switch=False,
)
class CSVUrlKnowledge(ServiceNode):
    """
    CSV URL-based knowledge base for Agno agents.
    Loads CSV documents from URLs with metadata for filtering.
    """

    # Vector Database Input
    vector_db: VectorDb | None = NodeVariableSettings(
        label="Vector Database",
        has_in=True,
        info="Connected vector database service for storing and querying document vectors.",
    )

    # CSV URLs (string, {url,metadata}, of dock {key,value})
    urls: list[Union[str, dict[str, Any]]] = NodeVariableSettings(
        label="CSV URLs",
        has_in=True,
        dock=dock_dict(
            key_label="URL",
            value_label="Metadata",
            info="List of CSV URLs with optional metadata for filtering."
        ),
        default=[],
        info="CSV URLs to load with optional metadata (e.g., source, dataset, region).",
    )

    # Optioneel: max docs / optimize
    num_documents: int | None = NodeVariableSettings(
        label="Max Documents",
        dock=True,
        info="Maximum number of documents to load (optional limit).",
    )

    optimize_on: int | None = NodeVariableSettings(
        label="Optimize On",
        dock=True,
        default=1000,
        info="Number of documents to optimize the vector database on.",
    )

    chunking_strategy: str | None = NodeVariableSettings(
        label="Chunking Strategy",
        dock=dock_property(select_values=CHUNKING_SELECT_VALUES),
        default="fixed",
        info="How to split documents into chunks for embedding.",
    )

    # Output
    knowledge_base_instance: AgentKnowledge | None = NodeVariableSettings(
        label="Knowledge Base Instance",
        has_out=True,
        info="CSV URL knowledge base instance for use in agents",
    )

    async def provide_instance(self) -> AgentKnowledge:
        # Vector DB
        vector_db = await find_connected_service(self, "vector_db", VectorDb)
        if not vector_db:
            raise ValueError("No vector database connected. Please connect a vector database service node.")

        formatted_urls = enrich_metadata(self.urls or [], extensions=".csv")

        kwargs = {
            "urls": formatted_urls,
            "vector_db": vector_db,
        }
        if self.num_documents is not None:
            kwargs["num_documents"] = self.num_documents
        if self.optimize_on is not None:
            kwargs["optimize_on"] = self.optimize_on

        if self.chunking_strategy:
            kwargs["chunking_strategy"] = chunking_strategy(self.chunking_strategy)
        try:
            self.knowledge_base_instance = CSVUrlKnowledgeBase(**kwargs)
            self.knowledge_base_instance._is_valid_url = make_url_validator([".csv"])
            return self.knowledge_base_instance
        except Exception:
            import traceback; traceback.print_exc()
            raise