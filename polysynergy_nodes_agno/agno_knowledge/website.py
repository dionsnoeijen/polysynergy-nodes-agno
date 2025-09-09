from typing import Any, Union
from agno.knowledge import AgentKnowledge
from agno.knowledge.website import WebsiteKnowledgeBase
from agno.vectordb import VectorDb
from polysynergy_node_runner.setup_context.dock_property import dock_dict, dock_property
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

from polysynergy_nodes_agno.agno_agent.utils.find_connected_service import find_connected_service
from polysynergy_nodes_agno.agno_knowledge.utils.chunking_strategy import chunking_strategy, CHUNKING_SELECT_VALUES


@node(
    name="Website Knowledge Base",
    category="agno_knowledge",
    icon="globe.svg",
    has_enabled_switch=False,
)
class WebsiteKnowledge(ServiceNode):
    """
    Website-based knowledge base for Agno agents.
    Reads one or more seed URLs, crawls pages, and stores content in a vector DB.
    """

    vector_db: VectorDb | None = NodeVariableSettings(
        label="Vector Database",
        has_in=True,
        info="Connected vector database service for storing and querying document vectors.",
    )

    urls: list[Union[str, dict[str, Any]]] = NodeVariableSettings(
        label="Seed URLs",
        has_in=True,
        dock=dock_dict(
            key_label="URL",
            value_label="Metadata (ignored here)",
            info="List of website URLs to crawl. Metadata is optional and not directly used."
        ),
        default=[],
        info="Seed URLs for crawling. Pages are parsed into text with BeautifulSoup.",
    )

    max_links: int | None = NodeVariableSettings(
        label="Max Links",
        dock=True,
        default=10,
        info="Number of links to follow from seed URLs.",
    )

    max_depth: int | None = NodeVariableSettings(
        label="Max Depth",
        dock=True,
        default=3,
        info="Maximum crawl depth starting from seed URLs.",
    )

    num_documents: int | None = NodeVariableSettings(
        label="Max Documents",
        dock=True,
        info="Maximum number of documents to return on search.",
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

    knowledge_base_instance: AgentKnowledge | None = NodeVariableSettings(
        label="Knowledge Base Instance", has_out=True
    )

    async def provide_instance(self) -> AgentKnowledge:
        vector_db = await find_connected_service(self, "vector_db", VectorDb)
        if not vector_db:
            raise ValueError("No vector database connected.")

        # flatten url-items: we gebruiken alleen de url zelf
        url_list = []
        for item in self.urls or []:
            if isinstance(item, str):
                url_list.append(item)
            elif isinstance(item, dict) and "url" in item:
                url_list.append(item["url"])

        kwargs = {
            "urls": url_list,
            "vector_db": vector_db,
        }
        if self.max_links is not None:
            kwargs["max_links"] = self.max_links
        if self.max_depth is not None:
            kwargs["max_depth"] = self.max_depth
        if self.num_documents is not None:
            kwargs["num_documents"] = self.num_documents
        if self.optimize_on is not None:
            kwargs["optimize_on"] = self.optimize_on

        if self.chunking_strategy:
            kwargs["chunking_strategy"] = chunking_strategy(self.chunking_strategy)

        kb = WebsiteKnowledgeBase(**kwargs)
        self.knowledge_base_instance = kb
        return kb