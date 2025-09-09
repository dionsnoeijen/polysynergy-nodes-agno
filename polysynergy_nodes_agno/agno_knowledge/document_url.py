# nodes/document_url_node.py
from typing import Any, Union, Sequence
from agno.knowledge import AgentKnowledge
from agno.knowledge.document import DocumentKnowledgeBase
from agno.vectordb import VectorDb
from polysynergy_node_runner.setup_context.dock_property import dock_dict, dock_property
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

from polysynergy_nodes_agno.agno_agent.utils.find_connected_service import find_connected_service
from polysynergy_nodes_agno.agno_knowledge.utils.chunking_strategy import CHUNKING_SELECT_VALUES, chunking_strategy
from polysynergy_nodes_agno.agno_knowledge.utils.enrich_metadata import enrich_metadata
from polysynergy_nodes_agno.agno_knowledge.utils.download_url_items_to_tmp import download_url_items_to_tmp
from polysynergy_nodes_agno.agno_knowledge.utils.files_to_documents import files_to_documents

@node(
    name="Document URL Knowledge Base",
    category="agno_knowledge",
    icon="brain.svg",
    has_enabled_switch=False,
)
class DocumentUrlKnowledge(ServiceNode):
    vector_db: VectorDb | None = NodeVariableSettings(
        label="Vector Database",
        has_in=True,
        info="Connected vector database service for storing and querying document vectors.",
    )

    urls: list[Union[str, dict[str, Any]]] = NodeVariableSettings(
        label="Document URLs",
        has_in=True,
        dock=dock_dict(
            key_label="URL",
            value_label="Metadata",
            info="List of mixed document URLs (pdf, docx, txt, rtf, pptx, xlsx, ...) with optional metadata."
        ),
        default=[],
        info="Mixed document URLs with optional metadata.",
    )

    allowed_extensions: list[str] | None = NodeVariableSettings(
        label="Allowed Extensions",
        dock=True,
        default=[".pdf", ".docx", ".doc", ".rtf", ".txt", ".pptx", ".xlsx", ".csv"],
        info="Extensions to accept from URLs.",
    )

    num_documents: int | None = NodeVariableSettings(label="Max Documents", dock=True)
    optimize_on: int | None = NodeVariableSettings(label="Optimize On", dock=True, default=1000)

    chunking_strategy: str | None = NodeVariableSettings(
        label="Chunking Strategy",
        dock=dock_property(select_values=CHUNKING_SELECT_VALUES),
        default="fixed",
        info="""
        How to split documents into chunks for embedding.

        - FixedSizeChunking → simple, fixed-length blocks. Fast and predictable, but may cut mid-sentence.
        - RecursiveChunking → splits at natural boundaries (headings, paragraphs, sentences). More coherent and readable.
        - AgenticChunking → an LLM decides how to chunk. Flexible but slower and more expensive.
        - SemanticChunking → uses embeddings (chonkie) to split where meaning shifts. Often best for retrieval quality.
        - DocumentChunking → preserves document structure (headings, sections, metadata). Useful for hierarchical documents.

        Choose based on trade-offs between speed, cost, and embedding quality.
        """
    )

    knowledge_base_instance: AgentKnowledge | None = NodeVariableSettings(
        label="Knowledge Base Instance", has_out=True
    )

    async def provide_instance(self) -> AgentKnowledge:
        vector_db = await find_connected_service(self, "vector_db", VectorDb)
        if not vector_db:
            raise ValueError("No vector database connected.")

        exts: Sequence[str] = self.allowed_extensions or [".pdf", ".docx"]

        url_items = enrich_metadata(self.urls or [], extensions=exts)
        path_items = download_url_items_to_tmp(url_items, extensions=exts)
        documents = files_to_documents(path_items)

        # 4) Bouw DocumentKnowledgeBase met Document-objects
        kwargs = {"documents": documents, "vector_db": vector_db}
        if self.num_documents is not None:
            kwargs["num_documents"] = self.num_documents
        if self.optimize_on is not None:
            kwargs["optimize_on"] = self.optimize_on

        if self.chunking_strategy:
            kwargs["chunking_strategy"] = chunking_strategy(self.chunking_strategy)

        kb = DocumentKnowledgeBase(**kwargs)
        self.knowledge_base_instance = kb
        return kb