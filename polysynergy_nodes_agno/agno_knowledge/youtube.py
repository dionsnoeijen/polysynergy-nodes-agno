from typing import Any, Union
from agno.knowledge import AgentKnowledge
from agno.knowledge.youtube import YouTubeKnowledgeBase, YouTubeReader
from agno.vectordb import VectorDb
from polysynergy_node_runner.setup_context.dock_property import dock_dict, dock_property
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

from polysynergy_nodes_agno.agno_agent.utils.find_connected_service import find_connected_service
from polysynergy_nodes_agno.agno_knowledge.utils.chunking_strategy import chunking_strategy, CHUNKING_SELECT_VALUES


@node(
    name="YouTube URL Knowledge Base",
    category="agno_knowledge",
    icon="youtube.svg",
    has_enabled_switch=False,
)
class YouTubeUrlKnowledge(ServiceNode):
    """
    YouTube-based knowledge base for Agno agents.
    Fetches video transcripts from YouTube URLs and stores them in a vector DB.
    """

    vector_db: VectorDb | None = NodeVariableSettings(
        label="Vector Database",
        has_in=True,
        info="Connected vector database service for storing and querying document vectors.",
    )

    urls: list[Union[str, dict[str, Any]]] = NodeVariableSettings(
        label="YouTube URLs",
        has_in=True,
        dock=dock_dict(
            key_label="URL",
            value_label="(optional) ignored",
            info="List of YouTube video URLs. Metadata is ignored by the KB."
        ),
        default=[],
        info="YouTube video URLs to ingest (transcripts).",
    )

    # YouTubeReader opties (optioneel)
    chunk_transcript: bool | None = NodeVariableSettings(
        label="Chunk Transcript",
        dock=dock_property(select_values={"true": True, "false": False}),
        default=True,
        info="Chunk the transcript into smaller pieces for better retrieval.",
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
        label="Knowledge Base Instance",
        has_out=True,
        info="YouTube knowledge base instance for use in agents",
    )

    async def provide_instance(self) -> AgentKnowledge:
        vector_db = await find_connected_service(self, "vector_db", VectorDb)
        if not vector_db:
            raise ValueError("No vector database connected.")

        url_list: list[str] = []
        for item in self.urls or []:
            if isinstance(item, str):
                url_list.append(item)
            elif isinstance(item, dict) and "url" in item:
                url_list.append(str(item["url"]))

        reader = YouTubeReader(chunk=bool(self.chunk_transcript)) if self.chunk_transcript is not None else None

        kwargs: dict[str, Any] = {
            "urls": url_list,
            "vector_db": vector_db,
        }
        if reader is not None:
            kwargs["reader"] = reader
        if self.num_documents is not None:
            kwargs["num_documents"] = self.num_documents
        if self.optimize_on is not None:
            kwargs["optimize_on"] = self.optimize_on

        if self.chunking_strategy:
            kwargs["chunking_strategy"] = chunking_strategy(self.chunking_strategy)

        kb = YouTubeKnowledgeBase(**kwargs)
        self.knowledge_base_instance = kb
        return kb